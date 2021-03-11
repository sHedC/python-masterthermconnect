"""Test Configuration for various tests."""
import json
import os

VALID_LOGIN = {"uname": "user name", "upwd": "hashpass", "token": "9jdhhs78dodlosd"}

GENERAL_ERROR_RESPONSE = "User not logged in"


def load_fixture(filename):
    """Load a JSON fixture for testing."""
    try:
        path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
        with open(path, encoding="utf-8") as fptr:
            return fptr.read()
    except Exception:
        return None


class ConnectionMock:
    """Mock the Connection Class to return what we want."""

    def __init__(self):
        """Initialize the Connection Mock."""

    def connect(self, role="400"):
        """Mock Connect, Return Connect Success/ Failures."""
        result = json.loads(load_fixture("login_success.json"))
        result["role"] = role

        return result

    def getDeviceInfo(self, module_id, device_id):
        """Return the Device Information from fixtures."""
        info = json.loads(load_fixture(f"pumpinfo_{module_id}_{device_id}.json"))
        if info is None:
            info = json.loads(load_fixture("pumpinfo_invalid.json"))

        return info

    def getDeviceData(self, module_id, device_id, last_update_time="0"):
        """Return Device Data from fixtures."""
        data = json.loads(
            load_fixture(f"pumpdata_{module_id}_{device_id}_{last_update_time}.json")
        )
        if data is None:
            data = json.loads(load_fixture("pumpdata_unavailable.json"))

        return data
