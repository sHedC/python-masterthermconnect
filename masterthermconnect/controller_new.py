"""Mastertherm Controller, for handling Mastertherm Data, local and api."""

import logging

from datetime import datetime, timedelta

from aiohttp import ClientSession

from .api import MasterthermAPI
from .modbus import MasterthermModbus

from .const import (
    CHAR_MAP,
    DEVICE_INFO_MAP,
    HC_MAP,
)
from .datamapread import DEVICE_READ_MAP, DEVICE_READ_HCMAP
from .datamapwrite import DEVICE_WRITE_MAP
from .exceptions import MasterthermEntryNotFound, MasterthermPumpError
from .special import Special
from .__version__ import __version__

_LOGGER: logging.Logger = logging.getLogger(__package__)


class MasterthermController:
    """Mastertherm Integration Contoller."""

    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession,
        api_version: str = "v1",
        device_list: dict[str, any] | None = None,
    ) -> None:
        """Initialize the MasterthermController and connection to the web API.

        Args:
            username: The mastertherm login username
            password: The mastertherm login password
            session: An aiohttp Client Session
            api_version: The version of the API, mainly the host
                "v1"  : Original version, data response in varfile_mt1_config1
                "v1b" : Original version, datalast_info_update response in varfile_mt1_config2
                "v2"  : New version since 2022 response in varFileData
            device_list: An optional list of pre-loaded devices to populate.

        Returns:
            The MasterthermController object

        Raises:
            MasterthermUnsupportedVersion: API Version is not supported.

        """
        self.__api = MasterthermAPI(
            username, password, session, api_version=api_version
        )
        self.__api_connected = False
        self.__info_update_min = None
        self.__data_update_sec = None
        self.__data_offset_sec = None
        self.__local_refresh_sec = None
        self.__full_refresh_min = None
        self.set_refresh_rate()

        # The device structure is held as a dictionary with the following format:
        # {
        #   "module_id_unit_id": {
        #       "last_data_update": <datetime>,
        #       "last_info_update": <datetime>,
        #       "last_full_load": <datetime>,
        #       "last_update_time": "1192282722",
        #       "active": True | False,
        #       "connection": "local | api",
        #       "ip_address": "10.0.0.20",
        #       "info": { Various Information},
        #       "data": { Normalized Data Information },
        #       "api_info": { All Info retrieved from the API },
        #       "api_update_data": { All Updated Data since last update },
        #       "api_full_data": { Full Data including last updated },
        #   }
        # }
        self.__devices = {}

        # If we have initial data, pre-populate the devices:
        if device_list:
            for device_id, device in device_list:
                self.__devices[device_id] = {
                    "last_update_time": "0",
                    "active": True,
                    "connection": device["connection"],
                    "ip_address": device["ip_address"],
                    "info": device["info"],
                    "data": device["data"],
                    "api_info": device["api_info"],
                    "api_update_data": {},
                    "api_full_data": device["api_data"],
                }

    def set_refresh_rate(
        self,
        info_refresh_minutes: int = -1,
        local_refresh_seconds: int = -1,
        data_refresh_seconds: int = -1,
        data_offset_seconds: int = -1,
        full_refresh_minutes: int = -1,
    ) -> None:
        """Set the Refresh Rates allowed.

        caution should be taken as too frequent requests could  cause lock-out on the new servers.
        Additionally the system seems not to update less than 30s.

        Updating these does not change how much you can call the refresh just how frequently it will
        reach out to the servers to update.

        Args:
            info_refresh_minutes: Default is 30 minutes, delay between refresh of info
            local_refresh_seconds: Defauls is 30 seconds, delay between refresh of local data
            data_refresh_seconds: Default is 60 seconds, delay between refresh of data
            data_offset_seconds: Default is 0, offset in the past from last update time
            full_refresh_minutes: Default is 15, minutes between doing updates and full data refresh.

        """
        if info_refresh_minutes < 0:
            if self.__info_update_min is None:
                self.__info_update_min = 30
        else:
            self.__info_update_min = info_refresh_minutes
        if local_refresh_seconds < 0:
            if self.__local_refresh_sec is None:
                self.__local_refresh_sec = 30
        else:
            self.__full_refresh_min = full_refresh_minutes
        if data_refresh_seconds < 0:
            if self.__data_update_sec is None:
                self.__data_update_sec = 60
        else:
            self.__data_update_sec = data_refresh_seconds
        if data_offset_seconds < 0:
            if self.__data_offset_sec is None:
                self.__data_offset_sec = 0
        else:
            self.__data_offset_sec = data_offset_seconds
        if full_refresh_minutes < 0:
            if self.__full_refresh_min is None:
                self.__full_refresh_min = 15
        else:
            self.__full_refresh_min = full_refresh_minutes

    async def connect(self, reload_modules: bool = False) -> bool:
        """Connect to the API, check the supported roles and update if required.

        Args:
            reload_modules: Optional, default False, True to reload modules.

        Returns:
            connected (bool): True if connected Raises Error if not

        Raises:
            MasterthermConnectionError: Failed to Connect
            MasterthermAuthenticationError: Failed to Authenticate
            MasterthermUnsportedRole: Role is not supported by API
            MasterthermServerTimeoutError: Server Timed Out more than once.

        """
        result = await self.__api.connect()

        if not self.__devices or reload_modules:
            # Mark all existing devices as inactive
            for device_id, _ in self.__devices:
                self.__devices[device_id]["active"] = False

            # Reload or Create Devices
            for module in result["modules"]:
                for unit in module["config"]:
                    device_id = module["id"] + "_" + str(unit["mb_addr"])

                    if device_id in self.__devices:
                        self.__devices["last_update_time"] = "0"
                        self.__devices[device_id]["active"] = True
                        self.__devices[device_id]["info"]["module_name"] = module[
                            "module_name"
                        ]
                        self.__devices[device_id]["info"]["unit_name"] = module[
                            "unit_name"
                        ]
                    else:
                        self.__devices[device_id] = {
                            "last_update_time": "0",
                            "active": True,
                            "connection": "api",
                            "ip_address": "",
                            "info": {
                                "module_id": module["id"],
                                "module_name": module["module_name"],
                                "unit_id": str(unit["mb_addr"]),
                                "unit_name": unit["mb_name"],
                            },
                            "data": {},
                            "api_info": {},
                            "api_update_data": {},
                            "api_full_data": {},
                        }

        self.__api_connected = True
        return self.__api_connected

    async def get_info(self) -> bool:
        """Refresh the data."""
        return

    async def refresh_data(self, full_load: bool = False) -> bool:
        """Refresh data and information for all the devices.

        Info refresh is restricted to protect against too many calls.
        Calling this functions should not happen more than every minute, may cause lockout.

        Updated to allow for refresh when API is not online and to add local refresh.

        Args:
            full_load: Optional Force a full load of the data, defaultis false

        Returns:
            success (bool): true if loaded

        Raises:
            MasterthermConnectionError: Failed to Connect
            MasterthermNotReady: Failed to complete first full import
            MasterthermAuthenticationError: Failed to Authenticate
            MasterthermUnsupportedRole: Role is not in supported roles
            MasterthermServerTimeoutError: Server Timed Out more than once.

        """

        # Go through the devices anre fresh as required.
        for device_id, device in self.__devices.items():
            device_active: bool = device["active"]
            connection_type = device["connection"]
            device_ip = device["ip_address"]

        return True
