"""Test the Initialization of the API."""
from unittest.mock import patch

from aiohttp import ClientSession
import pytest

from masterthermconnect import (
    Controller,
    MasterThermAuthenticationError,
    MasterThermConnectionError,
    MasterThermUnsupportedRole,
)

from .conftest import VALID_LOGIN, ConnectionMock


async def test_setup():
    """Test the Controller Sets up correctly."""
    api = Controller(ClientSession(), VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
    assert api is not None


async def test_connect():
    """Test the Controller Connects and setup devices."""
    controller = Controller(ClientSession(), VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
    mockconnect = ConnectionMock()

    with patch(
        "masterthermconnect.connection.Connection.connect",
        return_value=mockconnect.connect(),
    ) as mock_apiconnect:
        assert await controller.connect(update_data=False) is True

    assert len(mock_apiconnect.mock_calls) > 0


async def test_connect_unsupported():
    """Test the Controller Connects and setup devices."""
    controller = Controller(ClientSession(), VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
    mockconnect = ConnectionMock()

    with patch(
        "masterthermconnect.connection.Connection.connect",
        return_value=mockconnect.connect(role="999"),
    ) as mock_apiconnect:
        with pytest.raises(MasterThermUnsupportedRole):
            assert await controller.connect() is True

    assert len(mock_apiconnect.mock_calls) == 1


async def test_connect_failure():
    """Test the Controller Invalid Login Connection."""
    controller = Controller(ClientSession(), VALID_LOGIN["uname"], VALID_LOGIN["upwd"])

    with patch(
        "masterthermconnect.connection.Connection.connect",
        side_effect=MasterThermAuthenticationError(
            "1", "Invalid user name or password"
        ),
    ) as mock_apiconnect:
        with pytest.raises(MasterThermAuthenticationError):
            await controller.connect()

    assert len(mock_apiconnect.mock_calls) > 0


async def test_connect_error():
    """Test the Controller on Connection Failure."""
    controller = Controller(ClientSession(), VALID_LOGIN["uname"], VALID_LOGIN["upwd"])

    with patch(
        "masterthermconnect.connection.Connection.connect",
        side_effect=MasterThermConnectionError("500", "Some Other Error"),
    ) as mock_apiconnect:
        with pytest.raises(MasterThermConnectionError):
            await controller.connect()

    assert len(mock_apiconnect.mock_calls) > 0


async def test_get_info_data():
    """Test the Controller Connects and setup devices."""
    controller = Controller(ClientSession(), VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
    mockconnect = ConnectionMock()

    with patch(
        "masterthermconnect.connection.Connection.connect",
        return_value=mockconnect.connect(),
    ) as mock_apiconnect, patch(
        "masterthermconnect.connection.Connection.get_device_info",
        side_effect=mockconnect.get_device_info,
    ) as mock_get_device_info, patch(
        "masterthermconnect.connection.Connection.get_device_data",
        side_effect=mockconnect.get_device_data,
    ) as mock_get_device_data:
        assert await controller.connect() is True

    assert len(mock_apiconnect.mock_calls) > 0
    assert len(mock_get_device_info.mock_calls) > 0
    assert len(mock_get_device_data.mock_calls) > 0

    assert controller.get_devices()

    info = controller.get_device_info("1234", "1")
    data_raw = controller.get_device_registers("1234", "1")
    data = controller.get_device_data("1234", "1")

    assert info["country"] == "UK"
    assert data_raw["A_500"] == "46.2"
    assert data["on"] is True
    assert data["outside_temp"] == 4.2
    assert data["requested_temp"] == 46.2
    assert data["pads"]["pada"]["name"] == "HW-AN-"
    assert data["pads"]["pada"]["on"] is True
    assert "padc" not in data["pads"]


async def test_getdata_update():
    """Test getting the data and getting an update.
    Test the Controller Connects and setup devices."""
    controller = Controller(ClientSession(), VALID_LOGIN["uname"], VALID_LOGIN["upwd"])
    mockconnect = ConnectionMock()

    with patch(
        "masterthermconnect.connection.Connection.connect",
        return_value=mockconnect.connect(),
    ) as mock_apiconnect, patch(
        "masterthermconnect.connection.Connection.isConnected", return_value=True
    ) as mock_isconnected, patch(
        "masterthermconnect.connection.Connection.get_device_info",
        side_effect=mockconnect.get_device_info,
    ) as mock_get_device_info, patch(
        "masterthermconnect.connection.Connection.get_device_data",
        side_effect=mockconnect.get_device_data,
    ) as mock_get_device_data:
        assert await controller.connect() is True

        data = controller.get_device_data("1234", "1")
        assert data["requested_temp"] == 46.2
        assert await controller.refresh() is True

    assert len(mock_apiconnect.mock_calls) == 1
    assert len(mock_isconnected.mock_calls) == 1
    assert len(mock_get_device_info.mock_calls) == 2
    assert len(mock_get_device_data.mock_calls) == 2

    assert controller.get_devices()

    data_raw = controller.get_device_registers("1234", "1")
    data_update = controller.get_device_registers("1234", "1", last_updated=True)
    data = controller.get_device_data("1234", "1")

    assert data_raw["A_500"] == "40.7"
    assert data_update["A_500"] == "40.7"
    assert "I_418" not in data_update
    assert "I_418" in data_raw
    assert data["requested_temp"] == 40.7
