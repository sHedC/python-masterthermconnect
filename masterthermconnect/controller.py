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
from .exceptions import (
    MasterThermUnsupportedRole,
)

_LOGGER = logging.getLogger(__name__)

class Controller(object):
    """Mastertherm Connect Object."""

    def __init__(self, websession, username, password):
        """Initialize the Connection Object."""
        self.__api = Connection(websession, username, password)
        self.__deviceMap = None
        self.__invertedMap = None
        self.__role = ""
        self.__dataLoaded = False

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

    def __invertDeviceMap(self, map, keyList = []):
        """Invert the given map and return, this is a nested method."""
        invertedMap = {}
        for key, item in map.items():
            newKeyList = keyList.copy()
            newKeyList.append(key)
            if not isinstance(item,dict):
                itemValue = item[1]
                if isinstance(itemValue,list):
                    for listValue in itemValue:
                        invertedMap[listValue] = newKeyList
                else:
                    itemType = item[0]
                    if not (itemValue == "" or itemType == "fixed"): 
                        invertedMap[itemValue] = newKeyList
            else:
                invertedMap.update(self.__invertDeviceMap(item, newKeyList))

        return invertedMap

    def __populateData(self, map, registers):
        """Populate the Data from the fullData and DeviceMap."""
        data = {}
        for key, item in map.items():
            if not isinstance(item, dict):
                itemType = item[0]
                itemValue = item[1]
                if itemType == "fixed":
                    data[key] = itemValue
                elif itemType == "bool":
                    if itemValue == "": data[key] = False
                    else: data[key] = (registers[itemValue] == "1")
                elif itemType == "float":
                    if itemValue == "": data[key] = 0.0
                    else: data[key] = float(registers[itemValue])
                elif itemType == "int":
                    if itemValue == "": data[key] = 0
                    else: data[key] = int(registers[itemValue])
                elif itemType == "string":
                    if itemValue == "": data[key] = "" 
                    else:
                        itemStr = ""
                        for listValue in itemValue:
                            itemStr = itemStr + CHAR_MAP[int(registers[listValue])]
                        data[key] = itemStr
            else:
                data[key] = self.__populateData(map[key], registers)

        return data

    def __getPadName(self, pad, id):
        """Build the Pad Name from the full data."""
        if pad not in DEVICE_DATA_PADMAP: return "0"

        padName = ""
        padEmpty = ""
        fullData = self.__devices[id]["fullData"]
        for key in DEVICE_DATA_PADMAP[pad]["name"][1]:
            padName = padName + CHAR_MAP[int(fullData[key])]
            padEmpty = padEmpty + "-"

        if padName == padEmpty: padName = "0"
        return padName

    def __enabledPADs(self, id):
        """Enable the Pads for the devices, decoded as best as possible."""
        fullData = self.__devices[id]["fullData"]
        padInfo = {}

        # Pad 0 and 1 I believe are the Main Heating and Cooling circuites
        # I have heating enabled and cooling disabled but both show disabled.
        # TODO: Check what happens if I enable/ Disable what registers get updated.
        for i in range(2):
            padInfo[PAD_MAP[i]] = (fullData[DEVICE_SWITCH_MAP[i]] == "1")

        # Following Code is to manage Switch Pad a to f which
        # these are various typs of circuites Water Heating/ Thermal etc.
        # TODO: see if we can identify where the types are stored.

        # Used in the process of Enabling/ Disabling Pads.
        checkCode = int(fullData["I_104"])
        if checkCode < 11: 
            checkCode = 10 
        else:
             if checkCode <= 200: checkCode = 11

        # Setup and Enable Pad a to f
        for i in range(2,8):
            padname = self.__getPadName(PAD_MAP[i], id)
            if padname != "0" and checkCode >= 11:
                padInfo[PAD_MAP[i]] = (fullData[DEVICE_SWITCH_MAP[i]] == "1")
            else:
                padInfo[PAD_MAP[i]] = False

        # Pad Switch 8, no idea where a name comes from so its always disabled.
        # maby its SOLAR?
        padname = self.__getPadName(PAD_MAP[8], id)
        padInfo[PAD_MAP[8]] = False
        if padname != "0":
            if checkCode >= 11:
                # If any switch a to f is enabled then enable.
                for i in range(7,1,-1):
                    if padInfo[PAD_MAP[i]]: 
                        padInfo[PAD_MAP[8]] = True
                        break
            else:
                padInfo[PAD_MAP[8]] = (
                    fullData[DEVICE_SWITCH_MAP[8]] == "1" and 
                    float(fullData["A_190"]) > 0.1
                )

        return padInfo

    async def __fullLoad(self):
        """Perform a full load and create structure."""
        self.__dataLoaded = False

        for id, device in self.__devices.items():
            module_id = device["info"]["module_id"]
            device_id = device["info"]["device_id"]

            # Create the Device Info
            deviceInfo = await self.__api.getDeviceInfo(module_id, device_id)
            for key, item in DEVICE_INFO_MAP.items():
                if item in deviceInfo: device["info"][key] = deviceInfo[item]

            # Get the Full Device Data
            deviceData = await self.__api.getDeviceData(module_id, device_id)
            device["lastUpdateTime"] = deviceData["timestamp"]
            device["updatedData"] = deviceData["data"]["varfile_mt1_config1"]["001"].copy()
            device["fullData"] = device["updatedData"].copy()

            # Construct Normalized Data, using device map.
            self.__deviceMap = DEVICE_DATA_MAP
            enabledPads = self.__enabledPADs(id)
            for pad, padEnabled in enabledPads.items():
                if not padEnabled: self.__deviceMap["pads"].pop(pad, None)

            self.__invertedMap = self.__invertDeviceMap(self.__deviceMap)
            device["data"] = self.__populateData(self.__deviceMap, device["fullData"])

        self.__dataLoaded = True
        return True

    async def connect(self, updateData = True):
        """Connect to the API, check the supported roles and update if required."""
        result = await self.__api.connect()
        self.__role = result["role"]

        if not result["role"] in SUPPORTED_ROLES: 
            raise MasterThermUnsupportedRole("2", "Unsupported Role " + result["role"])

        # Initialize the Dictionary.
        self.__devices = {}
        for module in result["modules"]:
            for device in module["config"]:
                id = module["id"] + "-" + device["mb_addr"]

                self.__devices[id] = {
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

        if updateData: return await self.__fullLoad()
        else: return True

    async def refresh(self,fullLoad = False):
        """Refresh or Reload all entries for all devices."""
        if not await self.__api.isConnected(): return False

        if fullLoad: return self.__fullLoad()

        if not self.__dataLoaded: return False
        for id in self.__devices:
            device = self.__devices[id]
            module_id = device["info"]["module_id"]
            device_id = device["info"]["device_id"]
            
            # Refresh Device Info (checks login too)
            deviceInfo = await self.__api.getDeviceInfo(module_id, device_id)
            if deviceInfo["returncode"] == "0":
                for key, item in DEVICE_INFO_MAP.items():
                    if item in deviceInfo: device["info"][key] = deviceInfo[item]

            deviceData = await self.__api.getDeviceData(module_id, device_id, last_update_time=device["lastUpdateTime"])

            device["lastUpdateTime"] = deviceData["timestamp"]
            device["updatedData"] = deviceData["data"]["varfile_mt1_config1"]["001"].copy()
            device["fullData"].update(device["updatedData"])
                
            # Refresh Normalized Data
            updateData = False
            for registerKey in device["updatedData"]:
                if registerKey in self.__invertedMap: 
                    updateData = True
                    break
                
            if updateData: device["data"] = self.__populateData(self.__deviceMap, device["fullData"])

        return True

    def getDevices(self):
        """Return a List of the Devices with plus information."""
        deviceReturn = {}
        for device_id, device in self.__devices.items():
            deviceReturn[device_id] = device["info"]

        return deviceReturn

    def getDeviceInfo(self, module_id, device_id):
        """Get the Information for a specific device."""
        info = {}
        key = module_id + "-" + device_id
        if key in self.__devices: info = self.__devices[key]["info"]
        return info

    def getDeviceRegisters(self, module_id, device_id, lastUpdated = False):
        """Get the Device Register Data, if lastUpdated is True then get the latest update data."""
        data = {}
        key = module_id + "-" + device_id
        if key in self.__devices:
            if lastUpdated: data = self.__devices[key]["updatedData"]
            else: data = self.__devices[key]["fullData"]
        return data

    def getDeviceData(self, module_id, device_id):
        """Get the Device Data, if lastUpdated is True then get the latest update data."""
        data = {}
        key = module_id + "-" + device_id
        if key in self.__devices:
            data = self.__devices[key]["data"]
        return data
