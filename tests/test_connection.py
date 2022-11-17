"""Test the Connection Component."""
from datetime import datetime, timedelta
from hashlib import sha1
from unittest.mock import patch

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase
import pytest

from masterthermconnect import (
    Connection,
    MasterthermAuthenticationError,
    MasterthermConnectionError,
    MasterthermTokenInvalid,
)
from masterthermconnect.const import (
    COOKIE_TOKEN,
    DATE_FORMAT,
    URL_LOGIN,
    URL_PUMPDATA,
    URL_PUMPINFO,
)

from .conftest import GENERAL_ERROR_RESPONSE, VALID_LOGIN, load_fixture


@patch("masterthermconnect.connection.URL_BASE", "")
class ConnectionTestCase(AioHTTPTestCase):
    """Class to hold all API connection Tests."""

    logged_in = True

    async def get_application(self):
        """Start and Return a mock application."""

        async def _connect_response(request):
            """Check the Test Login Credentials and return login connect or failure."""
            data = await request.post()
            password = sha1(VALID_LOGIN["upwd"].encode("utf-8")).hexdigest()
            if data["uname"] == VALID_LOGIN["uname"] and data["upwd"] == password:
                response_text = load_fixture("login_success.json")
            else:
                response_text = load_fixture("login_invalid.json")

            token_expires = datetime.now() + timedelta(seconds=60)
            response = web.Response(
                text=response_text,
                content_type="application/json",
            )
            response.set_cookie(
                COOKIE_TOKEN, VALID_LOGIN["token"],
                expires=token_expires.strftime(DATE_FORMAT) + "GMT"
            )

            self.logged_in = True
            return response

        async def _get_info(request):
            """Get the Pump Info."""
            data = await request.post()
            if not self.logged_in:
                response_text = GENERAL_ERROR_RESPONSE
            else:
                module_id = data["moduleid"]
                device_id = data["unitid"]
                response_text = load_fixture(f"pumpinfo_{module_id}_{device_id}.json")
                if response_text is None:
                    response_text = load_fixture("pumpinfo_invalid.json")

            response = web.Response(text=response_text, content_type="application/json")
            return response

        async def _get_data(request):
            """Get the Pump Info."""
            data = await request.post()
            module_id = data["moduleId"]
            device_id = data["deviceId"]
            last_update_time = data["lastUpdateTime"]

            if not self.logged_in:
                response_text = load_fixture("pumpdata_unavailable.json")
            else:
                response_text = load_fixture(
                    f"pumpdata_{module_id}_{device_id}_{last_update_time}.json"
                )
                if response_text is None:
                    response_text = load_fixture("pumpdata_invalid.json")

            response = web.Response(text=response_text, content_type="application/json")
            return response

        app = web.Application()
        app.router.add_post(URL_LOGIN, _connect_response)
        app.router.add_post(URL_PUMPINFO, _get_info)
        app.router.add_post(URL_PUMPDATA, _get_data)
        return app

    async def test_setup(self):
        """Test the Setup of the Connection."""
        api = Connection(self.client, VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
        assert await api.is_connected() is False

    async def test_connect(self):
        """Test the Connection login."""
        api = Connection(self.client, VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
        result = await api.connect()

        assert result != {}
        assert result["returncode"] == 0
        assert result["modules"][0]["id"] == "1234"
        assert result["role"] == "400"

        assert await api.is_connected() is True

    async def test_autherror(self):
        """Test the Connection Authentication Error."""
        api = Connection(self.client, VALID_LOGIN["uname"], VALID_LOGIN["upwd"] + "bad")

        with pytest.raises(MasterthermAuthenticationError):
            await api.connect()

    async def test_connecterror(self):
        """Test the Connection Invalid Error."""
        api = Connection(self.client, VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
        with patch("masterthermconnect.connection.URL_LOGIN", "/"), pytest.raises(
            MasterthermConnectionError
        ):
            await api.connect()

    async def test_getinfo(self):
        """Test the Get Pump Info."""
        api = Connection(self.client, VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
        assert await api.connect() is not {}

        info = await api.get_device_info("1234", "1")

        assert info != {}
        assert info["moduleid"] == "1234"
        assert info["type"] == "AQI"

    async def test_getinfo_notconnected(self):
        """Test the Get Pump Info, on logged in."""
        api = Connection(self.client, VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
        assert await api.connect() is not {}

        self.logged_in = False
        with pytest.raises(MasterthermTokenInvalid):
            await api.get_device_info("1234", "1")

    async def test_getinfo_invalid(self):
        """Test the Get Pump Info, Invalid Device."""
        api = Connection(self.client, VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
        assert await api.connect() is not {}
        info = await api.get_device_info("1234", "2")

        assert info["returncode"] != 0

    async def test_getdata(self):
        """Test the Get Pump Data from New."""
        api = Connection(self.client, VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
        assert await api.connect() is not {}

        data = await api.get_device_data("1234", "1")

        assert data != {}
        assert data["error"]["errorId"] == 0
        assert data["messageId"] == 1
        assert data["data"] != {}

    async def test_getdata_update(self):
        """Test the Get Pump Data Updated."""
        api = Connection(self.client, VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
        assert await api.connect() is not {}

        data = await api.get_device_data("1234", "1")
        assert data != {}

        last_update_time = data["timestamp"]
        a_500 = data["data"]["varfile_mt1_config1"]["001"]["A_500"]

        data = await api.get_device_data("1234", "1", last_update_time=last_update_time)
        assert data != {}
        assert data["error"]["errorId"] == 0
        assert data["timestamp"] != last_update_time
        assert data["data"]["varfile_mt1_config1"]["001"]["A_500"] != a_500

    async def test_getdata_invalid(self):
        """Test the Get Pump Data invalid device."""
        api = Connection(self.client, VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
        assert await api.connect() is not {}

        data = await api.get_device_data("1234", "2")
        assert data != {}
        assert data["error"]["errorId"] != 0

    async def test_getdata_unavailable(self):
        """Test the Get Pump Data unavailable device."""
        api = Connection(self.client, VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
        assert await api.connect() is not {}

        self.logged_in = False

        data = await api.get_device_data("1234", "1")
        assert data != {}
        assert data["error"]["errorId"] == 9
