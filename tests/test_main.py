"""Test the Main command."""
import json

from unittest.mock import patch

from masterthermconnect.__main__ import main as MasterthermConnect

from .conftest import VALID_LOGIN, ConnectionMock


def test_help(capsys):
    """Test the Main Help."""
    MasterthermConnect(["--help"])

    out, err = capsys.readouterr()
    assert out.startswith(
        "usage: masterthermconnect [-h] [--version] [-d] [-v] {get,set}"
    )
    assert err == ""


def test_get_help(capsys):
    """Test the Get Help."""
    MasterthermConnect(["get", "-h"])

    out, err = capsys.readouterr()
    assert out.startswith(
        "usage: masterthermconnect get [-h] [--user USER] [--password PASSWORD]"
    )
    assert err == ""


def test_set_help(capsys):
    """Test the Set Help."""
    MasterthermConnect(["set", "-h"])

    out, err = capsys.readouterr()
    assert out.startswith(
        "usage: masterthermconnect set [-h] [--user USER] [--password PASSWORD]"
    )
    assert err == ""


def test_get_v1(capsys):
    """Test the Get devices for v1."""
    mockconnect = ConnectionMock(api_version="v1")

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
        return_code = MasterthermConnect(
            [
                "get",
                "--user",
                VALID_LOGIN["uname"],
                "--password",
                VALID_LOGIN["upwd"],
                "devices",
            ]
        )

        out, err = capsys.readouterr()

    assert len(mock_api_connect.mock_calls) > 0
    assert len(mock_get_device_info.mock_calls) > 0
    assert len(mock_get_device_data.mock_calls) > 0

    assert return_code == 0
    assert err == ""

    devices = json.loads(out.replace("\n", ""))
    assert devices["1234_1"]["module_id"] == "1234"


def test_set_v1(capsys):
    """Test the Get devices for v1."""
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
        return_code = MasterthermConnect(
            [
                "set",
                "--user",
                VALID_LOGIN["uname"],
                "--password",
                VALID_LOGIN["upwd"],
                "data",
                "1234",
                "1",
                "heating_circuits.hc1.ambient_requested",
                "50.1",
            ]
        )

        out, err = capsys.readouterr()

    assert return_code == 0
    assert err == ""
    assert out == "Data after Update: heating_circuits.hc1.ambient_requested = 50.1\n"


def test_set_power(capsys):
    """Test the Set devices for power state."""
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
        return_code = MasterthermConnect(
            [
                "set",
                "--user",
                VALID_LOGIN["uname"],
                "--password",
                VALID_LOGIN["upwd"],
                "data",
                "1234",
                "1",
                "hp_power_state",
                "false",
            ]
        )

        out, err = capsys.readouterr()

    assert return_code == 0
    assert err == ""
    assert out == "Data after Update: hp_power_state = False\n"


def test_set_reg(capsys):
    """Test the Set device registry."""
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
        return_code = MasterthermConnect(
            [
                "set",
                "--user",
                VALID_LOGIN["uname"],
                "--password",
                VALID_LOGIN["upwd"],
                "reg",
                "--force",
                "1234",
                "1",
                "D_3",
                "1",
            ]
        )

        out, err = capsys.readouterr()

    assert return_code == 0
    assert err == ""
    assert out == "Registration after Update: D_3 = 1\n"
