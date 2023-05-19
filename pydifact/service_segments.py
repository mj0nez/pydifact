from pydifact.api import EDISyntaxError
from pydifact.segments import Segment, SegmentFactory

from typing import Union, List


class FromElementsInterface:
    tag: str

    @classmethod
    def from_elements(cls, *elements: Union[str, List[str], None]):
        return cls(cls.tag, *elements)


class UNB(Segment, FromElementsInterface):
    __omitted__ = False

    tag = "UNB"

    def validate(self) -> bool:
        super().validate()

        if len(self.timestamp) not in (6, 8):
            raise EDISyntaxError("Timestamp of file-creation malformed.")

        if len(self.elements) < 4:
            raise EDISyntaxError("Missing elements in UNB header")

        return True

    @property
    def timestamp(self) -> str:
        return self.elements[3][0]

    @property
    def datetime_format(self):
        # In syntax version 3 the year is formatted using two digits, while in version 4 four digits are used.
        # Since some EDIFACT files in the wild don't adhere to this specification, we just use whatever format seems
        # more appropriate according to the length of the date string.

        if len(self.timestamp) == 6:
            datetime_fmt = "%y%m%d-%H%M"
        elif len(self.timestamp) == 8:
            datetime_fmt = "%Y%m%d-%H%M"

        return datetime_fmt


class UNZ(Segment, FromElementsInterface):
    __omitted__ = False

    tag = "UNZ"

    @property
    def control_count(self) -> str:
        return self[0]

    @property
    def control_reference(self) -> str:
        return self[1]


class UNH(Segment, FromElementsInterface):
    __omitted__ = False

    tag = "UNH"

    @property
    def message_reference_number(self) -> str:
        return self[0]

    @property
    def message_type(self) -> str:
        return self[1][0]

    @property
    def message_version_number(self) -> str:
        return self[1][1]

    @property
    def message_release_number(self) -> str:
        return self[1][2]

    @property
    def controlling_agency(self) -> str:
        return self[1][3]

    @property
    def association_assigned_code(self) -> str:
        return self[1][4]

    @property
    def common_access_reference(self) -> str:
        return self[2][0]

    @property
    def sequence_of_transfer(self) -> str:
        return self[3][0]

    @property
    def first_and_last_transfer(self) -> str:
        return self[3][1]


class UNT(Segment, FromElementsInterface):
    __omitted__ = False

    tag = "UNT"
