"""Mastertherm API Client Class, handle integration."""

import asyncio
import logging
import time

from datetime import datetime, timedelta
from hashlib import sha1
from json.decoder import JSONDecodeError
from urllib.parse import urljoin, quote_plus

from natsort import natsorted

from aiohttp import ClientSession, ClientConnectionError, ContentTypeError

from .const import (
    APP_CLIENTINFO,
    APP_CLIENTINFO_NEW,
    DATE_FORMAT,
    SUPPORTED_ROLES,
    SUPPORTED_API_VERSIONS,
    URL_BASE,
    URL_BASE_NEW,
    URL_LOGIN,
    URL_LOGIN_NEW,
    URL_MODULES_NEW,
    URL_PUMPDATA,
    URL_PUMPDATA_NEW,
    URL_PUMPINFO,
    URL_PUMPINFO_NEW,
    URL_POSTUPDATE,
    URL_POSTUPDATE_NEW,
)
from .exceptions import (
    MasterthermAuthenticationError,
    MasterthermConnectionError,
    MasterthermUnsupportedRole,
    MasterthermUnsupportedVersion,
    MasterthermTokenInvalid,
    MasterthermResponseFormatError,
    MasterthermPumpError,
    MasterthermServerTimeoutError,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)


class MasterthermAPI:
    """API Handler for the Mastertherm API."""

    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession,
        api_version: str,
    ) -> None:
        """Initialise the Mastertherm API Client.

        Args:
            username: The Login Username
            password: The Login Password
            session: an aiohttp client session
            api_version: The version of the API, mainly the host
                "v1"  : Original version, data response in varfile_mt1_config1 or 2
                "v2"  : New version since 2022 response in varFileData

        Returns:
            The MasterthermAPI object

        Raises:
            MasterthermUnsupportedVersion: API Version is not supported.

        """
        if api_version not in SUPPORTED_API_VERSIONS:
            raise MasterthermUnsupportedVersion(
                "-1", f"Unsupported Version {api_version}"
            )

        self.__session = session
        self.__api_version = api_version
        self.__token = None
        self.__expires = None

        # Setup the Session Details based on if Old or New API.
        codeduser = quote_plus(username)
        if self.__api_version == "v1":
            hashpass = sha1(password.encode("utf-8")).hexdigest()
            self.__login_params = (
                f"login=login&uname={codeduser}&upwd={hashpass}&{APP_CLIENTINFO}"
            )
        else:
            codedpass = quote_plus(password)
            self.__login_params = (
                f"grant_type=password&username={codeduser}&"
                + f"password={codedpass}&{APP_CLIENTINFO_NEW}"
            )

    async def __token_expired(self) -> bool:
        """Return if the token has expired."""
        if self.__expires is None:
            return True

        if self.__api_version == "v1":
            if self.__expires <= datetime.fromtimestamp(time.mktime(time.gmtime())):
                return True
        else:
            if self.__expires <= datetime.now():
                return True

        return False

    async def __post(self, url: str, params: str) -> dict:
        """Push updates to the API."""
        if await self.__token_expired():
            _LOGGER.info("__post: Token Expired, Refreshing Token.")
            await self.__connect_refresh()

        _LOGGER.debug("__post: data to: %s, params: %s", url, params)
        try:
            if self.__api_version == "v1":
                # Original uses post, with Cookie Token
                response = await self.__session.post(
                    urljoin(URL_BASE, url),
                    data=params,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    cookies={"PHPSESSID": self.__token, "$version": "1"},
                )
            else:
                # New uses get, with Authorization Bearer
                response = await self.__session.post(
                    urljoin(URL_BASE_NEW, url),
                    data=params,
                    headers={
                        "Authorization": f"Bearer {self.__token}",
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Host": "mastertherm.online",
                        "Connection": "close",
                    },
                )

            _LOGGER.debug(
                "__post: response status: %s, content: %s",
                response.status,
                await response.text(),
            )
            response_json = await response.json()
        except ClientConnectionError as ex:
            _LOGGER.error("Client Connection Error: %s", ex)
            raise MasterthermConnectionError("3", "Client Connection Error") from ex
        except JSONDecodeError as ex:
            response_text = await response.text()
            _LOGGER.error(
                "JSON Decode Error: %s:%s",
                response.status,
                response_text,
            )
            raise MasterthermResponseFormatError(response.status, response_text) from ex
        except ContentTypeError as ex:
            if response.status == 504:
                raise MasterthermServerTimeoutError(
                    response.status, response.reason
                ) from ex

            response_text = await response.text()
            if response_text == "User not logged in":
                raise MasterthermTokenInvalid(response.status, response_text) from ex
            else:
                _LOGGER.error(
                    "Mastertherm API some other error: %s:%s",
                    response.status,
                    response_text,
                )
                raise MasterthermConnectionError(response.status, response_text) from ex

        # Version 2 responds with an error and json.
        # We should only get something other than 200 if the servers are down.
        if response.status != 200:
            # Deal with the v2 error if we have a response
            if response_json["status"]["id"] == 401:
                raise MasterthermTokenInvalid(response.status, response_json)
            else:
                _LOGGER.error("Mastertherm API some other error: %s", response_json)
                raise MasterthermResponseFormatError(response.status, response_json)

        return response_json

    async def __get(self, url: str, params: str) -> dict:
        """Get updates from the API, for old this mostly uses Post."""
        if await self.__token_expired():
            _LOGGER.info("__get: Token Expired, Refreshing Token.")
            await self.__connect_refresh()

        _LOGGER.debug("__get: data from: %s", url)
        try:
            if self.__api_version == "v1":
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

            _LOGGER.debug(
                "__get: response status: %s, content: %s",
                response.status,
                await response.text(),
            )
            response_json = await response.json()
        except ClientConnectionError as ex:
            _LOGGER.error("Client Connection Error: %s", ex)
            raise MasterthermConnectionError("3", "Client Connection Error") from ex
        except JSONDecodeError as ex:
            response_text = await response.text()
            _LOGGER.error(
                "JSON Decode Error: %s:%s",
                response.status,
                response_text,
            )
            raise MasterthermResponseFormatError(response.status, response_text) from ex
        except ContentTypeError as ex:
            if response.status == 504:
                raise MasterthermServerTimeoutError(
                    response.status, response.reason
                ) from ex

            response_text = await response.text()
            if response_text == "User not logged in":
                raise MasterthermTokenInvalid(response.status, response_text) from ex
            else:
                _LOGGER.error(
                    "Mastertherm API some other error: %s:%s",
                    response.status,
                    response_text,
                )
                raise MasterthermConnectionError(response.status, response_text) from ex

        # Version 2 responds with an error and json.
        if response.status != 200:
            # Deal with the v2 error if we have a response
            if response_json["status"]["id"] == 401:
                raise MasterthermTokenInvalid(response.status, response_json)
            else:
                _LOGGER.error("Mastertherm API some other error: %s", response_json)
                raise MasterthermResponseFormatError(response.status, response_json)

        return response_json

    async def __connect_refresh(self) -> dict:
        """Perform the Connect only or refresh token."""
        # Connect based on requirements
        if self.__api_version == "v1":
            # Clear out cookies, clears the auth token.
            url = urljoin(URL_BASE, URL_LOGIN)
        else:
            url = urljoin(URL_BASE_NEW, URL_LOGIN_NEW)

        try:
            response = await self.__session.post(
                url,
                data=self.__login_params,
                cookies={"PHPSESSID": "", "$version": "1"},
                headers={"content-type": "application/x-www-form-urlencoded"},
            )
        except ClientConnectionError as ex:
            _LOGGER.warning("Connection Error: %s", ex)
            raise MasterthermConnectionError("3", "Client Connection Error") from ex

        # Response shoudl always be 200 even for login failures
        if response.status != 200:
            error_msg = await response.text()
            _LOGGER.warning(
                "Site Error status=%s, Error=%s", response.status, error_msg
            )
            raise MasterthermConnectionError(str(response.status), error_msg)

        response_json = await response.json()

        # Separate process for Old and New API's
        if self.__api_version == "v1":
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

        return response_json

    def get_url(self) -> str:
        """Return the API URL Used.

        Returns:
            URL(str): The API URL for the version.

        """
        if self.__api_version == "v1":
            return URL_BASE
        else:
            return URL_BASE_NEW

    async def connect(self) -> dict:
        """Perform the connection to the Mastertherm API Server.

        Returns:
             devices (dict): Return the list of devices, modules and units.

        Raises:
            MasterthermConnectionError - Failed to Connect
            MasterthermAuthenticationError - Failed to Authenticate
            MasterthermUnsupportedRole - Role is not in supported roles

        """
        response_json = await self.__connect_refresh()
        if self.__api_version == "v2":
            # Get the Modules as this now has moved to outside of the auth process
            response_json = await self.__get(url=URL_MODULES_NEW, params=None)

        # Next is same for old and new process, doing a double check just incase
        if response_json["returncode"] != 0:
            raise MasterthermAuthenticationError(
                response_json["returncode"], response_json["message"]
            )

        # Check if role is supported
        if response_json["role"] not in SUPPORTED_ROLES:
            raise MasterthermUnsupportedRole(
                "2", "Unsupported Role " + response_json["role"]
            )

        return response_json

    async def get_device_info(self, module_id: str, unit_id: str) -> dict:
        """Get the Device information.

        Args:
            module_id: This is the module_id for the unit
            unit_id: This is the unit id for the unit

        Return:
            device_info (dict): Information for a specific device.

        Raises:
            MasterthermConnectionError - General Connection Issue
            MasterthermTokenInvalid - Token has expired or is invalid
            MasterthermResponseFormatError - Some other issue, probably temporary
            MasterthermServerTimeoutError - Server Timed Out more than once.

        """
        retry = False
        params = f"moduleid={module_id}&unitid={unit_id}&application=android"

        _LOGGER.info("Get Device Info %s:%s", module_id, unit_id)
        try:
            response_json = await self.__get(
                url=URL_PUMPINFO if self.__api_version == "v1" else URL_PUMPINFO_NEW,
                params=params,
            )
        except MasterthermTokenInvalid as ex:
            _LOGGER.info("Token Expired Early Retry: %s:%s", ex.status, ex.message)
            retry = True
            self.__expires = None
        except MasterthermServerTimeoutError as ex:
            _LOGGER.info("API Timed Out Retry: %s:%s", ex.status, ex.message)
            retry = True

        if retry:
            await asyncio.sleep(0.5)
            response_json = await self.__get(
                url=URL_PUMPINFO if self.__api_version == "v1" else URL_PUMPINFO_NEW,
                params=params,
            )

        return response_json

    async def get_device_data(
        self, module_id: str, unit_id: str, last_update_time: str = None
    ) -> dict:
        """Get the Device lastest data.

        Args:
            module_id: This is the module_id for the unit
            unit_id: This is the unit id for the unit
            last_update_time: Optional last update date in number format

        Return:
            device_data (dict): data or updated data for a specific device.

        Raises:
            MasterthermConnectionError - General Connection Issue
            MasterthermTokenInvalid - Token has expired or is invalid
            MasterthermResponseFormatError - Some other issue, probably temporary
            MasterthermPumpDisconnected - Pump is unavailable, disconnected or offline.
            MasterthermServerTimeoutError - Server Timed Out more than once.

        """
        retry = False
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

        _LOGGER.info("Get Device Data %s:%s", module_id, unit_id)
        try:
            response_json = await self.__get(
                url=URL_PUMPDATA if self.__api_version == "v1" else URL_PUMPDATA_NEW,
                params=params,
            )
        except MasterthermTokenInvalid as ex:
            _LOGGER.info("Token Expired Early Retrying: %s:%s", ex.status, ex.message)
            retry = True
            self.__expires = None
        except MasterthermServerTimeoutError as ex:
            _LOGGER.info("API Timed Out Retry: %s:%s", ex.status, ex.message)
            retry = True

        if retry:
            await asyncio.sleep(0.5)
            response_json = await self.__get(
                url=URL_PUMPDATA if self.__api_version == "v1" else URL_PUMPDATA_NEW,
                params=params,
            )

        # Check for Errors with the Pump.
        error_id = response_json["error"]["errorId"]
        if error_id != 0:
            raise MasterthermPumpError(error_id, response_json["error"]["errorMessage"])

        # No error process the response.
        if response_json["data"] != {}:
            data_file = ""
            if self.__api_version == "v1":
                if "varfile_mt1_config1" in response_json["data"]:
                    data_file = "varfile_mt1_config1"
                elif "varfile_mt1_config2" in response_json["data"]:
                    data_file = "varfile_mt1_config2"
            elif self.__api_version == "v2":
                data_file = "varFileData"

            response_json["data"]["varData"] = response_json["data"][data_file]
            del response_json["data"][data_file]

            # Sort the Data
            sorted_reg = {}
            device_reg = response_json["data"]["varData"][str(unit_id).zfill(3)]
            for key in natsorted(device_reg.keys()):
                sorted_reg[key] = device_reg[key]
            response_json["data"]["varData"][str(unit_id).zfill(3)] = sorted_reg

        return response_json

    async def set_device_data(
        self, module_id: str, unit_id: str, register: str, value: any
    ) -> bool:
        """Set device data a specific register to a specific value.

        Updating any registry setting can cause the system to stop working
        the controller only allows tested updates this API has no protection.

        Args:
            module_id: This is the module_id for the unit
            unit_id: This is the unit id for the unit
            register: The Register to update
            value: The value to set.

        Return:
           success (bool): return true if succes and false if not.

        Raises:
            MasterthermConnectionError - General Connection Issue
            MasterthermTokenInvalid - Token has expired or is invalid
            MasterthermResponseFormatError - Some other issue, probably temporary
            MasterthermServerTimeoutError - Server Timed Out more than once.

        """
        retry = False
        params = (
            f"moduleId={module_id}&deviceId={unit_id}&"
            + "configFile=varfile_mt1_config&messageId=1&errorResponse=true&"
            + f"variableId={register}&variableValue={value}&application=android"
        )

        _LOGGER.info("Set Device Reg %s:%s:%s:%s", module_id, unit_id, register, value)
        try:
            response_json = await self.__post(
                url=(
                    URL_POSTUPDATE if self.__api_version == "v1" else URL_POSTUPDATE_NEW
                ),
                params=params,
            )
        except MasterthermTokenInvalid as ex:
            _LOGGER.info("Token Expired Early Retrying: %s:%s", ex.status, ex.message)
            retry = True
            self.__expires = None
        except MasterthermServerTimeoutError as ex:
            _LOGGER.info("API Timed Out Retry: %s:%s", ex.status, ex.message)
            retry = True

        if retry:
            await asyncio.sleep(0.5)
            response_json = await self.__post(
                url=(
                    URL_POSTUPDATE if self.__api_version == "v1" else URL_POSTUPDATE_NEW
                ),
                params=params,
            )

        _LOGGER.info("Set Device Reg response: %s", response_json)

        # Check the response for any errors:
        if response_json["error"]["errorId"] != 0:
            _LOGGER.error(
                "Client Connection Error: %s, Message: %s",
                response_json["error"]["errorId"],
                response_json["error"]["errorMessage"],
            )
            return False

        # Get the Value that is returned and set.
        if self.__api_version == "v1":
            data_file = ""
            if "varfile_mt1_config1" in response_json["data"]:
                data_file = "varfile_mt1_config1"
            elif "varfile_mt1_config2" in response_json["data"]:
                data_file = "varfile_mt1_config2"

            set_value = response_json["data"][data_file][str(unit_id).zfill(3)][
                register
            ]
        else:
            set_value = response_json["data"]["data"][str(unit_id).zfill(3)][register]

        return set_value == value
