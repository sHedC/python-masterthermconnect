"""Test the API Client."""
import json

from datetime import datetime, timedelta
from hashlib import sha1
from unittest.mock import patch

from aiohttp import web, ServerTimeoutError
from aiohttp.test_utils import AioHTTPTestCase, Request

import pytest

from masterthermconnect import (
    MasterthermAuthenticationError,
    MasterthermConnectionError,
    MasterthermTokenInvalid,
    MasterthermPumpError,
    MasterthermUnsupportedVersion,
    MasterthermResponseFormatError,
)
from masterthermconnect.api import MasterthermAPI
from masterthermconnect.const import (
    DATE_FORMAT,
    URL_LOGIN,
    URL_PUMPDATA,
    URL_PUMPINFO,
    URL_POSTUPDATE,
)

from .conftest import GENERAL_ERROR_RESPONSE, VALID_LOGIN, load_fixture


@patch("masterthermconnect.api.URL_BASE", "")
class APITestCase(AioHTTPTestCase):
    """Test the Original API Connection."""

    error_type = ""
    data: dict = None
    info: dict = None

    async def get_application(self):  # noqa: C901
        """Start and Return a mock application."""

        async def _connect_response(request: Request):
            """Check the Test Login Credentials and return login connect or failure."""
            data = await request.post()
            password = sha1(VALID_LOGIN["upwd"].encode("utf-8")).hexdigest()

            if self.error_type == "ClientConnectionError":
                return None

            if data["uname"] == VALID_LOGIN["uname"] and data["upwd"] == password:
                response_text = load_fixture("login_success.json")
            else:
                response_text = load_fixture("login_invalid.json")

            if self.error_type == "token_expire":
                token_expires = datetime.now() + timedelta(seconds=0)
            else:
                token_expires = datetime.now() + timedelta(seconds=60)

            response = web.Response(
                text=response_text,
                content_type="application/json",
            )
            response.set_cookie(
                "PHPSESSID",
                VALID_LOGIN["token"],
                expires=token_expires.strftime(DATE_FORMAT) + "GMT",
            )

            return response

        async def _get_info(request: Request):
            """Get the Pump Info."""
            data = await request.post()
            content_type = "application/json"

            if self.error_type == "ClientConnectionError":
                return None

            if self.error_type.startswith("login"):
                response_text = GENERAL_ERROR_RESPONSE
                content_type = "text/plain"
                if self.error_type == "login_once":
                    self.error_type = ""
            elif self.error_type.startswith("timeout"):
                if self.error_type == "timeout_once":
                    self.error_type = ""
                    raise ServerTimeoutError("Connection timeout.")
            elif self.info is None:
                module_id = data["moduleid"]
                unit_id = data["unitid"]
                response_text = load_fixture(f"pumpinfo_{module_id}_{unit_id}.json")
                if response_text is not None:
                    self.info = json.loads(response_text)
            else:
                response_text = json.dumps(self.info)

            if response_text is None:
                response_text = load_fixture("pumpinfo_invalid.json")

            response = web.Response(text=response_text, content_type=content_type)
            return response

        async def _get_data(request: Request):
            """Get the Pump Data."""
            data = await request.post()
            content_type = "application/json"
            module_id = data["moduleId"]
            unit_id = data["deviceId"]
            last_update_time = data["lastUpdateTime"]

            if self.error_type == "ClientConnectionError":
                return None

            if self.error_type == "content_error":
                response_text = "content error"
                content_type = "text/plain"
            elif self.error_type == "json_error":
                response_text = "json error"
            elif self.error_type.startswith("login"):
                response_text = GENERAL_ERROR_RESPONSE
                content_type = "text/plain"
                if self.error_type == "login_once":
                    self.error_type = ""
            elif self.error_type.startswith("timeout"):
                if self.error_type == "timeout_once":
                    self.error_type = ""
                    raise ServerTimeoutError("Connection timeout.")
            elif self.error_type == "unavailable":
                response_text = load_fixture("pumpdata_unavailable.json")
            elif self.data is None or last_update_time != "0":
                response_text = load_fixture(
                    f"pumpdata_{module_id}_{unit_id}_{last_update_time}.json"
                )
            else:
                response_text = json.dumps(self.data)

            if response_text is None:
                response_text = load_fixture("pumpdata_invalid.json")
            elif content_type == "application/json" and self.error_type != "json_error":
                self.data = json.loads(response_text)

            response = web.Response(text=response_text, content_type=content_type)
            return response

        async def _set_data(request: Request):
            """Set the Pump Data."""
            data = await request.post()
            content_type = "application/json"
            # module_id = data["moduleId"]
            unit_id = str(data["deviceId"]).zfill(3)
            variable_id = data["variableId"]
            variable_value = data["variableValue"]

            if self.error_type.startswith("login"):
                response_text = GENERAL_ERROR_RESPONSE
                content_type = "text/plain"
                if self.error_type == "login_once":
                    self.error_type = ""
            elif self.error_type.startswith("timeout"):
                if self.error_type == "timeout_once":
                    self.error_type = ""
                    raise ServerTimeoutError("Connection timeout.")
            elif self.error_type == "write_error":
                response_text = load_fixture("pumpwrite_error.json")
                self.error_type = ""
            else:
                response_text = load_fixture("pumpwrite_success.json")
                if "varfile_mt1_config1" in self.data["data"]:
                    self.data["data"]["varfile_mt1_config1"][unit_id][
                        variable_id
                    ] = variable_value
                else:
                    self.data["data"]["varfile_mt1_config2"][unit_id][
                        variable_id
                    ] = variable_value

            response = web.Response(text=response_text, content_type=content_type)
            return response

        app = web.Application()
        app.router.add_post(URL_LOGIN, _connect_response)
        app.router.add_post(URL_PUMPINFO, _get_info)
        app.router.add_post(URL_PUMPDATA, _get_data)
        app.router.add_post(URL_POSTUPDATE, _set_data)
        return app

    async def test_setup(self):
        """Test the API Setup."""
        assert MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )

    async def test_connect(self):
        """Test the API Logs in and Returns modules."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        result = await api.connect()

        assert result != {}
        assert result["returncode"] == 0
        assert result["modules"][0]["id"] == "1234"
        assert result["role"] == "400"

    async def test_autherror(self):
        """Test a Connection Authentication Error."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"],
            VALID_LOGIN["upwd"] + "bad",
            self.client,
            api_version="v1",
        )

        with pytest.raises(MasterthermAuthenticationError):
            await api.connect()

    async def test_connect_unavailabe(self):
        """Test the Connection unavailable or invalid."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )

        with patch("masterthermconnect.api.URL_LOGIN", "/"), pytest.raises(
            MasterthermConnectionError
        ):
            await api.connect()

    async def test_getinfo(self):
        """Test returning the Device Information."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect() != {}

        info = await api.get_device_info("1234", "1")

        assert info != {}
        assert info["moduleid"] == "1234"
        assert info["type"] == "AQI"

    async def test_getinfo_tokeninvalid(self):
        """Test the get device info token is not valid."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect() is not {}

        self.error_type = "login"
        with pytest.raises(MasterthermTokenInvalid):
            await api.get_device_info("1234", "1")

    async def test_getinfo_invalid(self):
        """Test the device info for invalid device."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect() is not {}
        info = await api.get_device_info("1234", "2")

        assert info["returncode"] != 0

    async def test_getdata(self):
        """Test the Get Device data from new."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect() is not {}

        data = await api.get_device_data("1234", "1")

        assert data != {}
        assert data["error"]["errorId"] == 0
        assert data["messageId"] == 1
        assert data["data"] != {}

    async def test_getdata_update(self):
        """Test the Get device Data update."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect() is not {}

        data = await api.get_device_data("1234", "1")
        assert data != {}

        last_update_time = data["timestamp"]
        a_500 = data["data"]["varData"]["001"]["A_500"]

        data = await api.get_device_data("1234", "1", last_update_time=last_update_time)
        assert data != {}
        assert data["error"]["errorId"] == 0
        assert data["timestamp"] != last_update_time
        assert data["data"]["varData"]["001"]["A_500"] != a_500

    async def test_getdata_invalid(self):
        """Test the get invalid device."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect() is not {}

        try:
            await api.get_device_data("1234", "2")
        except MasterthermPumpError as ex:
            assert ex.status == MasterthermPumpError.DEVICENOTFOUND

    async def test_offline_initial(self):
        """Test getting data when the HP is offline on initial connect."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect() is not {}

        self.error_type = "unavailable"
        try:
            await api.get_device_data("1234", "1")
        except MasterthermPumpError as ex:
            assert ex.status == MasterthermPumpError.OFFLINE

    async def test_offline_update(self):
        """Test getting data when the HP is offline on update."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect() is not {}

        data = await api.get_device_data("1234", "1")
        assert data != {}

        self.error_type = "unavailable"
        try:
            await api.get_device_data("1234", "1", last_update_time=None)
        except MasterthermPumpError as ex:
            assert ex.status == MasterthermPumpError.OFFLINE

    async def test_setdata(self):
        """Test we can send data to update the API."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect() is not {}

        # Read the Data and issue, Power State
        data = await api.get_device_data("1234", "1")
        assert data["data"]["varData"]["001"]["D_3"] == "1"

        # Issue an update back to the API
        assert await api.set_device_data("1234", "1", "D_3", "0")

        # Re-Read to check the update is correct.
        data = await api.get_device_data("1234", "1")
        assert data["data"]["varData"]["001"]["D_3"] == "0"

    async def test_setdata_fail(self):
        """Test we can send data to update the API."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect() is not {}

        # Read the Data and issue, Power State
        data = await api.get_device_data("1234", "1")
        assert data["data"]["varData"]["001"]["D_3"] == "1"

        # Issue an update back to the API
        self.error_type = "write_error"
        assert await api.set_device_data("1234", "1", "D_3", "0") is False

        # Re-Read to check the update is correct.
        data = await api.get_device_data("1234", "1")
        assert data["data"]["varData"]["001"]["D_3"] == "1"

    async def test_unsupported_version(self):
        """Test exception for unsupported version."""
        with pytest.raises(MasterthermUnsupportedVersion):
            MasterthermAPI("1234", "1", self.client, api_version="v10")

    async def test_expired_token(self):
        """Test for an expired token and re-connect."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        self.error_type = "token_expire"
        assert await api.connect() is not {}

        assert await api.get_device_info("1234", "1")
        assert await api.get_device_data("1234", "1")
        assert await api.set_device_data("1234", "1", "D_3", "0")

    async def test_invalid_token(self):
        """Test for an invalid token and re-try."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect() is not {}

        assert await api.get_device_info("1234", "1")

    async def test_client_connection_error(self):
        """Test for Client Connection Errors, such as timeout."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect()
        assert await api.get_device_info("1234", "1")

        self.error_type = "ClientConnectionError"
        with pytest.raises(MasterthermConnectionError):
            await api.connect()

        with pytest.raises(MasterthermConnectionError):
            await api.get_device_info("1234", "1")

        with pytest.raises(MasterthermConnectionError):
            await api.set_device_data("1234", "1", "D_3", "0")

    async def test_response_errors(self):
        """Test response format and content errors."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect()
        assert await api.get_device_info("1234", "1")

        self.error_type = "content_error"
        with pytest.raises(MasterthermConnectionError):
            await api.get_device_data("1234", "1")

        self.error_type = "json_error"
        with pytest.raises(MasterthermResponseFormatError):
            await api.get_device_data("1234", "1")

    async def test_fail_with_retry(self):
        """Test token error with a retry."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect()

        self.error_type = "login_once"
        assert await api.get_device_info("1234", "1")

        self.error_type = "login_once"
        assert await api.get_device_data("1234", "1")

        self.error_type = "login_once"
        await api.set_device_data("1234", "1", "D_3", "0")

    async def test_timeout(self):
        """Test timeout re-tries on refresh."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v1"
        )
        assert await api.connect()

        self.error_type = "timeout_once"
        assert await api.get_device_info("1234", "1")

        self.error_type = "timeout_once"
        assert await api.get_device_data("1234", "1")

        self.error_type = "timeout_once"
        await api.set_device_data("1234", "1", "D_3", "0")
