"""Test the New API Client."""
import json

from unittest.mock import patch

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, Request

import pytest

from masterthermconnect import (
    MasterthermAuthenticationError,
    MasterthermConnectionError,
    MasterthermResponseFormatError,
    MasterthermTokenInvalid,
    MasterthermPumpError,
    MasterthermUnsupportedVersion,
)
from masterthermconnect.api import MasterthermAPI
from masterthermconnect.const import (
    URL_LOGIN_NEW,
    URL_MODULES_NEW,
    URL_PUMPDATA_NEW,
    URL_PUMPINFO_NEW,
    URL_POSTUPDATE_NEW,
)

from .conftest import VALID_LOGIN, load_fixture


@patch("masterthermconnect.api.URL_BASE_NEW", "")
class APINewTestCase(AioHTTPTestCase):
    """Test the New API Connection."""

    error_type = ""
    data: dict = None
    info: dict = None

    async def get_application(self):
        """Start and Return a mock application."""

        async def _connect_response(request: Request):
            """Check the Test Login Credentials and return login connect or failure."""
            data = await request.post()

            if self.error_type == "ClientConnectionError":
                return None

            if (
                data["username"] == VALID_LOGIN["uname"]
                and data["password"] == VALID_LOGIN["upwd"]
            ):
                response_text = load_fixture("newapi/login_success.json")

                if self.error_type == "token_expire":
                    response_text = response_text.replace(": 7200", ": 0")
                else:
                    self.data = None
                    self.info = None
            else:
                response_text = load_fixture("newapi/login_invalid.json")

            response = web.Response(
                text=response_text,
                content_type="application/json",
            )

            return response

        async def _get_modules(request: Request):
            """Get the Devices, new in the new API."""
            token = request.headers.get("Authorization")
            content_type = "application/json"
            response_status = 200
            if self.error_type == "login" or token != "Bearer bearertoken":
                response_text = load_fixture("newapi/error_authorization.json")
                response_status = 401
            else:
                response_text = load_fixture("newapi/modules.json")

            if response_text is None:
                response_text = load_fixture("newapi/error_unavailable.json")
                response_status = 500

            response = web.Response(
                status=response_status, text=response_text, content_type=content_type
            )
            return response

        async def _get_info(request: Request):
            """Get the Pump Info."""
            token = request.headers.get("Authorization")
            data = request.query
            content_type = "application/json"
            response_status = 200

            if self.error_type == "ClientConnectionError":
                return None

            if self.error_type == "login" or token != "Bearer bearertoken":
                response_text = load_fixture("newapi/error_authorization.json")
                response_status = 401
            elif self.info is None:
                module_id = data["moduleid"]
                unit_id = data["unitid"]
                response_text = load_fixture(
                    f"newapi/pumpinfo_{module_id}_{unit_id}.json"
                )
            else:
                response_text = json.dumps(self.info)

            if response_text is None:
                response_text = load_fixture("newapi/error_unavailable.json")
                response_status = 500
            else:
                self.info = json.loads(response_text)

            response = web.Response(
                status=response_status, text=response_text, content_type=content_type
            )
            return response

        async def _get_data(request: Request):
            """Get the Pump Info."""
            token = request.headers.get("Authorization")
            data = request.query

            if self.error_type == "ClientConnectionError":
                return None

            module_id = data["moduleId"]
            unit_id = data["deviceId"]
            last_update_time = data["lastUpdateTime"]

            content_type = "application/json"
            response_status = 200
            if self.error_type == "login" or token != "Bearer bearertoken":
                response_text = load_fixture("newapi/error_authorization.json")
                response_status = 401
            elif self.data is None or last_update_time != "0":
                response_text = load_fixture(
                    f"newapi/pumpdata_{module_id}_{unit_id}_{last_update_time}.json"
                )
            else:
                response_text = json.dumps(self.data)

            if response_text is None:
                response_text = load_fixture("newapi/error_unavailable.json")
                response_status = 500
            else:
                self.data = json.loads(response_text)

            response = web.Response(
                status=response_status, text=response_text, content_type=content_type
            )
            return response

        async def _set_data(request: Request):
            """Set the Pump Data."""
            data = await request.post()
            content_type = "application/json"
            # module_id = data["moduleId"]
            unit_id = str(data["deviceId"]).zfill(3)
            variable_id = data["variableId"]
            variable_value = data["variableValue"]

            response_text = load_fixture("newapi/pumpwrite_success.json")
            self.data["data"]["varFileData"][unit_id][variable_id] = variable_value

            response = web.Response(text=response_text, content_type=content_type)
            return response

        app: web.Application = web.Application()
        app.router.add_post(URL_LOGIN_NEW, _connect_response)
        app.router.add_get(URL_MODULES_NEW, _get_modules)
        app.router.add_get(URL_PUMPINFO_NEW, _get_info)
        app.router.add_get(URL_PUMPDATA_NEW, _get_data)
        app.router.add_post(URL_POSTUPDATE_NEW, _set_data)

        return app

    async def test_setup(self):
        """Test the API Setup."""
        assert MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )

    async def test_connect(self):
        """Test the API Logs in and Returns modules."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        result = await api.connect()

        assert result != {}
        assert result["returncode"] == 0
        assert result["modules"][0]["id"] == "10021"
        assert result["role"] == "400"

    async def test_autherror(self):
        """Test a Connection Authentication Error."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"],
            VALID_LOGIN["upwd"] + "bad",
            self.client,
            api_version="v2",
        )

        with pytest.raises(MasterthermAuthenticationError):
            await api.connect()

    async def test_connecterror(self):
        """Test the Connection Invalid Error."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )

        with patch("masterthermconnect.api.URL_LOGIN_NEW", "/"), pytest.raises(
            MasterthermConnectionError
        ):
            await api.connect()

    async def test_getinfo(self):
        """Test returning the Device Information."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        assert await api.connect() != {}

        info = await api.get_device_info("10021", "1")

        assert info != {}
        assert info["moduleid"] == 10021
        assert info["type"] == "BAI"

    async def test_getinfo_tokeninvalid(self):
        """Test the get device info when token is invalid."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        assert await api.connect() is not {}

        self.error_type = "login"
        with pytest.raises(MasterthermTokenInvalid):
            await api.get_device_info("10021", "1")

    async def test_getinfo_invalid(self):
        """Test the device info for invalid device."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        assert await api.connect() is not {}

        with pytest.raises(MasterthermResponseFormatError):
            await api.get_device_info("1234", "2")

    async def test_getdata(self):
        """Test the Get Device data from new."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        assert await api.connect() is not {}

        data = await api.get_device_data("10021", "1")

        assert data != {}
        assert data["error"]["errorId"] == 0
        assert data["messageId"] == 1
        assert data["data"] != {}

    async def test_getdata_update(self):
        """Test the Get device Data update."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        assert await api.connect() is not {}

        data = await api.get_device_data("10021", "1")
        assert data != {}

        last_update_time = data["timestamp"]
        a_500 = data["data"]["varData"]["001"]["A_500"]

        data = await api.get_device_data(
            "10021", "1", last_update_time=last_update_time
        )
        assert data != {}
        assert data["error"]["errorId"] == 0
        assert data["timestamp"] != last_update_time
        assert data["data"]["varData"]["001"]["A_500"] != a_500

    async def test_getdata_invalid(self):
        """Test the get invalid device."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        assert await api.connect() is not {}

        with pytest.raises(MasterthermResponseFormatError):
            await api.get_device_info("1234", "2")

    async def test_offline_initial(self):
        """Test getting data when the HP is offline on initial connect."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        assert await api.connect() is not {}

        self.error_type = "unavailable"
        try:
            await api.get_device_data("10021", "1")
        except MasterthermPumpError as ex:
            assert ex.status == MasterthermPumpError.OFFLINE

    async def test_offline_update(self):
        """Test getting data when the HP is offline on update."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        assert await api.connect() is not {}

        data = await api.get_device_data("10021", "1")
        assert data != {}

        self.error_type = "unavailable"
        try:
            await api.get_device_data("10021", "1", last_update_time=None)
        except MasterthermPumpError as ex:
            assert ex.status == MasterthermPumpError.OFFLINE

    async def test_setdata(self):
        """Test we can send data to update the API."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        assert await api.connect() is not {}

        # Read the Data and issue, Power State
        data = await api.get_device_data("10021", "1")
        assert data["data"]["varData"]["001"]["D_3"] == "1"

        # Issue an update back to the API
        assert await api.set_device_data("10021", "1", "D_3", "0")

        # Re-Read to check the update is correct.
        data = await api.get_device_data("10021", "1")
        assert data["data"]["varData"]["001"]["D_3"] == "0"

    async def test_unsupported_version(self):
        """Test exception for unsupported version."""
        with pytest.raises(MasterthermUnsupportedVersion):
            MasterthermAPI("1234", "1", self.client, api_version="v10")

    async def test_expired_token(self):
        """Test for an expired token and re-connect."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        self.error_type = "token_expire"
        assert await api.connect() is not {}

        assert await api.get_device_info("10021", "1")
        assert await api.get_device_data("10021", "1")
        assert await api.set_device_data("10021", "1", "D_3", "0")

    async def test_client_connection_error(self):
        """Test for Client Connection Errors, such as timeout."""
        api = MasterthermAPI(
            VALID_LOGIN["uname"], VALID_LOGIN["upwd"], self.client, api_version="v2"
        )
        assert await api.connect()
        assert await api.get_device_info("10021", "1")

        self.error_type = "ClientConnectionError"
        with pytest.raises(MasterthermConnectionError):
            await api.connect()

        with pytest.raises(MasterthermConnectionError):
            await api.get_device_info("10021", "1")

        with pytest.raises(MasterthermConnectionError):
            await api.set_device_data("10021", "1", "D_3", "0")
