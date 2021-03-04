"""MasterTherm Controller, for handling MasterTherm Data."""
import logging

from masterthermconnect.connecton import Connection

_LOGGER = logging.getLogger(__name__)

class Controller(object):
    """Mastertherm Connect Object."""

    def __init__(self, websession, username, password):
        """Initialize the Connection Object."""
        self.__api = Connection(websession, username, password)
        self.__role = ""

        # The device structure is held as a dictionary with the following format:
        # {
        #   "id-mbr_addr": {
        #       "lastUpdateTime": "1234567890",
        #       "info": { Various Information },
        #       "updatedData": { All Updated Data since last update },
        #       "fullData": { Full Data including last updated },
        #       "normalizedData": { TBD }
        #   }
        # }
        self.__devices = {}

    async def connect(self, updateData = False):
        return False
    
    async def refresh(self):
        return False

    async def getModuleInfo(self, moduleId):
        return {}

    async def getModules(self):
        return {}
