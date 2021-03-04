"""MasterTherm Connection to the Web API."""
import logging

_LOGGER = logging.getLogger(__name__)

class Connection:
    """Connection Handler for the MasterTherm API."""

    def __init__(self, websession, username, password):
        """Initiate the Connection API."""
        self.__session = websession
        self.__unname = username
        self.__upwd = password
        self.__token = None
        self.__expires = None

    async def connect(self):
        return {}

    async def getModuleInfo(self, moduleId):
        return {}

    async def getDeviceData(self, moduleId, deviceId):
        return {}
        