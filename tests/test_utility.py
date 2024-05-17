import sys
import os

if not os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) in sys.path:
    # Add the project root directory to the sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from Libs.Utility import digest_str_duration


def test_digest_str_duration():
    assert digest_str_duration("1h") == 3600
    assert digest_str_duration("1d") == 86400
    assert digest_str_duration("24m") == 1440
    assert digest_str_duration("60s") == 60
    assert digest_str_duration("0") == 0
    assert digest_str_duration("5") == 0
    assert digest_str_duration("1w") == 0
