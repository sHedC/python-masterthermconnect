"""Test the Initialization of the API."""

from aiohttp import ClientSession

from masterthermconnect import Controller

from .conftest import (
    load_fixture,
    VALID_LOGIN,
)

async def test_setup():
    """Test the Controller Sets up correctly."""
    api = Controller(ClientSession(), VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
    assert api is not None
    