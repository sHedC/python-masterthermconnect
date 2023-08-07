"""Test the Initialization of the API."""
from unittest.mock import patch

from aiohttp import ClientSession
import pytest

from masterthermconnect import (
    MasterthermController,
    MasterthermAuthenticationError,
    MasterthermConnectionError,
    MasterthermEntryNotFound,
    MasterthermPumpError,
)
from masterthermconnect.const import URL_BASE

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
    ) as mock_apiconnect, pytest.raises(MasterthermAuthenticationError):
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
    ) as mock_apiconnect, pytest.raises(MasterthermConnectionError):
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
    assert data_raw["A_500"] == "32.1"
    assert data["hp_power_state"] is True
    assert data["outside_temp"] == 5.3
    assert data["actual_temp"] == 32.1
    assert data["heating_circuits"]["hc1"]["name"] == "HW-ANN"
    assert data["heating_circuits"]["hc1"]["on"] is False
    assert "hc3" not in data["heating_circuits"]
    assert "pool" not in data["heating_circuits"]
    assert "solar" not in data["heating_circuits"]


async def test_pool_solar():
    """Test the Controller Gets Pool and Solar."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock(api_version="v1", use_mt=True)

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

    info = controller.get_device_info("0001", "1")
    data = controller.get_device_data("0001", "1")

    assert info["country"] == "DE"
    assert data["heating_circuits"]["pool"]
    assert data["heating_circuits"]["solar"]


async def test_operating_mode_idle():
    """Test the Controller Operating Mode."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock(api_version="v1", use_mt=True)

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

    data = controller.get_device_data("0524", "4")

    assert data["operating_mode"] == "idle"


async def test_operating_mode_cooling():
    """Test the Passive Cooling Operating Mode."""
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

    data = controller.get_device_data("10021", "2")

    assert data["operating_mode"] == "cooling"
    assert data["requested_temp"] == 15.1


async def test_operating_mode_heating():
    """Test the Controller Operating Mode."""
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

    data = controller.get_device_data("1234", "1")

    assert data["operating_mode"] == "heating"
    assert data["requested_temp"] == 34.7


async def test_operating_mode_dhw():
    """Test the Controller Operating Mode DHW."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock(api_version="v1", use_mt=True)

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

    data = controller.get_device_data("0002", "1")

    assert data["operating_mode"] == "dhw"
    assert data["requested_temp"] == 45.0


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
    assert info["api_url"] == URL_BASE

    assert data_raw["A_500"] == "30.5"
    assert data["hp_power_state"] is True
    assert data["outside_temp"] == 6.4
    assert data["actual_temp"] == 30.5

    assert "hc0" not in data["heating_circuits"]

    assert data["heating_circuits"]["hc1"]["name"] == "Living room"
    assert data["heating_circuits"]["hc1"]["on"] is True

    assert data["heating_circuits"]["hc2"]["name"] == "Bedroom"
    assert data["heating_circuits"]["hc2"]["on"] is False


async def test_getdata_update():
    """Test getting the data and getting an update.

    Test the Controller Connects and setup devices.
    """
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
        controller.set_refresh_rate(data_refresh_seconds=0, data_offset_seconds=0)
        assert await controller.refresh() is True

        data = controller.get_device_data("1234", "1")
        assert data["actual_temp"] == 32.1
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


async def test_periodic_full_load():
    """Test getting full data on refresh time."""
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
        controller.set_refresh_rate(
            data_refresh_seconds=0, data_offset_seconds=0, full_refresh_minutes=0
        )
        assert await controller.refresh() is True

        data = controller.get_device_data("1234", "1")
        assert data["actual_temp"] == 32.1
        assert await controller.refresh() is True

    assert len(mock_apiconnect.mock_calls) == 1
    assert len(mock_get_device_info.mock_calls) == 1
    assert len(mock_get_device_data.mock_calls) == 2


async def test_season_winter():
    """Test the Controller Season."""
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

    data = controller.get_device_data("1234", "1")

    assert data["season"]["mode"] == "winter"


async def test_season_auto_winter():
    """Test the Controller Season Auto Winter."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock(api_version="v1", use_mt=True)

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

    data = controller.get_device_data("0001", "1")

    assert data["season"]["mode"] == "winter"


async def test_toggle_hp_on():
    """Test toggling the HP Main Switch."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock(api_version="v1", use_mt=True)

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
    ) as mock_set:
        assert await controller.connect() is True
        assert await controller.refresh() is True

        data = controller.get_device_data("0001", "1")
        state = data["hp_power_state"]

        assert await controller.set_device_data_item(
            "0001", "1", "hp_power_state", not state
        )

        await controller.refresh(full_load=True)
        data = controller.get_device_data_item("0001", "1", "hp_power_state")
        assert data != state

    assert len(mock_set.mock_calls) > 0


async def test_toggle_hc1_on():
    """Test toggling the Heating Circuit 1 Switch."""
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
    ) as mock_set:
        assert await controller.connect() is True
        assert await controller.refresh() is True

        data = controller.get_device_data("1234", "1")
        state = data["heating_circuits"]["hc1"]["on"]

        assert await controller.set_device_data_item(
            "1234", "1", "heating_circuits.hc1.on", not state
        )

        await controller.refresh(full_load=True)
        data = controller.get_device_data_item("1234", "1", "heating_circuits.hc1.on")
        assert data != state

    assert len(mock_set.mock_calls) > 0


async def test_set_not_valid():
    """Test that value that can't be updated is disabled."""
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
        temp = data["heating_circuits"]["hc1"]["ambient_temp"]

        with pytest.raises(MasterthermEntryNotFound):
            await controller.set_device_data_item(
                "1234", "1", "heating_circuits.hc1.ambient_temp", 50.1
            )

        await controller.refresh(full_load=True)
        data = controller.get_device_data_item(
            "1234", "1", "heating_circuits.hc1.ambient_temp"
        )
        assert data == temp


async def test_cooling_feature():
    """Test the Controller Correctly disables Cooling Mode."""
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

    info1 = controller.get_device_info("10021", "1")
    data1 = controller.get_device_data("10021", "1")
    info2 = controller.get_device_info("10021", "2")
    data2 = controller.get_device_data("10021", "2")

    # Unit 1 has cooling disabled
    assert info1["cooling"] == "0"
    assert "hp_function" not in data1
    assert "control_curve_cooling" not in data1

    # Unit 2 has cooling enabled
    assert info2["cooling"] == "1"
    assert "hp_function" in data2
    assert "control_curve_cooling" in data2


async def test_set_cooling_feature():
    """Test cooling feature setting."""
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
    ), patch(
        "masterthermconnect.api.MasterthermAPI.set_device_data",
        side_effect=mockconnect.set_device_data,
    ):
        assert await controller.connect() is True
        assert await controller.refresh() is True

        with pytest.raises(MasterthermEntryNotFound):
            await controller.set_device_data_item("10021", "1", "hp_function", 1)

        with pytest.raises(MasterthermEntryNotFound):
            await controller.set_device_data_item(
                "10021", "1", "control_curve_cooling.setpoint_a_outside", 20.2
            )

        await controller.set_device_data_item("10021", "2", "hp_function", 1)
        await controller.set_device_data_item(
            "10021", "2", "control_curve_cooling.setpoint_a_outside", 20.2
        )


async def test_ground_source():
    """Test the HP Types and what type of thermal pump."""
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

    assert controller.get_device_data_item("1234", "1", "hp_type") == 1
    assert "brine_pump_running" in controller.get_device_data("1234", "1")


async def test_air_source():
    """Test the HP Types and what type of thermal pump."""
    controller = MasterthermController(
        VALID_LOGIN["uname"], VALID_LOGIN["upwd"], ClientSession()
    )
    mockconnect = ConnectionMock(api_version="v1", use_mt=True)

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

    data = controller.get_device_data("0001", "1")
    assert data["hp_type"] == 4
    assert "fan_running" in data

    data = controller.get_device_data("0524", "1")
    assert data["hp_type"] == 0
    assert "fan_running" in data


async def test_pump_offline_connect():
    """Test the Pump being offline on initial connect."""
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
        side_effect=MasterthermPumpError(
            MasterthermPumpError.OFFLINE,
            "Actual data for some variables are not available.",
        ),
    ):
        assert await controller.connect() is True
        assert await controller.refresh() is True

    assert controller.get_device_data_item("1234", "1", "operating_mode") == "offline"


async def test_pump_offline_update():
    """Test the Pump being offline after connect on update."""
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

    with patch(
        "masterthermconnect.api.MasterthermAPI.get_device_info",
        side_effect=mockconnect.get_device_info,
    ), patch(
        "masterthermconnect.api.MasterthermAPI.get_device_data",
        side_effect=MasterthermPumpError(
            MasterthermPumpError.OFFLINE,
            "Actual data for some variables are not available.",
        ),
    ):
        assert await controller.refresh(full_load=True)

    assert controller.get_device_data_item("1234", "1", "operating_mode") == "offline"


async def test_diagnostics_data():
    """Test the Diagnostics Data comes back correctly."""
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

        diag_data = controller.get_diagnostics_data()
        # Verify Sensitive Data:

        # Info Sensitive
        info = controller.get_device_info("10021", "1")
        diag_info = diag_data["1112_1"]["info"]
        assert diag_info["module_id"] != info["module_id"]
        assert diag_info["module_name"] != info["module_name"]
        assert diag_info["name"] != info["name"]
        assert diag_info["surname"] != info["surname"]
        assert diag_info["latitude"] != info["latitude"]
        assert diag_info["longitude"] != info["longitude"]
        assert diag_info["place"] != info["place"]
        assert diag_info["notes"] != info["notes"]


async def test_diagnostics_nohide():
    """Test the Diagnostics Data comes back correctly."""
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

        diag_data = controller.get_diagnostics_data(hide_sensitive=False)
        # Verify Sensitive Data:

        info = controller.get_device_info("1234", "1")
        diag_info = diag_data["1234_1"]["info"]
        assert diag_info["module_id"] == info["module_id"]
        assert diag_info["module_name"] == info["module_name"]
        assert diag_info["name"] == info["name"]
        assert diag_info["surname"] == info["surname"]
        assert diag_info["latitude"] == info["latitude"]
        assert diag_info["longitude"] == info["longitude"]
        assert diag_info["place"] == info["place"]
        assert diag_info["notes"] == info["notes"]
