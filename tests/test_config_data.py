"""Test the Configuration data in const."""
from unittest.mock import patch

from aiohttp import ClientSession
from masterthermconnect import MasterthermController

from .conftest import VALID_LOGIN, ConnectionMock


async def test_setup():
    """Test the Setup."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock()

    with patch(
        "masterthermconnect.api.MasterthermAPI.connect",
        return_value=mockconnect.connect(),
    ), patch(
        "masterthermconnect.api.MasterthermAPI.get_device_info",
        side_effect=mockconnect.get_device_info,
    ), patch(
        "masterthermconnect.api.MasterthermAPI.get_device_data",
        side_effect=mockconnect.get_device_data,
    ):
        assert await controller.connect() is True
        assert await controller.refresh() is True

    # Verify basic setup.
    data = controller.get_device_data("1234", "1")
    assert data["hp_power_state"]
    assert data["control_curve_heating"]["setpoint_a_outside"] == 20.0


async def test_hc0():
    """Test basic setup HC0 only no optional modules."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock(api_version="v2")

    with patch(
        "masterthermconnect.api.MasterthermAPI.connect",
        return_value=mockconnect.connect(),
    ), patch(
        "masterthermconnect.api.MasterthermAPI.get_device_info",
        side_effect=mockconnect.get_device_info,
    ), patch(
        "masterthermconnect.api.MasterthermAPI.get_device_data",
        side_effect=mockconnect.get_device_data,
    ):
        assert await controller.connect() is True
        assert await controller.refresh() is True

    # Verify Setup with HC0 only
    data = controller.get_device_data("10021", "2")
    assert data["hp_power_state"]
    assert data["heating_circuits"]["hc0"]["enabled"]


async def test_hc1_no_thermostat():
    """Test no thermostat installed in HC1"""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock(api_version="v1")

    with patch(
        "masterthermconnect.api.MasterthermAPI.connect",
        return_value=mockconnect.connect(),
    ), patch(
        "masterthermconnect.api.MasterthermAPI.get_device_info",
        side_effect=mockconnect.get_device_info,
    ), patch(
        "masterthermconnect.api.MasterthermAPI.get_device_data",
        side_effect=mockconnect.get_device_data,
    ):
        assert await controller.connect() is True
        assert await controller.refresh() is True

    # Verify Setup with HC0 only
    data = controller.get_device_data("1234", "1")
    assert data["hp_power_state"]
    assert data["heating_circuits"]["hc1"]["enabled"]
    assert data["heating_circuits"]["hc1"]["int"]["enabled"]
    assert not "pad" in data["heating_circuits"]["hc1"]


async def test_hcx_thermostat():
    """Test Thermostat installed in HC?"""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock(api_version="v2")

    with patch(
        "masterthermconnect.api.MasterthermAPI.connect",
        return_value=mockconnect.connect(),
    ), patch(
        "masterthermconnect.api.MasterthermAPI.get_device_info",
        side_effect=mockconnect.get_device_info,
    ), patch(
        "masterthermconnect.api.MasterthermAPI.get_device_data",
        side_effect=mockconnect.get_device_data,
    ):
        assert await controller.connect() is True
        assert await controller.refresh() is True

    # Verify Setup with HC0 only
    data = controller.get_device_data("10021", "1")
    assert data["hp_power_state"]
    assert data["heating_circuits"]["hc2"]["enabled"]
    assert data["heating_circuits"]["hc2"]["pad"]["enabled"]
    assert not "int" in data["heating_circuits"]["hc2"]
