"""MasterTherm Connection to the Web API."""
import logging

from datetime import datetime
from hashlib import sha1
from urllib.parse import urljoin

from masterthermconnect.const import (
    APP_CLIENTINFO,
    APP_OS,
    APP_VERSION,
    COOKIE_TOKEN,
    HEADER_TOKEN_EXPIRES,
    DATE_FORMAT,
    URL_BASE,
    URL_LOGIN,
    URL_PUMPDATA,
    URL_PUMPINFO,
)
from .exceptions import (
    MasterThermAuthenticationError,
    MasterThermConnectionError,
    MasterThermResponseFormatError,
    MasterThermTokenInvalid,
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
        """Perform the Post to the API server and check results."""
        # Check to see if our token is still valid, if not re-connect
        if self.__expires is None: await self.connect()
        if datetime.now() > self.__expires: await self.connect()

        # Post with the valid token
        cookies = {COOKIE_TOKEN: self.__token, "$version": APP_VERSION}
        try:
            response = await self.__session.post(
                urljoin(URL_BASE,url),
                data=params,
                headers={"content-type": "application/x-www-form-urlencoded"},
                cookies=cookies
            )
        except Exception as ex:
            _LOGGER.error("MasterTherm API some other error: %s", ex)
            raise Exception() from ex

        if response.status != 200:
            raise MasterThermConnectionError(str(response.status))

        # Convert to JSON if possible and return the result
        try:
            responseJSON = await response.json()
        except Exception:
            responseText = await response.text()
            if responseText == "User not logged in":
                _LOGGER.error("MasterTherm API Invalid Token: %s", responseText)
                raise MasterThermTokenInvalid("Token Expired")
            else:
                _LOGGER.error("MasterTherm API some other error: %s", responseText)
                raise MasterThermResponseFormatError(responseText)

        return responseJSON

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

    async def getModuleInfo(self, module_id, device_id):
        """Return the Pump Information as sent from server."""
        params = f"moduleid={module_id}&unitid={device_id}&application={APP_OS}"
        response = await self.__post(URL_PUMPINFO,params)
        return response

    async def getDeviceData(self, moduleId, deviceId):
        return {}
        