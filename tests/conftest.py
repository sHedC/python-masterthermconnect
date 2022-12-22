"""Test Configuration for various tests."""
import json
import os

VALID_LOGIN = {
    "uname": "user name@email",
    "upwd": "hash%pass or",
    "token": "9jdhhs78dodlosd",
}

GENERAL_ERROR_RESPONSE = "User not logged in"


def load_fixture(filename):
    """Load a JSON fixture for testing."""
    try:
        path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
        with open(path, encoding="utf-8") as fptr:
            return fptr.read()
    except OSError:
        return None


class ConnectionMock:
    """Mock the Connection Class to return what we want."""

    def __init__(self, api_version: str = "v1", use_mt: bool = False):
        """Initialize the Connection Mock."""
        self.__api_version = api_version

        if api_version == "v1":
            if use_mt:
                self.__subfolder = "mt/"
            else:
                self.__subfolder = ""
        else:
            self.__subfolder = "newapi/"

    def connect(self, role="400"):
        """Mock Connect, Return Connect Success/ Failures."""
        if self.__api_version == "v1":
            result = json.loads(load_fixture(f"{self.__subfolder}login_success.json"))
        else:
            result = json.loads(load_fixture(f"{self.__subfolder}modules.json"))

        result["role"] = role

        return result

    def get_device_info(self, module_id, device_id):
        """Return the Device Information from fixtures."""
        info = json.loads(
            load_fixture(f"{self.__subfolder}pumpinfo_{module_id}_{device_id}.json")
        )

        return info

    def get_device_data(self, module_id, device_id, last_update_time=None):
        """Return Device Data from fixtures, fixed for Controller Test"""
        if last_update_time is None:
            last_update_time = "0"

        data = json.loads(
            load_fixture(
                f"{self.__subfolder}pumpdata_{module_id}_{device_id}_{last_update_time}.json"
            )
        )
        if "varfile_mt1_config1" in data["data"]:
            var_data = "varfile_mt1_config1"
        elif "varfile_mt1_config2" in data["data"]:
            var_data = "varfile_mt1_config2"
        else:
            var_data = "varFileData"

        data["data"]["varData"] = data["data"][var_data]
        del data["data"][var_data]

        return data
