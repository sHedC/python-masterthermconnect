"""Mastertherm API Client Class, handle integration."""
import logging

from datetime import datetime, timedelta
from hashlib import sha1
from json.decoder import JSONDecodeError
from urllib.parse import urljoin

from aiohttp import ClientSession

from .const import (
    APP_CLIENTINFO,
    APP_CLIENTINFO_NEW,
    DATE_FORMAT,
    SUPPORTED_ROLES,
    URL_BASE,
    URL_BASE_NEW,
    URL_LOGIN,
    URL_LOGIN_NEW,
    URL_MODULES_NEW,
    URL_PUMPDATA,
    URL_PUMPDATA_NEW,
    URL_PUMPINFO,
    URL_PUMPINFO_NEW,
)
from .exceptions import (
    MasterthermAuthenticationError,
    MasterthermConnectionError,
    MasterthermUnsupportedRole,
    MasterthermTokenInvalid,
    MasterthermResponseFormatError,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class MasterthermAPI:
    """API Handler for the Mastertherm API."""

    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession,
        original_api: bool = True,
    ) -> None:
        """Initialise the Mastertherm API Client.

        Parameters:
            username (str): The Login Username
            password (str): The Login Password
            session (ClientSession): an aiohttp client session
            original_api (bool): Optional defaults to true, false for post 2022 pumps"""
        self.__session = session
        self.__original_api = original_api
        self.__token = None
        self.__expires = None

        # Setup the Session Details based on if Old or New API.
        if self.__original_api:
            hashpass = sha1(password.encode("utf-8")).hexdigest()
            codeduser = username.replace(" ", "+")
            self.__login_params = (
                f"login=login&uname={codeduser}&upwd={hashpass}&{APP_CLIENTINFO}"
            )
        else:
            self.__login_params = (
                f"grant_type=password&username={username}&"
                + f"password={password}&{APP_CLIENTINFO_NEW}"
            )

    def __token_expired(self) -> bool:
        """Return if the token has expired.

        Return:
            token_expired (bool): Return true if token has expired."""

        # TODO: Simplify and make more robust
        if self.__expires is None:
            return True

        if datetime.now() > self.__expires:
            return True

        return False

    async def __get(self, url: str, params: str) -> dict:
        """Get updates from the API, for old this mostly uses Post.

        Parameters:
            url (str): The url part for the request
            params (str): The parameters to send with the request

        Return:
            device_info (dict): Information for a specific device."""

        # TODO: Document Exceptions and Return
        if self.__token_expired():
            _LOGGER.info("Token Expired.")

        try:
            if self.__original_api:
                # Original uses post, with Cookie Token
                response = await self.__session.post(
                    urljoin(URL_BASE, url),
                    data=params,
                    headers={"content-type": "application/x-www-form-urlencoded"},
                    cookies={"PHPSESSID": self.__token, "$version": "1"},
                )
            else:
                # New uses get, with Authorization Bearer
                response = await self.__session.get(
                    urljoin(URL_BASE_NEW, url),
                    params=params,
                    headers={
                        "Authorization": f"Bearer {self.__token}",
                        "Host": "mastertherm.online",
                        "Connection": "close",
                    },
                )
        except Exception as ex:
            # TODO: Be more specific with exceptions.
            _LOGGER.error("Some posting error has occured: %s", ex)
            raise Exception() from ex

        # We should only get something other than 200 if the servers are down.
        if response.status != 200:
            error_msg = await response.text()
            raise MasterthermConnectionError(str(response.status), error_msg)

        # Convert to JSON if possible and return the result
        try:
            response_json = await response.json()
        except JSONDecodeError as exc:
            response_text = await response.text()
            if response_text == "User not logged in":
                _LOGGER.error("Mastertherm API Invalid Token: %s", response_text)
                raise MasterthermTokenInvalid("1", response_text) from exc
            else:
                _LOGGER.error("Mastertherm API some other error: %s", response_text)
                raise MasterthermResponseFormatError("2", response_text) from exc

        return response_json

    async def connect(self) -> dict:
        """Perform the connection to the Mastertherm API Server:

        Returns:
             devices (dict): Return the list of devices, modules and units.

        Raises:
            MasterthermConnectionError - Failed to Connect
            MasterthermAuthenticationError - Failed to Authenticate
            MasterthermUnsupportedRole - Role is not in supported roles"""
        # Connect based on requirements
        if self.__original_api:
            url = urljoin(URL_BASE, URL_LOGIN)
        else:
            url = urljoin(URL_BASE_NEW, URL_LOGIN_NEW)

        response = await self.__session.post(
            url,
            data=self.__login_params,
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        # Response shoudl always be 200 even for login failures
        if response.status != 200:
            error_msg = await response.text()
            raise MasterthermConnectionError(str(response.status), error_msg)

        response_json = await response.json()

        # Separate process for Old and New API's
        if self.__original_api:
            # Old Process gets return and modules in one go
            # token and expiry is stored in a cookie.
            if response_json["returncode"] != 0:
                raise MasterthermAuthenticationError(
                    response_json["returncode"], response_json["message"]
                )

            # Get or Refresh the Token and Expiry
            self.__token = response.cookies["PHPSESSID"].value
            self.__expires = datetime.strptime(
                response.cookies["PHPSESSID"]["expires"], DATE_FORMAT
            )
        else:
            # New process uses JSON responses with Openconnect ID.
            # Requires an additional call to get the modules.
            if "error" in response_json:
                raise MasterthermAuthenticationError(
                    response_json["error"], response_json["error_description"]
                )

            #  Get or Refresh the Token and Expiry
            self.__token = response_json["access_token"]
            self.__expires = datetime.today() + timedelta(
                seconds=response_json["expires_in"]
            )

            # Get the Modules as this now has moved to outside of the auth process
            url = urljoin(URL_BASE_NEW, URL_MODULES_NEW)
            response = await self.__session.get(
                url, headers={"Authorization": f"Bearer {self.__token}"}
            )

            # Response shoudl always be 200 even for login failures
            if response.status != 200:
                error_msg = await response.text()
                raise MasterthermConnectionError(str(response.status), error_msg)

            response_json = await response.json()

        # Next is same for old and new process, doing a double check just incase
        if response_json["returncode"] != 0:
            raise MasterthermAuthenticationError(
                response_json["returncode"], response_json["message"]
            )

        # Check if role is supported
        if not response_json["role"] in SUPPORTED_ROLES:
            raise MasterthermUnsupportedRole(
                "2", "Unsupported Role " + response_json["role"]
            )

        _LOGGER.info("Token Expires: %s", {self.__expires})

        return response_json

    async def get_device_info(self, module_id: str, unit_id: str) -> dict:
        """Get the Device information.

        Parameters:
            module_id (str): This is the module_id for the unit
            unit_id (str): This is the unit id for the unit

        Return:
            device_info (dict): Information for a specific device."""
        params = f"moduleid={module_id}&unitid={unit_id}&application=android"
        response_json = await self.__get(
            url=URL_PUMPINFO if self.__original_api else URL_PUMPINFO_NEW, params=params
        )

        return response_json

    async def get_device_data(
        self, module_id: str, unit_id: str, last_update_time: str = None
    ) -> dict:
        """Get the Device lastest data.

        Parameters:
            module_id (str): This is the module_id for the unit
            unit_id (str): This is the unit id for the unit
            last_update_time (str): Optional last update date in number format

        Return:
            device_data (dict): data or updated data for a specific device."""

        params = f"moduleId={module_id}&deviceId={unit_id}&application=android&"
        if last_update_time is None:
            params = (
                params
                + "messageId=1&lastUpdateTime=0&errorResponse=true&fullRange=true"
            )
        else:
            params = (
                params
                + f"messageId=2&lastUpdateTime={last_update_time}&errorResponse=true&fullRange=true"
            )

        response_json = await self.__get(
            url=URL_PUMPDATA if self.__original_api else URL_PUMPDATA_NEW, params=params
        )

        if self.__original_api and response_json["data"] != {}:
            if "varfile_mt1_config1" in response_json["data"]:
                file_data = "varfile_mt1_config1"
            elif "varfile_mt1_config2" in response_json["data"]:
                file_data = "varfile_mt1_config2"

            response_json["data"]["varFileData"] = response_json["data"][file_data]
            del response_json["data"][file_data]

        return response_json
