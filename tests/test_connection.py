"""Test the Connection Component."""
import json
import pytest

from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from datetime import datetime, timedelta
from hashlib import sha1
from unittest.mock import patch

from masterthermconnect import (
    Connection,
    MasterThermAuthenticationError,
    MasterThermConnectionError,
    MasterThermResponseFormatError,
    MasterThermTokenInvalid,
)
from masterthermconnect.const import (
    COOKIE_TOKEN,
    DATE_FORMAT,
    HEADER_TOKEN_EXPIRES,
    URL_LOGIN,
    URL_PUMPDATA,
    URL_PUMPINFO,
)

from .conftest import (
    load_fixture,
    GENERAL_ERROR_RESPONSE,
    VALID_LOGIN,
)

@patch("masterthermconnect.connection.URL_BASE","")
class ConnectionTestCase(AioHTTPTestCase):
    """Class to hold all API connection Tests."""
    loggedIn = True

    async def get_application(self):
        """Setup and return the Application with any routes needed."""
        async def _connectResponse(request):
            """Check the Test Login Credentials and return loggin connect or failure."""
            data = await request.post()
            password = sha1(VALID_LOGIN["upwd"].encode("utf-8")).hexdigest()
            if data["uname"] == VALID_LOGIN["uname"] and data["upwd"] == password:
                responseText = load_fixture("login_success.json")
            else:
                responseText = load_fixture("login_invalid.json")

            token_expires = datetime.now() + timedelta(seconds=10)
            expire_header = {
                HEADER_TOKEN_EXPIRES: token_expires.strftime(DATE_FORMAT) + "GMT"
            }
            response = web.Response(text=responseText,headers=expire_header,content_type="application/json")
            response.set_cookie(COOKIE_TOKEN,VALID_LOGIN["token"])

            self.loggedIn = True
            return response

        async def _getInfo(request):
            """Get the Pump Info."""
            data = await request.post()
            token = request.cookies[COOKIE_TOKEN]
            if not self.loggedIn:
                responseText = GENERAL_ERROR_RESPONSE
            else:
                module_id = data["moduleid"]
                device_id = data["unitid"]
                responseText = load_fixture(f"pumpinfo_{module_id}_{device_id}.json")
                if responseText is None:
                    responseText = load_fixture("pumpinfo_invalid.json")

            response = web.Response(text=responseText,content_type="application/json")
            return response

        app = web.Application()
        app.router.add_post(URL_LOGIN,_connectResponse)
        app.router.add_post(URL_PUMPINFO,_getInfo)
        return app

    @unittest_run_loop
    async def test_setup(self):
        """Test the Setup of the Connection."""
        api = Connection(self.client,VALID_LOGIN["uname"],VALID_LOGIN["upwd"])
        assert await api.isConnected() == False

    @unittest_run_loop
    async def test_connect(self):
        """Test the Connection login."""
        api = Connection(self.client,VALID_LOGIN["uname"],VALID_LOGIN["upwd"])
        result = await api.connect() 

        assert result != {}
        assert result["returncode"] == 0
        assert result["modules"][0]["id"] == "1234"
        assert result["role"] == "400"

        assert await api.isConnected() == True

    @unittest_run_loop
    async def test_autherror(self):
        """Test the Connection Authentication Error."""
        api = Connection(self.client,VALID_LOGIN["uname"],VALID_LOGIN["upwd"]+"bad")

        with pytest.raises(MasterThermAuthenticationError):
            result = await api.connect() 

    @unittest_run_loop
    async def test_connecterror(self):
        """Test the Connection Invalid Error."""
        api = Connection(self.client,VALID_LOGIN["uname"],VALID_LOGIN["upwd"])
        with patch(
            "masterthermconnect.connection.URL_LOGIN",
            "/"
        ), pytest.raises(
            MasterThermConnectionError
        ):
           result = await api.connect()

    @unittest_run_loop
    async def test_getinfo(self):
        """Test the Get Pump Info."""
        api = Connection(self.client,VALID_LOGIN["uname"],VALID_LOGIN["upwd"])
        result = await api.connect() 

        info = await api.getModuleInfo("1234","1")

        assert info != {}
        assert info["moduleid"] == "1234"
        assert info["type"] == "AQI"

    @unittest_run_loop
    async def test_getinfo_notconnected(self):
        """Test the Get Pump Info, on logged in."""
        api = Connection(self.client,VALID_LOGIN["uname"],VALID_LOGIN["upwd"])
        result = await api.connect() 

        self.loggedIn = False
        with pytest.raises(MasterThermTokenInvalid):
            info = await api.getModuleInfo("1234","1")

    @unittest_run_loop
    async def test_getinfo_invalid(self):
        """Test the Get Pump Info, Invalid Device."""
        api = Connection(self.client,VALID_LOGIN["uname"],VALID_LOGIN["upwd"])
        result = await api.connect() 
        info = await api.getModuleInfo("1234","2")

        assert info["returncode"] != 0

    @unittest_run_loop
    async def test_getdata(self):
        """Test the Get Pump Data from New."""
        pass

    @unittest_run_loop
    async def test_getdata_update(self):
        """Test the Get Pump Data Updated."""
        pass

