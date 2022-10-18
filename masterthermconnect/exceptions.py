"""Contains all the MasterTherm Exception classes."""

class MasterThermError(Exception):
    """Base Exception for all MasterTherm Exceptions"""
    def __init__(self,status, message):
        """Initialize."""
        super().__init__(status)
        self.status = status
        self.message = message

class MasterThermAuthenticationError(MasterThermError):
    """Raised when login returns wrong result."""

class MasterThermConnectionError(MasterThermError):
    """Raised when communication ended in error."""

class MasterThermResponseFormatError(MasterThermError):
    """Raised when page returns an unexpected response."""

class MasterThermTokenInvalid(MasterThermError):
    """Raised when page returns the Token is not valie."""

class MasterThermUnsupportedRole(MasterThermError):
    """Raised when connecting to an Unsupported Role."""
