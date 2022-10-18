"""MasterTherm Controller, for handling MasterTherm Data."""
import logging

from .connection import Connection
from .const import (
    CHAR_MAP,
    DEVICE_DATA_MAP,
    DEVICE_DATA_PADMAP,
    DEVICE_INFO_MAP,
    DEVICE_SWITCH_MAP,
    PAD_MAP,
    SUPPORTED_ROLES,
)
from .exceptions import MasterThermUnsupportedRole

_LOGGER = logging.getLogger(__name__)

class Controller:
    """Mastertherm Connect Object."""

    def __init__(self, websession, username, password):
        """Initialize the Connection Object."""
        self.__api = Connection(websession, username, password)
        self.__device_map = None
        self.__inverted_map = None
        self.__role = ""
        self.__data_loaded = False

        # The device structure is held as a dictionary with the following format:
        # {
        #   "id-mb_addr": {
        #       "lastUpdateTime": "1234567890",
        #       "info": { Various Information },
        #       "data": { Normalized Data Information }
        #       "updatedData": { All Updated Data since last update },
        #       "fullData": { Full Data including last updated },
        #   }
        # }
        self.__devices = {}

    def __invert_device_map(self, device_map, key_list = None):
        """Invert the given map and return, this is a nested method."""

        if key_list is None:
            key_list = []

        inverted_map = {}
        for key, item in device_map.items():
            new_key_list = key_list.copy()
            new_key_list.append(key)
            if not isinstance(item,dict):
                item_value = item[1]
                if isinstance(item_value,list):
                    for list_value in item_value:
                        inverted_map[list_value] = new_key_list
                else:
                    item_type = item[0]
                    if not (item_value == "" or item_type == "fixed"):
                        inverted_map[item_value] = new_key_list
            else:
                inverted_map.update(self.__invert_device_map(item, new_key_list))

        return inverted_map

    def __populate_data(self, device_map, registers):
        """Populate the Data from the fullData and DeviceMap."""
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
                        data[key] = (registers[item_value] == "1")
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

    def __get_pad_name(self, pad, device_key):
        """Build the Pad Name from the full data."""
        if pad not in DEVICE_DATA_PADMAP:
            return "0"

        pad_name = ""
        pad_empty = ""
        full_data = self.__devices[device_key]["fullData"]
        for key in DEVICE_DATA_PADMAP[pad]["name"][1]:
            pad_name = pad_name + CHAR_MAP[int(full_data[key])]
            pad_empty = pad_empty + "-"

        if pad_name == pad_empty:
            pad_name = "0"
        return pad_name

    def __enabled_pads(self, device_key):
        """Enable the Pads for the devices, decoded as best as possible."""
        full_data = self.__devices[device_key]["fullData"]
        pad_info = {}

        # Pad 0 and 1 I believe are the Main Heating and Cooling circuites
        # I have heating enabled and cooling disabled but both show disabled.
        # TODO: Check what happens if I enable/ Disable what registers get updated.
        for i in range(2):
            pad_info[PAD_MAP[i]] = (full_data[DEVICE_SWITCH_MAP[i]] == "1")

        # Following Code is to manage Switch Pad a to f which
        # these are various typs of circuites Water Heating/ Thermal etc.
        # TODO: see if we can identify where the types are stored.

        # Used in the process of Enabling/ Disabling Pads.
        check_code = int(full_data["I_104"])
        if check_code < 11:
            check_code = 10
        else:
            if check_code <= 200:
                check_code = 11

        # Setup and Enable Pad a to f
        for i in range(2,8):
            pad_name = self.__get_pad_name(PAD_MAP[i], device_key)
            if pad_name != "0" and check_code >= 11:
                pad_info[PAD_MAP[i]] = (full_data[DEVICE_SWITCH_MAP[i]] == "1")
            else:
                pad_info[PAD_MAP[i]] = False

        # Pad Switch 8, no idea where a name comes from so its always disabled.
        # maby its SOLAR?
        pad_name = self.__get_pad_name(PAD_MAP[8], device_key)
        pad_info[PAD_MAP[8]] = False
        if pad_name != "0":
            if check_code >= 11:
                # If any switch a to f is enabled then enable.
                for i in range(7,1,-1):
                    if pad_info[PAD_MAP[i]]:
                        pad_info[PAD_MAP[8]] = True
                        break
            else:
                pad_info[PAD_MAP[8]] = (
                    full_data[DEVICE_SWITCH_MAP[8]] == "1" and
                    float(full_data["A_190"]) > 0.1
                )

        return pad_info

    async def __full_load(self):
        """Perform a full load and create structure."""
        self.__data_loaded = False

        for device_key, device in self.__devices.items():
            module_id = device["info"]["module_id"]
            device_id = device["info"]["device_id"]

            # Create the Device Info
            device_info = await self.__api.get_device_info(module_id, device_id)
            for key, item in DEVICE_INFO_MAP.items():
                if item in device_info:
                    device["info"][key] = device_info[item]

            # Get the Full Device Data
            device_data = await self.__api.get_device_data(module_id, device_id)
            device["lastUpdateTime"] = device_data["timestamp"]
            device["updatedData"] = device_data["data"]["varfile_mt1_config1"]["001"].copy()
            device["fullData"] = device["updatedData"].copy()

            # Construct Normalized Data, using device map.
            self.__device_map = DEVICE_DATA_MAP
            enabled_pads = self.__enabled_pads(device_key)
            for pad, pad_enabled in enabled_pads.items():
                if not pad_enabled:
                    self.__device_map["pads"].pop(pad, None)

            self.__inverted_map = self.__invert_device_map(self.__device_map)
            device["data"] = self.__populate_data(self.__device_map, device["fullData"])

        self.__data_loaded = True
        return True

    async def connect(self, update_data = True):
        """Connect to the API, check the supported roles and update if required.

        Parameters:
            update_data (bool): False to only connect, default True

        Returns:
            connected (bool): True if connected Raises Error if not

        Raises:
            MasterThermConnectionError - Failed to Connect
            MasterThermAuthenticationError - Failed to Authenticate
            MasterThermUnsportedRole - Role is not supported by API"""
        result = await self.__api.connect()
        self.__role = result["role"]

        if self.__role not in SUPPORTED_ROLES:
            raise MasterThermUnsupportedRole("2", "Unsupported Role " + result["role"])

        # Initialize the Dictionary.
        self.__devices = {}
        for module in result["modules"]:
            for device in module["config"]:
                device_key = module["id"] + "-" + device["mb_addr"]

                self.__devices[device_key] = {
                    "lastUpdateTime": "0",
                    "info": {
                        "module_id": module["id"],
                        "module_name": module["module_name"],
                        "device_id": device["mb_addr"],
                        "device_name": device["mb_name"],
                    },
                    "updatedData": {},
                    "fullData": {},
                    "data": {},
                }

        if update_data:
            return await self.__full_load()

        return True

    async def refresh(self,full_load = False):
        """Refresh or Reload all entries for all devices."""
        if not await self.__api.is_connected():
            return False

        if full_load:
            return self.__full_load()

        if not self.__data_loaded:
            return False

        for device in self.__devices.values():
            module_id = device["info"]["module_id"]
            device_id = device["info"]["device_id"]

            # Refresh Device Info (checks login too)
            device_info = await self.__api.get_device_info(module_id, device_id)
            if device_info["returncode"] == "0":
                for key, item in DEVICE_INFO_MAP.items():
                    if item in device_info:
                        device["info"][key] = device_info[item]

            device_data = await self.__api.get_device_data(
                module_id, device_id, last_update_time=device["lastUpdateTime"])

            device["lastUpdateTime"] = device_data["timestamp"]
            device["updatedData"] = device_data["data"]["varfile_mt1_config1"]["001"].copy()
            device["fullData"].update(device["updatedData"])

            # Refresh Normalized Data
            update_data = False
            for register_key in device["updatedData"]:
                if register_key in self.__inverted_map:
                    update_data = True
                    break

            if update_data:
                device["data"] = self.__populate_data(self.__device_map, device["fullData"])

        return True

    def get_devices(self):
        """Return a List of the Devices with plus information."""
        # TODO: Add Randomize Key Data
        device_return = {}
        for device_id, device in self.__devices.items():
            device_return[device_id] = device["info"]

        return device_return

    def get_device_info(self, module_id, device_id):
        """Get the Information for a specific device."""
        # TODO: Add Randomize Key Data
        info = {}
        key = module_id + "-" + device_id
        if key in self.__devices:
            info = self.__devices[key]["info"]
        return info

    def get_device_registers(self, module_id, device_id, last_updated = False):
        """Get the Device Register Data, if lastUpdated is True then get the latest update data."""
        data = {}
        key = module_id + "-" + device_id
        if key in self.__devices:
            if last_updated:
                data = self.__devices[key]["updatedData"]
            else:
                data = self.__devices[key]["fullData"]
        return data

    def get_device_data(self, module_id, device_id):
        """Get the Device Data, if lastUpdated is True then get the latest update data."""
        data = {}
        key = module_id + "-" + device_id
        if key in self.__devices:
            data = self.__devices[key]["data"]
        return data
