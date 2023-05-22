from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterator, Optional, Union

from enum import Enum


class PluginMount(type):
    """Generic plugin mount point (= entry point) for pydifact plugins.

    .. note::
        Plugins that have an **__omitted__** attriute are not added to the list!
    """

    # thanks to Marty Alchin!

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, "plugins"):
            cls.plugins = []
        else:
            if not getattr(cls, "__omitted__", False):
                cls.plugins.append(cls)


class EDISyntaxError(SyntaxError):
    """A Syntax error within the parsed EDIFACT file was found."""


class Component(ABC):
    """
    The base Component class declares common operations for both simple and
    complex objects of a composition.
    """

    description: str

    @property
    def parent(self) -> Component:
        return self._parent

    @parent.setter
    def parent(self, parent: Component):
        """
        Optionally, the base Component can declare an interface for setting and
        accessing a parent of the component in a tree structure. It can also
        provide some default implementation for these methods.
        """

        self._parent = parent

    """
    In some cases, it would be beneficial to define the child-management
    operations right in the base Component class. This way, you won't need to
    expose any concrete component classes to the client code, even during the
    object tree assembly. The downside is that these methods will be empty for
    the leaf-level components.
    """

    def add(self, component: Component) -> None:
        pass

    def remove(self, component: Component) -> None:
        pass

    def is_composite(self) -> bool:
        """
        You can provide a method that lets the client code figure out whether a
        component can bear children.
        """

        return False

    def get_component(self, description: Optional[str] = None) -> Iterator[Component]:
        # argument description is implemented to provide a unified interface
        # a leaf yields itself, while a composite yields all matching children
        # and ONLY children!
        yield self

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @abstractmethod
    def serialize(self) -> Union[str, list[str]]:
        """
        The base Component may implement some default behavior or leave it to
        concrete classes (by declaring the method containing the behavior as
        "abstract").
        """

        pass

    @abstractmethod
    def parse(self, content: Union[str, list[str]]) -> None:
        pass


class Field(str, Enum):
    description = "description"
    name = "name"
    content = "content"


class Leaf(Component):
    """
    The Leaf class represents the end objects of a composition. A leaf can't
    have any children.

    Usually, it's the Leaf objects that do the actual work, whereas Composite
    objects only delegate to their sub-components.
    """

    def __init__(self, description: str, name: Optional[str] = "") -> None:
        self.description = description
        self.name = name
        self._content = ""  # we need an empty string at least

    def to_dict(self) -> dict:
        return {
            Field.description: self.description,
            Field.name: self.name,
            Field.content: self.serialize(),
        }

    def serialize(self) -> str:
        return self._content

    def parse(self, content: str) -> None:
        self._content = content


class Composite(Component):
    """
    The Composite class represents the complex components that may have
    children. Usually, the Composite objects delegate the actual work to their
    children and then "sum-up" the result.
    """

    def __init__(self, description: str, name: Optional[str] = "") -> None:
        self.description = description
        self.name = name
        self._children: list[Component] = []

    """
    A composite object can add or remove other components (both simple or
    complex) to or from its child list.
    """

    def add(self, component: Component) -> None:
        self._children.append(component)
        component.parent = self

    def remove(self, component: Component) -> None:
        self._children.remove(component)
        component.parent = None

    def get_component(self, description: Optional[str] = None) -> Iterator[Component]:
        # here we need to fetch all children, whose description match
        for child in self._children:
            if child.description == description:
                yield child

    def is_composite(self) -> bool:
        return True

    def to_dict(self) -> dict:
        # data elements may be repeated,
        # therefore we have to account for e.g. DE4400 in C108 of a FTX segment
        return {
            Field.description: self.description,
            Field.name: self.name,
            Field.content: [child.to_dict() for child in self._children],
        }

    def serialize(self) -> list[str]:
        """
        The Composite executes its primary logic in a particular way. It
        traverses recursively through all its children, collecting and summing
        their results. Since the composite's children pass these calls to their
        children and so forth, the whole object tree is traversed as a result.
        """

        return [child.serialize() for child in self._children]

    def parse(self, content: list[str]) -> None:
        if len(content) != len(self._children):
            raise ValueError("Length of children does not match the given elements.")

        for child, child_content in zip(self._children, content):
            child.parse(child_content)
