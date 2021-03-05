"""Test Configuration for various tests."""
import json
import os
import pytest

from aiohttp import web, ClientSession
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from unittest.mock import patch

VALID_LOGIN = {
    "uname": "user name",
    "upwd": "hashpass",
    "token": "9jdhhs78dodlosd"
}

GENERAL_ERROR_RESPONSE = "User not logged in"

def load_fixture(filename):
    """Loads a JSON Fixture for testing."""
    try:
        path = os.path.join(os.path.dirname(__file__), "fixtures", filename)
        with open(path, encoding="utf-8") as fptr:
            return fptr.read()
    except Exception:
        return None

class MasterThermTestCase(AioHTTPTestCase):
    """The Base Test Class for the bulk of the testing, sets up some override methods."""

    def setUp(self):
        super().setUp()
        