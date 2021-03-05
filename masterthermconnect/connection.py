"""MasterTherm Connection to the Web API."""
import logging

from datetime import datetime
from hashlib import sha1
from urllib.parse import urljoin

from masterthermconnect.const import (
    APP_CLIENTINFO,
    COOKIE_TOKEN,
    HEADER_TOKEN_EXPIRES,
    DATE_FORMAT,
    URL_BASE,
    URL_LOGIN,
)
from .exceptions import (
    MasterThermAuthenticationError,
    MasterThermConnectionError,
)

_LOGGER = logging.getLogger(__name__)

class Connection:
    """Connection Handler for the MasterTherm API."""

    def __init__(self, websession, username, password):
        """Initiate the Connection API."""
        self.__session = websession
        self.__unname = username
        self.__upwd = sha1(password.encode("utf-8")).hexdigest()
        self.__clientinfo = APP_CLIENTINFO
        self.__token = None
        self.__expires = None
        self.__isConnected = False

    async def __post(self, url, params):
        """Post a request with Parameters to the API, check if re-connection is needed."""
        return {}

    async def connect(self):
        """Perform the connection tot he API Server, setup the Tokens and return configured modules."""
        self.__isConnected = False

        params = f"login=login&uname={self.__unname}&upwd={self.__upwd}&{self.__clientinfo}"
        response = await self.__session.post(
            urljoin(URL_BASE,URL_LOGIN),
            data=params,
            headers={"content-type": "application/x-www-form-urlencoded"}
        )

        # Response should always be 200 even for login failures.
        if response.status != 200:
            errorMsg = await response.text()
            raise MasterThermConnectionError(str(response.status), errorMsg)

        # Expect that the response is JSON, check the result.
        responseJSON = await response.json()
        if responseJSON["returncode"] != 0:
            raise MasterThermAuthenticationError(responseJSON["returncode"],responseJSON["message"])
        
        # Get or Refresh the Token and Expiry
        self.__token = response.cookies[COOKIE_TOKEN].value
        self.__expires = datetime.strptime(response.headers[HEADER_TOKEN_EXPIRES], DATE_FORMAT)
        
        self.__isConnected = True
        return responseJSON

    async def isConnected(self):
        """Check we are connected to the API and still valid."""
        # Check expiry, maybe just get info to check.
        return self.__isConnected

    async def getModuleInfo(self, moduleId):
        return {}

    async def getDeviceData(self, moduleId, deviceId):
        return {}
        