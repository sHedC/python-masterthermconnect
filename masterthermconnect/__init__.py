"""Python API wrapper for Mastertherm Connect."""
from masterthermconnect.__version__ import __version__
from masterthermconnect.connection import Connection
from masterthermconnect.controller import Controller
from masterthermconnect.exceptions import (
    MasterthermAuthenticationError,
    MasterthermConnectionError,
    MasterthermResponseFormatError,
    MasterthermTokenInvalid,
    MasterthermUnsupportedRole,
)

__all__ = [
    "__version__",
    "Connection",
    "Controller",
    "MasterthermAuthenticationError",
    "MasterthermConnectionError",
    "MasterthermResponseFormatError",
    "MasterthermTokenInvalid",
    "MasterthermUnsupportedRole",
]
