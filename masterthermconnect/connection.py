"""MasterTherm Connection to the Web API."""
from datetime import datetime
from hashlib import sha1
import logging
from urllib.parse import urljoin
from json.decoder import JSONDecodeError

from masterthermconnect.const import (
    APP_CLIENTINFO,
    APP_OS,
    APP_VERSION,
    COOKIE_TOKEN,
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
        self.__is_connected = False

    async def __post(self, url, params):
        """Perform the Post to the API server and check results."""
        # Check to see if our token is still valid, if not re-connect
        if self.__expires is None:
            await self.connect()
        if datetime.now() > self.__expires:
            await self.connect()

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
            error_msg = await response.text()
            raise MasterThermConnectionError(str(response.status),error_msg)

        # Convert to JSON if possible and return the result
        try:
            response_json = await response.json()
        except JSONDecodeError as exc:
            response_text = await response.text()
            if response_text == "User not logged in":
                _LOGGER.error("MasterTherm API Invalid Token: %s", response_text)
                raise MasterThermTokenInvalid("1", response_text) from exc
            else:
                _LOGGER.error("MasterTherm API some other error: %s", response_text)
                raise MasterThermResponseFormatError("2",response_text) from exc

        return response_json

    async def connect(self):
        """Perform the connection to the Mastertherm API Server:

        Returns:
             json_repsonse (dict): Devices and Information in JSON Format

        Raises:
            MasterThermConnectionError - Failed to Connect
            MasterThermAuthenticationError - Failed to Authenticate"""

        # TODO Check Reconnection on Expire
        self.__is_connected = False

        params = f"login=login&uname={self.__unname}&upwd={self.__upwd}&{self.__clientinfo}"
        response = await self.__session.post(
            urljoin(URL_BASE,URL_LOGIN),
            data=params,
            headers={"content-type": "application/x-www-form-urlencoded"}
        )

        # Response should always be 200 even for login failures.
        if response.status != 200:
            error_msg = await response.text()
            raise MasterThermConnectionError(str(response.status), error_msg)

        # Expect that the response is JSON, check the result.
        response_json = await response.json()
        if response_json["returncode"] != 0:
            raise MasterThermAuthenticationError(
                response_json["returncode"],response_json["message"])

        # Get or Refresh the Token and Expiry
        cookie = response.cookies.get(COOKIE_TOKEN)
        self.__token = cookie.value
        self.__expires = datetime.strptime(cookie["expires"], DATE_FORMAT)

        self.__is_connected = True
        return response_json

    async def is_connected(self):
        """Check we are connected to the API and still valid."""
        # Check expiry, maybe just get info to check.
        return self.__is_connected

    async def get_device_info(self, module_id, device_id):
        """Return the Pump Information as sent from server."""
        params = f"moduleid={module_id}&unitid={device_id}&application={APP_OS}"
        response = await self.__post(URL_PUMPINFO,params)
        return response

    async def get_device_data(self, module_id, device_id, last_update_time = None):
        """Return the Device Data from the server."""
        params = f"moduleId={module_id}&deviceId={device_id}&application={APP_OS}&"
        if last_update_time is None:
            params = params + "messageId=1&lastUpdateTime=0&errorResponse=true&fullRange=true"
        else:
            params = params + \
                f"messageId=2&lastUpdateTime={last_update_time}&errorResponse=true&fullRange=true"
        response = await self.__post(URL_PUMPDATA,params)
        return response
