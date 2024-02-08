"""Mastertherm Controller, for handling Mastertherm Data."""

import logging

from datetime import datetime, timedelta

from aiohttp import ClientSession

from .api import MasterthermAPI
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
        self.__full_refresh_min = None
        self.set_refresh_rate()

        # The device structure is held as a dictionary with the following format:
        # {
        #   "module_id_unit_id": {
        #       "last_data_update": <datetime>,
        #       "last_info_update": <datetime>,
        #       "last_full_load": <datetime>,
        #       "last_update_time": "1192282722"
        #       "info": { Various Information },
        #       "data": { Normalized Data Information },
        #       "api_info": { All Info retrieved from the API },
        #       "api_update_data": { All Updated Data since last update },
        #       "api_full_data": { Full Data including last updated },
        #   }
        # }
        self.__devices = {}

    def __convert_data(self, item_type, item_value, registers) -> any:
        """Convert the data for use with Populate Data."""
        return_value: any = None

        if isinstance(item_type, Special):
            # Handle Special Types
            special_item: Special = item_type

            if special_item.condition == Special.FIXED:
                return_value = special_item.data_type(item_value)
            elif special_item.condition == Special.NAMEARRAY:
                item_str = ""
                for list_value in item_value:
                    item_str = item_str + CHAR_MAP[int(registers[list_value])]
                return_value = item_str
            elif special_item.condition == Special.FORMULA:
                values = []
                for item in item_value[1]:
                    # Bool needs to converted as an int not string
                    if item[0] == bool:
                        values.append(item[0](int(registers[item[1]])))
                    else:
                        values.append(item[0](registers[item[1]]))

                return_value = special_item.evaluate(item_value[0], values)
        else:
            # Convert Simple Types
            # Bool needs to converted as an int not string
            if item_type == bool:
                return_value = item_type(int(registers[item_value]))
            else:
                return_value = item_type(registers[item_value])

        return return_value

    def __populate_data(self, device_map, registers) -> dict:
        """Populate the Data from the api_full_data and DeviceMap."""
        data = {}
        for key, item in device_map.items():
            if not isinstance(item, dict):
                data[key] = self.__convert_data(item[0], item[1], registers)
            else:
                data[key] = self.__populate_data(device_map[key], registers)

        return data

    def __get_hc_name(self, hc_id: int, device_key: str) -> str:
        """Build the Heating Cooling Circuit Name from the full data."""
        if HC_MAP[hc_id]["id"] not in DEVICE_READ_HCMAP:
            return "0"

        hc_name = ""
        hc_empty = ""
        full_data = self.__devices[device_key]["api_full_data"]

        # Get the Name from the api data.
        for key in DEVICE_READ_HCMAP[HC_MAP[hc_id]["id"]]["name"][1]:
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
            hc_info[HC_MAP[i]["id"]] = hc_name != "" and (
                version < 11 or full_data[HC_MAP[i]["register"]] == "1"
            )
            hc_optional_enabled = hc_optional_enabled or hc_info[HC_MAP[i]["id"]]

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
        """Refresh data and information for all the devices.

        apply default restrictions to the number of times a call can be made..

        Args:
            full_load: Optional Force a full load of the data, defaultis false

        Raises:
            MasterthermConnectionError: Failed to Connect
            MasterthermAuthenticationError: Failed to Authenticate
            MasterthermUnsupportedRole: Role is not in supported roles
            MasterthermServerTimeoutError: Server Timed Out more than once.

        """
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
                >= last_info_update + timedelta(minutes=self.__info_update_min)
            ):
                device_info = await self.__api.get_device_info(module_id, unit_id)
                if device_info["returncode"] == "0":
                    device["last_info_update"] = datetime.now()
                    device["api_info"] = device_info

            # Refresh the Device Data, refresh rate of this data is restricted by default
            # to try and keep frequency of requests down.all(iterable)
            last_data_update = None
            last_update_time = 0

            # Check to see if full data load is required.
            if "last_full_load" in device:
                last_full_load = device["last_full_load"]

                if datetime.now() >= last_full_load + timedelta(
                    minutes=self.__full_refresh_min
                ):
                    full_load = True
            else:
                full_load = True

            if "last_data_update" in device and not full_load:
                last_data_update = device["last_data_update"]
                last_update_time = device["last_update_time"]
                last_update_time = last_update_time - self.__data_offset_sec

            if (
                last_data_update is None
                or datetime.now()
                >= last_data_update + timedelta(seconds=self.__data_update_sec)
            ):
                try:
                    # Refresh Device Data.
                    device_data = await self.__api.get_device_data(
                        module_id, unit_id, last_update_time=last_update_time
                    )
                    device["last_data_update"] = datetime.now()
                    device["data"]["operating_mode"] = "online"

                    # Check that we have data, sometimes nothing is returned.
                    if device_data["data"]:
                        device["last_update_time"] = device_data["timestamp"]
                        if full_load:
                            device["last_full_load"] = datetime.now()

                        device["api_update_data"] = device_data["data"]["varData"][
                            str(unit_id).zfill(3)
                        ].copy()
                        device["api_full_data"].update(device["api_update_data"])

                except MasterthermPumpError as mpe:
                    if mpe.status == MasterthermPumpError.OFFLINE:
                        device["data"]["operating_mode"] = "offline"
                    else:
                        raise MasterthermPumpError(mpe.status, mpe.message) from mpe

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
        self,
        info_refresh_minutes: int = -1,
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
            data_refresh_seconds: Default is 60 seconds, delay between refresh of data
            data_offset_seconds: Default is 0, offset in the past from last update time
            full_refresh_minutes: Default is 15, minutes between doing updates and full data refresh.

        """
        if info_refresh_minutes < 0:
            if self.__info_update_min is None:
                self.__info_update_min = 30
        else:
            self.__info_update_min = info_refresh_minutes
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

    async def refresh(self, full_load: bool = False) -> bool:
        """Refresh data and information for all the devices.

        Info refresh is restricted to protect against too many calls.
        Calling this functions should not happen more than every minute, may cause lockout.

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

            # Add some additional details to the info such as URL
            device["info"]["api_url"] = self.__api.get_url()
            device["info"]["version"] = __version__

            if device["data"]["operating_mode"] != "offline":
                # Populate Device Data
                device["data"] = self.__populate_data(
                    DEVICE_READ_MAP, device["api_full_data"]
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

                # Disable certain fields if Cooling Mode is disabled
                cooling_disabled = device["info"]["cooling"] != "1"
                if cooling_disabled:
                    device["data"].pop("hp_function")
                    device["data"].pop("control_curve_cooling")

                # Set if circuits are enabled or not, remove circuts that
                # are not enabled.
                hc_enabled_result = self.__hc_enabled(device_id)
                hc_circuits: dict = self.__devices[device_id]["data"][
                    "heating_circuits"
                ]
                for hc_id, hc_enabled in hc_enabled_result.items():
                    if not hc_enabled:
                        hc_circuits.pop(hc_id)
                    else:
                        hc_circuits[hc_id]["enabled"] = hc_enabled
                        if not hc_circuits[hc_id]["pad"]["enabled"]:
                            hc_circuits[hc_id].pop("pad")

                        if (
                            cooling_disabled
                            and "control_curve_cooling" in hc_circuits[hc_id]
                        ):
                            hc_circuits[hc_id].pop("control_curve_cooling")

                # Check if the Pool and Solar are enabled
                if not hc_circuits["solar"]["enabled"]:
                    hc_circuits.pop("solar")
                if not hc_circuits["pool"]["enabled"]:
                    hc_circuits.pop("pool")

                # Remove the Domestic Hot Water if the feature is disabled.
                if not self.__devices[device_id]["data"]["domestic_hot_water"][
                    "enabled"
                ]:
                    self.__devices[device_id]["data"].pop("domestic_hot_water")

                # Filter the Fan/ Brine and Water Pumps based on HP Type
                # 0=A/W, 1=B/W, 2=W/W, 3=DX/W, 4=A/W R, 5=B/W R, 6=W/W R
                data = self.__devices[device_id]["data"]
                hp_type = data["hp_type"]
                if hp_type not in [0, 4]:
                    data.pop("fan_running")
                if hp_type not in [1, 2, 3, 5, 6]:
                    data.pop("brine_pump_running")

        return True

    def get_devices(self) -> dict:
        """Return a List of the Devices with plus information.

        Returns:
            devices (dict): All the devices associated with the login

        """
        device_return = {}
        for device_id, device in self.__devices.items():
            device_return[device_id] = device["info"]

        return device_return

    def get_device_info(self, module_id, unit_id) -> dict:
        """Get the Information for a specific device.

        Args:
            module_id: The id of the module
            unit_id: the id fo the unit

        Returns:
            info (dict): Device information.

        """
        info = {}
        key = module_id + "_" + unit_id
        if key in self.__devices:
            info = self.__devices[key]["info"]

        return info

    def get_device_registers(self, module_id, unit_id, last_updated=False) -> dict:
        """Get the Device Register Data, if lastUpdated is True then get the latest update data.

        Args:
            module_id: The id of the module
            unit_id: the id fo the unit
            last_updated: Optional, true to return all data

        Returns:
            data (dict): Device Raw Data or Updated Data.

        """
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

        Args:
            module_id: The id of the module
            unit_id: the id fo the unit

        Returns:
            Device Normalised Data.

        """
        data = {}
        key = module_id + "_" + unit_id
        if key in self.__devices:
            data = self.__devices[key]["data"]

        return data

    def get_device_data_item(self, module_id: str, unit_id: str, entry: str) -> any:
        """Get the Device Data Item based on the dot notation.

        Args:
            module_id: The id of the module
            unit_id:   The id of the unit
            entry:     The entry to using dot notation, e.g. hp_power_state
                       or heating_circuits.hc0.on

        Returns:
            any: Returns the value of the item found

        Raises:
            MasterthermEntryNotFound - Entry is not valid.

        """
        data = self.get_device_data(module_id, unit_id)

        keys: list[str] = entry.split(".")
        for i in range(len(keys) - 1):
            if keys[i] in data:
                data = data[keys[i]]
            else:
                raise MasterthermEntryNotFound(
                    "401", f"{keys[i]} in {entry} not found."
                )

        item = keys[len(keys) - 1]
        if item not in data:
            raise MasterthermEntryNotFound("401", f"{item} in {entry} not found.")

        return data[item]

    def get_diagnostics_data(self, hide_sensitive: bool = True) -> dict:
        """Get full diagnostics data hiding sensitive information by default.

        Args:
            hide_sensitive: Default True, if False then sensitive information is shown.

        Returns:
            dict: Returns a dict of all the data for all modules.

        """
        diagnostics_data = {}
        new_module_id = 1111
        old_module_id = ""

        for device_id, device_item in self.__devices.items():
            module_id = device_item["info"]["module_id"]
            unit_id = device_item["info"]["unit_id"]

            if module_id != old_module_id:
                old_module_id = module_id
                new_module_id = new_module_id + 1

            info = device_item["info"].copy()
            api_info = device_item["api_info"].copy()

            if hide_sensitive:
                device_id = f"{str(new_module_id)}_{unit_id}"
                info["module_id"] = str(new_module_id)
                info["module_name"] = "REDACTED"
                info["name"] = "REDACTED"
                info["surname"] = "REDACTED"
                info["latitude"] = "REDACTED"
                info["longitude"] = "REDACTED"
                info["place"] = "REDACTED"
                info["notes"] = "REDACTED"

                api_info["moduleid"] = str(new_module_id)
                api_info["module_name"] = "REDACTED"
                api_info["givenname"] = "REDACTED"
                api_info["surname"] = "REDACTED"
                api_info["password8"] = "REDACTED"
                api_info["password9"] = "REDACTED"
                api_info["password10"] = "REDACTED"
                api_info["city"] = "REDACTED"
                api_info["notes"] = "REDACTED"

                # Version 2 API Information.
                if "location" in api_info:
                    api_info["location"] = "REDACTED"
                    api_info["latitude"] = "REDACTED"
                    api_info["longitude"] = "REDACTED"

            diagnostics_data[device_id] = {
                "info": info,
                "data": device_item["data"].copy(),
                "api_info": api_info,
                "api_data": device_item["api_full_data"].copy(),
            }

        return diagnostics_data

    async def set_device_data_item(
        self, module_id: str, unit_id: str, entry: str, value: any
    ) -> bool:
        """Set the Device Data and Update to the Mastertherm Heat Pump.

        Args:
            module_id: The id of the module
            unit_id:   The id of the unit
            entry:     The entry to using dot notation, e.g. hp_power_state
                       or heating_circuits.hc0.on
            value:     The value to set should be bool, str, float or int

        Returns:
            bool: True if success, False if failure

        Raises:
            MasterthermConnectionError - Failed to Connect
            MasterthermAuthenticationError - Failed to Authenticate
            MasterthermEntryNotFound - Entry is not valid.
            MasterthermServerTimeoutError - Server Timed Out more than once.

        """
        # Split the entry into its components and find the mapping and data type.
        # Check if in both read and write map, if not in both stop.
        write_map = DEVICE_WRITE_MAP
        device_data = self.get_device_data(module_id, unit_id)
        keys: list[str] = entry.split(".")
        for i in range(len(keys) - 1):
            if keys[i] in write_map and keys[i] in device_data:
                write_map = write_map[keys[i]]
                device_data = device_data[keys[i]]
            else:
                raise MasterthermEntryNotFound(
                    "401", f"{keys[i]} in {entry} not found."
                )

        # Make sure the item is valid the start processing.
        item = keys[len(keys) - 1]
        if item not in write_map or item not in device_data:
            raise MasterthermEntryNotFound("401", f"{item} in {entry} not found.")

        # Get the Registry to set and prepare the value.
        entry_type = write_map[item][0]
        entry_value = write_map[item][1]
        entry_reg = ""

        registers = self.get_device_registers(module_id, unit_id)

        if isinstance(entry_type, Special):
            # If Special then find the Registry Entry.
            special_item: Special = entry_type
            if special_item.condition == Special.FORMULA:
                values = []
                for item in entry_value[1]:
                    if item[0] == bool:
                        values.append(item[0](int(registers[item[1]])))
                    else:
                        values.append(item[0](registers[item[1]]))

                entry_reg = special_item.evaluate(entry_value[0], values)
                entry_type = special_item.data_type
            else:
                return False
        else:
            # If Normal just set it from the Value
            entry_reg = entry_value

        _LOGGER.info(
            "Set module %s:%s property: %s, register: %s, value: %s",
            module_id,
            unit_id,
            entry,
            entry_reg,
            value,
        )

        # Test if the entry_type matches our value type.
        if isinstance(value, entry_type):
            if isinstance(value, bool):
                entry_value = str(int(value))
            else:
                entry_value = str(value)
        else:
            return False

        # Set the data
        set_success = await self.__api.set_device_data(
            module_id, unit_id, entry_reg, entry_value
        )
        if set_success:
            registers[entry_reg] = entry_value

        return set_success
