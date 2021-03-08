"""MasterTherm Controller, for handling MasterTherm Data."""
import logging

from .connection import Connection
from .const import (
    DEVICEINFO_MAP,
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
        self.__role = ""

        # The device structure is held as a dictionary with the following format:
        # {
        #   "id-mb_addr": {
        #       "lastUpdateTime": "1234567890",
        #       "info": { Various Information },
        #       "updatedData": { All Updated Data since last update },
        #       "fullData": { Full Data including last updated },
        #       "normalizedData": { TBD }
        #   }
        # }
        self.__devices = {}

    async def connect(self, updateData = True):
        """Connect to the API, check the supported roles and update if required."""
        result = await self.__api.connect()

        if not result["role"] in SUPPORTED_ROLES: 
            raise MasterThermUnsupportedRole("2", "Unsupported Role " + result["role"])

        # Initialize the Dictionary.
        self.__devices = {}
        for module in result["modules"]:
            for device in module["config"]:
                id = module["id"] + "-" + device["mb_addr"]

                data = {
                    "lastUpdateTime": "0",
                    "info": {
                        "module_id": module["id"],
                        "module_name": module["module_name"],
                        "device_id": device["mb_addr"],
                        "device_name": device["mb_name"],
                    },
                    "updatedData": {},
                    "fullData": {},
                }

                self.__devices[id] = data

        if updateData: return await self.refresh(fullLoad=True)
        else: return True
    
    async def refresh(self,fullLoad = False):
        """Refresh or Reload all entries for all devices."""
        if not await self.__api.isConnected(): return False

        for id, device in self.__devices.items():
            module_id = device["info"]["module_id"]
            device_id = device["info"]["device_id"]

            deviceInfo = await self.__api.getDeviceInfo(module_id, device_id)
            if deviceInfo["returncode"] == "0":
                for key, item in DEVICEINFO_MAP.items():
                    if item in deviceInfo: device["info"][key] = deviceInfo[item]

            lastUpdateTime = device["lastUpdateTime"]
            if fullLoad: lastUpdateTime = "0"
            deviceData = await self.__api.getDeviceData(module_id, device_id, last_update_time=lastUpdateTime)

            device["lastUpdateTime"] = deviceData["timestamp"]
            device["updatedData"] = deviceData["data"]["varfile_mt1_config1"]["001"].copy()
            if lastUpdateTime == "0":
                device["fullData"] = device["updatedData"].copy()
            else:
                device["fullData"].update(device["updatedData"])

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

    def getDeviceData(self, module_id, device_id, lastUpdated = False):
        """Get the Device Data, if lastUpdated is True then get the latest update data."""
        data = {}
        key = module_id + "-" + device_id
        if key in self.__devices:
            if lastUpdated: data = self.__devices[key]["updatedData"]
            else: data = self.__devices[key]["fullData"]
        return data
