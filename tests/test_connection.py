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
)
from masterthermconnect.const import (
    COOKIE_TOKEN,
    DATE_FORMAT,
    HEADER_TOKEN_EXPIRES,
    URL_LOGIN,
)

from .conftest import (
    load_fixture,
    VALID_LOGIN,
)

@patch("masterthermconnect.connection.URL_BASE","")
class ConnectionTestCase(AioHTTPTestCase):
    """Class to hold all API connection Tests."""

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
            return response

        app = web.Application()
        app.router.add_post(URL_LOGIN,_connectResponse)
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
