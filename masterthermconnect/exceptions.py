"""Contains all the MasterTherm Exception classes."""
class MasterThermAuthenticationError(Exception):
    """Raised when login returns wrong result."""
    def __init__(self,status,message):
        """Initialize."""
        super(MasterThermAuthenticationError,self).__init__(status)
        self.status = status
        self.message = message

class MasterThermConnectionError(Exception):
    """Raised when communication ended in error."""
    def __init__(self,status,message):
        """Initialize."""
        super(MasterThermConnectionError,self).__init__(status)
        self.status = status
        self.message = message
