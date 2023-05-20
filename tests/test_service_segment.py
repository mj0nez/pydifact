from pydifact.service_segments import UNB, UNH
from pydifact.parser import Parser


def test_service_segment():
    assert isinstance(UNB(["a", "b"]), UNB)


samples = [
    "UNH+1+UTILMD:D:11A:UN:5.2e+UNB_DE0020_nr_1+1:C'",
    "UNH+2+UTILMD:D:11A:UN:X.Yz+UNB_DE0020_nr_1+2’",
    "UNH+3+UTILMD:D:11A:UN:X.Yz+UNB_DE0020_nr_1+3:F",
]


def test_UNH():
    pass
