"""Test the Initialization of the API."""
from unittest.mock import patch

from aiohttp import ClientSession
import pytest

from masterthermconnect import (
    MasterthermController,
    MasterthermAuthenticationError,
    MasterthermConnectionError,
)

from .conftest import VALID_LOGIN, ConnectionMock


async def test_setup():
    """Test the Controller Sets up correctly."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    assert controller is not None


async def test_connect():
    """Test the Controller Connects and setup devices."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock()

    with patch(
        "masterthermconnect.api.MasterthermAPI.connect",
        return_value=mockconnect.connect(),
    ) as mock_apiconnect:
        assert await controller.connect() is True

    assert len(mock_apiconnect.mock_calls) > 0


async def test_connect_failure():
    """Test the Controller Invalid Login Connection."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )

    with patch(
        "masterthermconnect.api.MasterthermAPI.connect",
        side_effect=MasterthermAuthenticationError(
            "1", "Invalid user name or password"
        ),
    ) as mock_apiconnect:
        with pytest.raises(MasterthermAuthenticationError):
            await controller.connect()

    assert len(mock_apiconnect.mock_calls) > 0


async def test_connect_error():
    """Test the Controller on Connection Failure."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )

    with patch(
        "masterthermconnect.api.MasterthermAPI.connect",
        side_effect=MasterthermConnectionError("500", "Some Other Error"),
    ) as mock_apiconnect:
        with pytest.raises(MasterthermConnectionError):
            await controller.connect()

    assert len(mock_apiconnect.mock_calls) > 0


async def test_get_info_data():
    """Test the Controller Connects and setup devices."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock()

    with patch(
        "masterthermconnect.api.MasterthermAPI.connect",
        return_value=mockconnect.connect(),
    ) as mock_api_connect, patch(
        "masterthermconnect.api.MasterthermAPI.get_device_info",
        side_effect=mockconnect.get_device_info,
    ) as mock_get_device_info, patch(
        "masterthermconnect.api.MasterthermAPI.get_device_data",
        side_effect=mockconnect.get_device_data,
    ) as mock_get_device_data:
        assert await controller.connect() is True
        assert await controller.refresh() is True

    assert len(mock_api_connect.mock_calls) > 0
    assert len(mock_get_device_info.mock_calls) > 0
    assert len(mock_get_device_data.mock_calls) > 0

    assert controller.get_devices()

    info = controller.get_device_info("1234", "1")
    data_raw = controller.get_device_registers("1234", "1")
    data = controller.get_device_data("1234", "1")

    assert info["country"] == "UK"
    assert data_raw["A_500"] == "46.2"
    assert data["hp_power_state"] is True
    assert data["outside_temp"] == 4.2
    assert data["actual_temp"] == 46.2
    assert data["heating_circuits"]["hc1"]["name"] == "HW-AN-"
    assert data["heating_circuits"]["hc1"]["on"] is True
    assert not "hc3" in data["heating_circuits"]


async def test_new_api_get_info_data():
    """Test the Controller Connects and setup devices for the New API."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock(api_version="v2")

    with patch(
        "masterthermconnect.api.MasterthermAPI.connect",
        return_value=mockconnect.connect(),
    ) as mock_api_connect, patch(
        "masterthermconnect.api.MasterthermAPI.get_device_info",
        side_effect=mockconnect.get_device_info,
    ) as mock_get_device_info, patch(
        "masterthermconnect.api.MasterthermAPI.get_device_data",
        side_effect=mockconnect.get_device_data,
    ) as mock_get_device_data:
        assert await controller.connect() is True
        assert await controller.refresh() is True

    assert len(mock_api_connect.mock_calls) > 0
    assert len(mock_get_device_info.mock_calls) > 0
    assert len(mock_get_device_data.mock_calls) > 0

    assert controller.get_devices()

    info = controller.get_device_info("10021", "1")
    data_raw = controller.get_device_registers("10021", "1")
    data = controller.get_device_data("10021", "1")

    assert info["country"] == "CZ"
    assert data_raw["A_500"] == "30.5"
    assert data["hp_power_state"] is True
    assert data["outside_temp"] == 6.4
    assert data["actual_temp"] == 30.5

    assert not "hc0" in data["heating_circuits"]

    assert data["heating_circuits"]["hc1"]["name"] == "Living room"
    assert data["heating_circuits"]["hc1"]["on"] is True

    assert data["heating_circuits"]["hc2"]["name"] == "Bedroom"
    assert data["heating_circuits"]["hc2"]["on"] is False


async def test_getdata_update():
    """Test getting the data and getting an update.
    Test the Controller Connects and setup devices."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock()

    with patch(
        "masterthermconnect.api.MasterthermAPI.connect",
        return_value=mockconnect.connect(),
    ) as mock_apiconnect, patch(
        "masterthermconnect.api.MasterthermAPI.get_device_info",
        side_effect=mockconnect.get_device_info,
    ) as mock_get_device_info, patch(
        "masterthermconnect.api.MasterthermAPI.get_device_data",
        side_effect=mockconnect.get_device_data,
    ) as mock_get_device_data:
        assert await controller.connect() is True
        controller.set_refresh_rate(data_refresh_seconds=0)
        assert await controller.refresh() is True

        data = controller.get_device_data("1234", "1")
        assert data["actual_temp"] == 46.2
        assert await controller.refresh() is True

    assert len(mock_apiconnect.mock_calls) == 1
    assert len(mock_get_device_info.mock_calls) == 1
    assert len(mock_get_device_data.mock_calls) == 2

    assert controller.get_devices()

    data_raw = controller.get_device_registers("1234", "1")
    data_update = controller.get_device_registers("1234", "1", last_updated=True)
    data = controller.get_device_data("1234", "1")

    assert data_raw["A_500"] == "40.7"
    assert data_update["A_500"] == "40.7"
    assert "I_418" not in data_update
    assert "I_418" in data_raw
    assert data["actual_temp"] == 40.7
