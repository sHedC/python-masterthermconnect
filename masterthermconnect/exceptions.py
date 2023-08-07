"""Contains all the Mastertherm Exception classes."""


class MasterthermError(Exception):
    """Base Exception for all Mastertherm Exceptions."""

    def __init__(self, status, message):
        """Initialize."""
        super().__init__(status)
        self.status = status
        self.message = message


class MasterthermUnsupportedVersion(MasterthermError):
    """Raised when a version that is not supported is used."""


class MasterthermAuthenticationError(MasterthermError):
    """Raised when login returns wrong result."""


class MasterthermConnectionError(MasterthermError):
    """Raised when communication ended in error."""


class MasterthermResponseFormatError(MasterthermError):
    """Raised when page returns an unexpected response."""


class MasterthermTokenInvalid(MasterthermError):
    """Raised when page returns the Token is not valie."""


class MasterthermUnsupportedRole(MasterthermError):
    """Raised when connecting to an Unsupported Role."""


class MasterthermEntryNotFound(MasterthermError):
    """Raised when the data entry update requested is not found."""


class MasterthermPumpError(MasterthermError):
    """Raised if there is an Error retrieving data from the pump."""

    DEVICENOTFOUND = 5
    OFFLINE = 9


class MasterthermServerTimeoutError(MasterthermError):
    """Raised if there is a server timeout error."""
