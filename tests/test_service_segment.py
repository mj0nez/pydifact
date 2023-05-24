from __future__ import annotations
from pydifact.service_segments import UNB


from pydifact.segments import (
    Segment as Segment_pydifact,
    SegmentFactory,
    SegmentInterface,
)


def test_service_segment():
    assert isinstance(UNB(["a", "b"]), UNB)


samples = [
    "UNH+1+UTILMD:D:11A:UN:5.2e+UNB_DE0020_nr_1+1:C'",
    "UNH+2+UTILMD:D:11A:UN:X.Yz+UNB_DE0020_nr_1+2’",
    "UNH+3+UTILMD:D:11A:UN:X.Yz+UNB_DE0020_nr_1+3:F",
]


from pydifact.api import Leaf, Composite


def test_leaf_creation():
    de062 = Leaf("DE0062", "Hello World")


def test_composite_creation():
    c006 = Composite("C006")


def test_leaf_parsing():
    de062 = Leaf("DE0062", "Hello World")
    de062.parse("65")


def test_composite_parse():
    de062 = Leaf("DE0062", "Hello World")
    de063 = Leaf("DE0063", "Hallo Welt")

    c006 = Composite("C006")
    c006.add(de062)
    c006.add(de063)
    c006.parse(["5", "6"])


def test_leaf_serialization():
    de062 = Leaf("DE0062", "Hello World")
    de062.parse("65")

    assert de062.serialize() == "65"


def test_composite_serialization():
    de062 = Leaf("DE0062", "Hello World")
    de062.parse("65")
    de062 = Leaf("DE0062", "Hello World")
    de063 = Leaf("DE0063", "Hallo Welt")

    c006 = Composite("C006")
    c006.add(de062)
    c006.add(de063)
    c006.parse(["5", "6"])

    assert c006.serialize() == ["5", "6"]


def test_leaf_dict():
    de062 = Leaf("DE0062", "Hello World")
    de062.parse("65")

    assert de062.to_dict() == {
        "description": "DE0062",
        "name": "Hello World",
        "content": "65",
    }


def test_composite_dict():
    de062 = Leaf("DE0062", "Hello World")
    de062 = Leaf("DE0062", "Hello World")
    de063 = Leaf("DE0063", "Hallo Welt")

    c006 = Composite("C006", "Hi du")
    c006.add(de062)
    c006.add(de063)
    c006.parse(["5", "6"])

    assert c006.to_dict() == {
        "description": "C006",
        "name": "Hi du",
        "content": [
            {"description": "DE0062", "name": "Hello World", "content": "5"},
            {"description": "DE0063", "name": "Hallo Welt", "content": "6"},
        ],
    }


class DataElement(Leaf):
    pass


class ElementGroup(Composite):
    pass


class Segment(Composite):
    def from_segment(self, segment: SegmentInterface):
        if self.description != segment.tag:
            raise ValueError("Incorrect tag ....")

        self.parse(segment.elements)

    def to_segment(self) -> SegmentInterface:
        return SegmentFactory.create_segment(self.description, *self.serialize())


class SegmentGroup(Composite):
    pass


def test_segment_creation():
    unt = Segment("UNT", "Nachrichten-Endesegment")

    unt.add(DataElement("DE0074", "Anzahl der Segmente in einer Nachricht"))
    unt.add(DataElement("DE0062", "Nachrichten-Referenznummer"))

    unt.parse(["6", "hji78"])

    unt.serialize()


def test_segment_creation():
    unt = Segment("UNT", "Nachrichten-Endesegment")

    unt.add(DataElement("DE0074", "Anzahl der Segmente in einer Nachricht"))
    unt.add(DataElement("DE0062", "Nachrichten-Referenznummer"))

    unt.from_segment(Segment_pydifact("UNT", "6", "hji78"))

    print(unt)


def test_nested_composite():
    unt = Segment("UNT", "Nachrichten-Endesegment")

    unt.add(DataElement("DE0074", "Anzahl der Segmente in einer Nachricht"))

    c006 = ElementGroup("C006", "Hi du")
    c006.add(DataElement("DE0076", "Anzahl der Segmente in einer Nachricht_2"))
    c006.add(DataElement("DE0066", "Nachrichten-Referenznummer_2"))

    unt.add(c006)


def test_segment_group():
    segment_group = SegmentGroup("SG6")
    for i in range(3):
        unt = Segment("UNT", f"Nachrichten-Endesegment_{i}")

        unt.add(DataElement("DE0074", "Anzahl der Segmente in einer Nachricht"))
        unt.add(DataElement("DE0062", "Nachrichten-Referenznummer"))

        segment_group.add(unt)

    print(segment_group)


# TODO  find a way to loosen the repetition of data elements in an group
#       e.g. when parsing a FTX segment we don't know the number of repeated
#       elements before parsing...
#       itertools.zip_longest could be sufficient....
#       
#       https://docs.python.org/3/library/itertools.html#itertools.zip_longest