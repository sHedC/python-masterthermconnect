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
    assert data["heating_circuits"]["hc0"]["pad"]["enabled"]


async def test_hc1_no_thermostat():
    """Test no thermostat installed in HC1."""
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
    assert data["heating_circuits"]["hc1"]["ambient_requested"] == 20.2
    assert "pad" not in data["heating_circuits"]["hc1"]


async def test_hcx_thermostat():
    """Test Thermostat installed in HC."""
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
    assert data["heating_circuits"]["hc2"]["ambient_requested"] == 20.1


async def test_hcx_loop_type():
    """Test HCx Loop Type."""
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

    # Verify Setup with HC1 and HC2
    data = controller.get_device_data("1234", "1")
    assert data["heating_circuits"]["hc1"]["loop_type"] == 3
    assert data["heating_circuits"]["hc2"]["loop_type"] == 3


async def test_set_ambient_requested():
    """Test HC1 Ambient Requested."""
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
    ), patch(
        "masterthermconnect.api.MasterthermAPI.set_device_data",
        side_effect=mockconnect.set_device_data,
    ):
        assert await controller.connect() is True
        assert await controller.refresh() is True

        data = controller.get_device_data("1234", "1")
        assert await controller.set_device_data_item(
            "1234", "1", "heating_circuits.hc1.ambient_requested", 50.1
        )

        # Verfiy we update internally.
        registers = controller.get_device_registers("1234", "1")
        assert registers["A_215"] == "50.1"

        await controller.refresh(full_load=True)
        data = controller.get_device_data_item(
            "1234", "1", "heating_circuits.hc1.ambient_requested"
        )
        assert data == 50.1


async def test_season_set():
    """Test Season Sets correctly."""
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
    ), patch(
        "masterthermconnect.api.MasterthermAPI.set_device_data",
        side_effect=mockconnect.set_device_data,
    ):
        assert await controller.connect()
        assert await controller.refresh()

        # Test Winter Set
        assert await controller.set_device_data_item(
            "1234", "1", "season.manual_set", True
        )
        assert await controller.set_device_data_item("1234", "1", "season.winter", True)

        assert await controller.refresh(full_load=True)
        season = controller.get_device_data_item("1234", "1", "season.mode")
        assert season == "winter"

        # Test Summer Set
        assert await controller.set_device_data_item(
            "1234", "1", "season.manual_set", True
        )
        assert await controller.set_device_data_item(
            "1234", "1", "season.winter", False
        )

        assert await controller.refresh(full_load=True)
        season = controller.get_device_data_item("1234", "1", "season.mode")
        assert season == "summer"

        # Test Auto Winter Set
        assert await controller.set_device_data_item(
            "1234", "1", "season.manual_set", False
        )
        assert await controller.set_device_data_item("1234", "1", "season.winter", True)

        assert await controller.refresh(full_load=True)
        season = controller.get_device_data_item("1234", "1", "season.mode")
        assert season == "auto-winter"
