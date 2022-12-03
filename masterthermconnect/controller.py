"""Mastertherm Controller, for handling Mastertherm Data."""
import logging

from datetime import datetime, timedelta

from aiohttp import ClientSession

from .api import MasterthermAPI
from .const import (
    CHAR_MAP,
    DEVICE_DATA_MAP,
    DEVICE_DATA_HCMAP,
    DEVICE_INFO_MAP,
    HC_MAP,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)


class MasterthermController:
    """Mastertherm Integration Contoller."""

    def __init__(
        self,
        username: str,
        password: str,
        session: ClientSession,
        api_version: str = "v1",
    ) -> None:
        """Initialize the MasterthermController and connection to the web API.

        Parameters:
            username (str): The mastertherm login username
            password (str): The mastertherm login password
            session (ClientSession): An aiohttp Client Session
            api_version (str): The version of the API, mainly the host
                "v1"  : Original version, data response in varfile_mt1_config1
                "v1b" : Original version, datalast_info_update response in varfile_mt1_config2
                "v2"  : New version since 2022 response in varFileData

        Return:
            The MasterthermController object

        Raises:
            MasterthermUnsupportedVersion: API Version is not supported."""
        self.__api = MasterthermAPI(
            username, password, session, api_version=api_version
        )
        self.__device_map = DEVICE_DATA_MAP
        self.__api_connected = False
        self.__info_update_minutes = 30
        self.__data_update_seconds = 60

        # The device structure is held as a dictionary with the following format:
        # {
        #   "module_id_unit_id": {
        #       "last_data_update": <datetime>,
        #       "last_info_update": <datetime>,
        #       "last_update_time": "1192282722"
        #       "info": { Various Information },
        #       "data": { Normalized Data Information },
        #       "api_info": { All Info retrieved from the API },
        #       "api_update_data": { All Updated Data since last update },
        #       "api_full_data": { Full Data including last updated },
        #   }
        # }
        self.__devices = {}

    def __populate_data(self, device_map, registers) -> dict:
        """Populate the Data from the api_full_data and DeviceMap."""
        data = {}
        for key, item in device_map.items():
            if not isinstance(item, dict):
                item_type = item[0]
                item_value = item[1]
                if item_type == "fixed":
                    data[key] = item_value
                elif item_type == "bool":
                    if item_value == "":
                        data[key] = False
                    else:
                        data[key] = registers[item_value] == "1"
                elif item_type == "float":
                    if item_value == "":
                        data[key] = 0.0
                    else:
                        data[key] = float(registers[item_value])
                elif item_type == "int":
                    if item_value == "":
                        data[key] = 0
                    else:
                        data[key] = int(registers[item_value])
                elif item_type == "string":
                    if item_value == "":
                        data[key] = ""
                    else:
                        item_str = ""
                        for list_value in item_value:
                            item_str = item_str + CHAR_MAP[int(registers[list_value])]
                        data[key] = item_str
            else:
                data[key] = self.__populate_data(device_map[key], registers)

        return data

    def __get_hc_name(self, hc_id: int, device_key: str) -> str:
        """Build the Heating Cooling Circuit Name from the full data."""
        if HC_MAP[hc_id]["id"] not in DEVICE_DATA_HCMAP:
            return "0"

        hc_name = ""
        hc_empty = ""
        full_data = self.__devices[device_key]["api_full_data"]

        # Get the Name from the api data.
        for key in DEVICE_DATA_HCMAP[HC_MAP[hc_id]["id"]]["name"][1]:
            hc_name = hc_name + CHAR_MAP[int(full_data[key])]
            hc_empty = hc_empty + "-"

        # Empty Names return "0"
        if hc_name == hc_empty:
            hc_name = ""

        return hc_name

    def __hc_enabled(self, device_key: str) -> dict:
        """Enable the Pads for the devices, decoded as best as possible."""
        full_data = self.__devices[device_key]["api_full_data"]
        hc_info = {}

        # The following check_code is used to deal with some legacy types
        version = int(full_data["I_104"])
        if version < 11:
            version = 10
        else:
            if version <= 200:
                version = 11

        # HC's 1 to 6 are enabled if check based on the Check Code
        # the name being available and the relevant register.
        hc_optional_enabled = False
        for i in range(1, 7):
            hc_name = self.__devices[device_key]["info"][HC_MAP[i]["pad"]]
            hc_info[HC_MAP[i]["id"]] = "" != hc_name and (
                version < 11 or "1" == full_data[HC_MAP[i]["register"]]
            )
            hc_optional_enabled = hc_optional_enabled or hc_info[HC_MAP[i]["id"]]

        # TODO: Enabled/ Disable Solar and Pool
        #    return "1" == this.namedVars.solarenabled_v
        #    return "1" == this.namedVars.poolenabled_v

        # Check HC 0 to see if it is enabled.
        hc_name = self.__devices[device_key]["info"][HC_MAP[0]["pad"]]
        hc_info[HC_MAP[0]["id"]] = False
        if hc_name != "":
            if version < 11:
                hc_info[HC_MAP[0]["id"]] = (
                    full_data[HC_MAP[0]["register"]] == "1"
                    and float(full_data["A_190"]) >= 0.1
                )
            else:
                hc_info[HC_MAP[0]["id"]] = not hc_optional_enabled

        return hc_info

    async def __get_hp_updates(self, full_load: bool = False) -> None:
        """Refresh data and information for all the devices, apply default restrictions to
               the number of times a call can be made..

               Parameters:
                   full_load: Optional Force a full load of the data, defaultis false
        gd
               Raises
                   MasterthermConnectionError - Failed to Connect
                   MasterthermAuthenticationError - Failed to Authenticate
                   MasterthermUnsupportedRole - Role is not in supported roles"""
        for device in self.__devices.values():
            module_id = device["info"]["module_id"]
            unit_id = device["info"]["unit_id"]

            # Refresh the Device Information, refresh rate of this data is restricted
            # as the new servers are sensitive to number of requests.
            last_info_update = None
            if "last_info_update" in device:
                last_info_update = device["last_info_update"]

            if (
                last_info_update is None
                or datetime.now()
                >= last_info_update + timedelta(minutes=self.__info_update_minutes)
            ):
                device_info = await self.__api.get_device_info(module_id, unit_id)
                if device_info["returncode"] == "0":
                    device["last_info_update"] = datetime.now()
                    device["api_info"] = device_info

            # Refresh the Device Data, refresh rate of this data is restricted by default
            # to try and keep frequency of requests down.all(iterable)
            last_data_update = None
            if "last_data_update" in device and not full_load:
                last_data_update = device["last_data_update"]

            if (
                last_data_update is None
                or datetime.now()
                >= last_data_update + timedelta(seconds=self.__data_update_seconds)
            ):
                # Refresh Device Data.
                device_data = await self.__api.get_device_data(
                    module_id, unit_id, last_update_time=device["last_update_time"]
                )
                device["last_data_update"] = datetime.now()

                # Check that we have data, sometimes nothing is returned.
                if device_data["data"]:
                    device["last_update_time"] = device_data["timestamp"]
                    device["api_update_data"] = device_data["data"]["varData"][
                        "001"
                    ].copy()
                    device["api_full_data"].update(device["api_update_data"])

    async def connect(self, reload_modules: bool = False) -> bool:
        """Connect to the API, check the supported roles and update if required.

        Parameters:
            reload_modules (bool): Optional, default False, True to reload modules.

        Returns:
            connected (bool): True if connected Raises Error if not

        Raises:
            MasterthermConnectionError - Failed to Connect
            MasterthermAuthenticationError - Failed to Authenticate
            MasterthermUnsportedRole - Role is not supported by API"""
        result = await self.__api.connect()

        # Initialize the Dictionary.
        if not self.__devices or reload_modules:
            self.__devices = {}
            for module in result["modules"]:
                for unit in module["config"]:
                    device_id = module["id"] + "_" + str(unit["mb_addr"])

                    self.__devices[device_id] = {
                        "last_update_time": "0",
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

    def set_refresh_rate(
        self, info_refresh_minutes: int = 30, data_refresh_seconds: int = 60
    ) -> None:
        """Set the Refresh Rates allowed, caution should be taken as too frequent requests
        could  cause lock-out on the new servers. Additionally the system seems not to update
        less than 30s.

        Updating these does not change how much you can call the refresh just how frequently it will
        reach out to the servers to update.

        Parameters:
            info_refresh_minutes - The refresh rate in minutes default is 30, should be left
            data_refresh_seconds - Default is 60 seconds but could be reducded with care."""
        self.__info_update_minutes = info_refresh_minutes
        self.__data_update_seconds = data_refresh_seconds

    async def refresh(self, full_load: bool = False) -> bool:
        """Refresh data and information for all the devices, info refresh is restricted
        to protect against too many calls.

        Calling this functions should not happen more than every minute, may cause lockout.

        Parameters:
            full_load: Optional Force a full load of the data, defaultis false

        Returns:
            success (bool): true if loaded

        Raises
            MasterthermConnectionError - Failed to Connect
            MasterthermNotReady - Failed to complete first full import
            MasterthermAuthenticationError - Failed to Authenticate
            MasterthermUnsupportedRole - Role is not in supported roles"""
        if not self.__api_connected:
            return False

        # Refresh the raw data if needed.
        await self.__get_hp_updates(full_load=full_load)

        # Refresh the data and check that there is both info and data to continue.
        for device_id, device in self.__devices.items():
            device_info = device["api_info"]

            # Populate Info
            for key, item in DEVICE_INFO_MAP.items():
                # Map the info from the API output
                if item in device_info:
                    device["info"][key] = device_info[item]

            # Populate Device Data
            device["data"] = self.__populate_data(
                self.__device_map, device["api_full_data"]
            )

            # Check the Pad Names, if blank get them from the data
            # Populate all data correctly.
            for hc_id in range(0, 7):
                hc_key = HC_MAP[hc_id]["id"]
                hc_pad = HC_MAP[hc_id]["pad"]

                if device["api_info"][hc_pad] in ("", "0"):
                    device["info"][hc_pad] = self.__get_hc_name(hc_id, device_id)

                if device["info"][hc_pad] in ("", "0"):
                    device["info"][hc_pad] = HC_MAP[hc_id]["default"]

                device["data"]["heating_circuits"][hc_key]["name"] = device["info"][
                    hc_pad
                ]

            # Set if circuits are enabled or not
            hc_enabled_result = self.__hc_enabled(device_id)
            hc_circuits = self.__devices[device_id]["data"]["heating_circuits"]
            for hc_id, hc_enabled in hc_enabled_result.items():
                hc_circuits[hc_id]["enabled"] = hc_enabled

        return True

    def get_devices(self) -> dict:
        """Return a List of the Devices with plus information.

        Returns:
            devices (dict): All the devices associated with the login"""
        device_return = {}
        for device_id, device in self.__devices.items():
            device_return[device_id] = device["info"]

        return device_return

    def get_device_info(self, module_id, unit_id) -> dict:
        """Get the Information for a specific device.

        Parameters:
            module_id (str): The id of the module
            unit_id (str): the id fo the unit

        Returns:
            info (dict): Device information."""
        info = {}
        key = module_id + "_" + unit_id
        if key in self.__devices:
            info = self.__devices[key]["info"]

        return info

    def get_device_registers(self, module_id, unit_id, last_updated=False) -> dict:
        """Get the Device Register Data, if lastUpdated is True then get the latest update data.

        Parameters:
            module_id (str): The id of the module
            unit_id (str): the id fo the unit
            last_updated (bool): Optional, true to return all data

        Returns:
            data (dict): Device Raw Data or Updated Data."""
        data = {}
        key = module_id + "_" + unit_id
        if key in self.__devices:
            if last_updated:
                data = self.__devices[key]["api_update_data"]
            else:
                data = self.__devices[key]["api_full_data"]

        return data

    def get_device_data(self, module_id, unit_id) -> dict:
        """Get the Device Data, if lastUpdated is True then get the latest update data.
        Parameters:
            module_id (str): The id of the module
            unit_id (str): the id fo the unit

        Returns:
            data (dict): Device Normalised Data."""
        data = {}
        key = module_id + "_" + unit_id
        if key in self.__devices:
            data = self.__devices[key]["data"]

        return data
