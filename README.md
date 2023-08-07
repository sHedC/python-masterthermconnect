# Mastertherm Connect Module
[![License][license-shield]](LICENSE)
[![GitHub Activity][commits-shield]][commits]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

Main -
[![workflow-main][workflow-main-shield]][workflow-main-link]
[![codecov][codecov-shield]][codecov-link]
[![issues][issues-shield]][issues-link]

Latest -
[![GitHub Release][latest-release-shield]][releases]
[![workflow-latest][workflow-latest-shield]][workflow-latest-link]

Stable -
[![GitHub Release][stable-release-shield]][releases]
[![workflow-stable][workflow-stable-shield]][workflow-stable-link]

## About
This module provides the connection and conversion for the two Mastertherm Heat Pump APIs. It is being developed as a best effort to support an integration plugin for Home Assistant.

There are two entry points for the Mastertherm Heat Pumps:
- mastertherm.vip-it.cz - This is the server for pre 2022 heat pumps
- mastertherm.online - This is the server for 2022 onward

NOTES:
- materhterm.online is sensitive to too many requests so take care when using the command line or using this libary. The Application and Web App does a refresh on one module/ unit every 30 seconds.
- if multiple requests are sent at the same time (i.e. from home assistant/ the app and web) some will be refused by the servers, its temporary.  The updates have been built to report but ignore these.


## Installation
Releases are done using PyPi, the release is here: <a href="https://pypi.org/project/masterthermconnect" target="_blank">masterthermconnect</a>
- Latest Release Version: python -m pip install masterthermconnect
- Specific Version or Pre-Release e.g.: python -m pip install masterthermconnect==1.1.0rc9

### Command Line
This is used as a libary but it can also be run directly for debug purposes and must be used with extreme caution, especially when using the set commands.

> :warning: **Use SET with REG directly with extreme caution**: There is no protection on the masterhterm API Web for updating registry settings you must not and updating these can break your system, this applies to using the mastertherm set & reg command you have to actively confirm each set command when using this feature.

> :warning: **Do Not Run This Too Frequently**: The new API may lock you're IP out for an unknown period of time.  The app and web app refresh every 30 seconds. I don't know how many times in succession would lock you out, probably frequent calls over a period of time such as an hour.

```
usage: masterthermconnect [-h] [--version] [-d] [-v] {get,set} ...

Python Mastertherm Connect API Module, used for debug purposes, allows you to get and set registers and other information for testing, use with
caution!!!

options:
  -h, --help        show this help message and exit
  --version         display the Mastertherm Connect API version
  -d, --debug       display Debug Logging
  -v, --verbose     display Verbose/ Info logging

commands:
  Valid commands to access the API, use -h to get more help after the command for specific help.

  {get,set}         Retrieve and Send data to or from the API.
    get             Read data from the API and Display it
    set             Set data to the API and check the Result

DO NOT RUN THIS TOO FREQENTLY, IT IS POSSIBLE TO GET YOUR IP BLOCKED, I think new new API is sensitive to logging in too frequently.
```

Get
```
usage: masterthermconnect get [-h] [--user USER] [--password PASSWORD] [--api-ver {v1,v2}] [--hide-sensitive] [--pretty] {devices,data,reg} ...

options:
  -h, --help           show this help message and exit
  --user USER          login user for Mastertherm
  --password PASSWORD  login password for Mastertherm
  --api-ver {v1,v2}    API Version to use: Default: v1 (pre 2022), v2 (post 2022)
  --hide-sensitive     Hide the actual sensitive information, used when creating debug information for sharing.
  --pretty             Prettify the Output in JSON Format.

get commands:
  {devices,data,reg}
    devices            All Devices List associated with the account.
    data               Normalized data for a speicif device, e.g. data 1234 1
    reg                Registers for a specific device, e.g. get reg 1234 1 A_101,A102 or reg 1234 1 all
```

Set
```
usage: masterthermconnect set [-h] [--user USER] [--password PASSWORD] [--api-ver {v1,v2}] {reg} ...

options:
  -h, --help           show this help message and exit
  --user USER          login user for Mastertherm
  --password PASSWORD  login password for Mastertherm
  --api-ver {v1,v2}    API Version to use: Default: v1 (pre 2022), v2 (post 2022)

set commands:
  {reg}
    reg                Registers for a specific device, e.g. reg 1234 1 D_3 0
```

If you can login using mastertherm.online then use the api version v2, for mastertherm.vip-it.cz use v1 or do not provide. If you use special characters or spaces in user name or password use double quotes "user name" to quote the parameter.

### API Version
For examples on how to use the API please see `__main__.py` file as an exmaple, it is quite simple to use and retrieve information and is documented inline:

> :warning: **Do NOT use the MasterthermAPI Directly**: There is no control on updating registries using the API and updating the wrong one can break your system.  The MasterthermController has controls to only allow certain updates that are avialable on the Web UI and Thermostats.

To import the required modules:
```
from masterthermconnect import (
    MasterthermController,
    MasterthermAuthenticationError,
    MasterthermConnectionError,
    MasterthermResponseFormatError,
    MasterthermTokenInvalid,
    MasterthermUnsupportedRole,
    MasterthermUnsupportedVersion,
)
```

To setup a connection create a new aiohttp ClientSession and pass the login details:
```
    async def connect(
        username: str, password: str, api_version: str, refresh: bool
    ) -> MasterthermController:
        """Setup and Connect to the Mastertherm Server."""
        # Login to the Server.
        session = ClientSession()
        controller = MasterthermController(
            username, password, session, api_version=api_version
        )

        try:
            await controller.connect()
            if refresh:
                await controller.refresh()

            return controller
        except MasterthermAutenticationError as mte:
            print("Authentication Failed " + mte.message)
        except MaseterthermConnectionError as mte:
            print("Connection Failed " + mte.message)
        finally:
            await session.close()

        return None
```

Device Information and Data can be retrieved from the controller for example. Data is available in a dictionary format described below:
```
     devices = controller.get_devices()
     device_data = controller.get_device_data(module_id, unit_id)
```

## Heat Pump Details
Writes are avaialble in limited capacity based on the UI and Thermostat controls. Some controls have a min/ max value that is configured in the heatpump, whilst we don't have any restrictions built in masterthermconnect the min and max values are available:
- Domestic Hot Water has a min and max temperature exposed
- Heating/ Cooling Curves - have a min/ max in the main heating/ cooling curve

 This is being developed to support the Home Assistant integration.

Everything is based on observations from the Web and Android Applications, the current testing has been done on some basic setup we have not tested options with Solar and Pool but have tried to add sensors based on the apps.
1. One Main circuit with heating and cooling and domestic hot water with attached room thermostats
2. Main Circuit for heating and two optional circuits for Barn and House Domestic Hot Water, no room thermostats

#### Mapping Setup
Pretty much every piece of information and settings are stored as registry keys such as D_110 and I_120, there are hundreds. There is a mapping to the structure used in this module in the const.py.

The data is stored under the controller as an array of module and unit's making a device.

```
{
    "module_id_unit_id": {
        "last_data_update": <datetime> control data update frequency
        "last_info_update": <datetime> control info update frequently
        "last_update_time": "1192282722" used for data updates in the API
        "info":             normallised information for the device
        "data":             normallised data for the devive
        "api_info":         All Info retrieved from the API
        "api_update_data":  All Updated Data since last update
        "api_full_data":    Full Data including last updated
    },
    ...
}
```

The information is stored as key value pairs as below:

```
{
    "name": "givenname",
    "surname": "surname",
    "country": "localization",
    "language": "lang",
    "hp_type": "type",
    "controller": "regulation",
    "exp": "exp",
    "output": "output",
    "reservation": "reservation",
    "place": "city",
    "latitude": "password9",
    "longitude": "password10",
    "notes": "notes",
    "pada": "pada",
    "padb": "padb",
    "padc": "padc",
    "padd": "padd",
    "pade": "pade",
    "padf": "padf",
    "padz": "padz",
}
```

The data is normallies based on the following key value pairs and sub dictionary setup below is the format but exact mappings can be found in the const.py file.

Where possble the normalized data is filtered out based on whether a feature is enabled or not, for example HC0-HC6, Pool and Solar are avaialble only if the circuits are enabled and available.
```
{
    "hp_power_state": ["bool", "D_3"],
    "hp_function": ["int", "I_51"],  # 0: heating, #1: cooling, #2: auto (Write)
    "season": {
        "mode": [
            Special(str, Special.FORMULA),
            [
                "('' if {0} else 'auto-') + ('winter' if {1} else 'summer')",
                [[bool, "I_50"], [bool, "D_24"]],
            ],
        ],
        "manual_set": [bool, "I_50"],
        "winter": [bool, "D_24"],
        "winter_temp": [float, "A_82"],
        "summer_temp": [float, "A_83"],
    },
    "operating_mode": ["fixed", "heating"],  # heating, cooling, pool, dhw, dpc
    "cooling_mode": ["bool", "D_4"],
    "control_curve_heating": {
        "setpoint_a_outside": ["float", "A_122"],
    },
    "control_curve_cooling": {
        "setpoint_a_outside": ["float", "A_362"],
    },
    "domestic_hot_water": {
        "heating": ["bool", "D_66"],
        "enabled": ["bool", "D_275"],
    },
    "compressor_running": ["bool", "D_5"],
    "compressor2_running": ["bool", "D_32"],
    "runtime_info": {
        "compressor_run_time": ["int", "I_11"],
        "compressor_start_counter": ["int", "I_12"],
    },
    "error_info": {
        "some_error": ["bool", "D_20"],
        "three_errors": ["bool", "D_21"],
    },
    "heating_circuits": {}, # Heating and Cooling Circuits
}
```

The Heating/ Cooling Ciruits are optionally installed, HC0 refers to the main heat pump, HC1 to 6 are optional heating and cooling cirguits and additionally there is Pool and Solar as optional components.

In addition each Heating/ Cooling Circuit can have a room thermostat installed or not.  Where possible the sections that are not enabled are removed. Within each of the hc0 to hc6 a room thermostat can be installed if so then the pad sub key is enabled, if not then the int sub key is enabled.

Note Ambient Requested Temperature and Ambient Current Temperatures remain at the hcX level in line with the UI, they should show the correct temperature based on whether a thermostat is installed or not.

Additionally hc0 the control curves are the same as the main cuves so not shown in this section.

```
{
    "hc0": {
        "enabled": boolean Disabled if any of HC1 to HC6 are installed.
        "name": ["string", []],  # hc0 does not have a name, default is Home
        "ambient_temp": ["float", "A_211"],
        "pad": {
            "enabled": ["not bool", "D_242"],  # Seems to be enabled if this is false.
            "current_humidity": ["float", "I_185"],
        },
    },
    "hc1": {
        "enabled": ["fixed", False],
        "name": [
            "string",
            ["I_211", "I_212", "I_213", "I_214", "I_215", "I_216"],
        ],
        "on": ["bool", "D_212"],
        "int": {
            "enabled": ["not bool", "D_245"],
        },
        "ambient_requested": ["if", "D_245", "float", "A_219", "A_215"],
        "ambient_temp": ["float", "A_216"],
        "pad": {
            "enabled": ["bool", "D_245"],
            "state": ["int", "I_15"],  # 0 - Permanently Off, 1 - Scheduled Off, 2 - On
            "current_humidity": ["float", "I_219"],
        },
        "control_curve_heating": {
            "setpoint_a_outside": ["float", "A_101"],
        },
        "control_curve_cooling": {
            "setpoint_a_outside": ["float", "A_314"],
        },
    },
    .
    .
    .
    "solar": {
        "enabled": ["bool", "D_433"],
        "name": ["fixed", "Solar"],
    },
    "pool": {
        "enabled": ["bool", "D_348"],
        "name": ["fixed", "Pool"],
    },
}
```

***
[commits-shield]: https://img.shields.io/github/commit-activity/y/sHedC/python-masterthermconnect?style=for-the-badge
[commits]: https://github.com/shedc/python-masterthermconnect/commits/main
[license-shield]: https://img.shields.io/github/license/shedc/python-masterthermconnect?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Richard%20Holmes%20%40shedc-blue.svg?style=for-the-badge

[buymecoffee]: https://www.buymeacoffee.com/sHedC
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge

[codecov-shield]: https://codecov.io/gh/sHedC/python-masterthermconnect/branch/main/graph/badge.svg?token=747WODRAGO
[codecov-link]: https://codecov.io/gh/sHedC/python-masterthermconnect

[issues-shield]: https://img.shields.io/github/issues/shedc/python-masterthermconnect?style=flat
[issues-link]: https://github.com/sHedC/python-masterthermconnect/issues

[releases]: https://github.com/shedc/python-masterthermconnect/releases
[stable-release-shield]: https://img.shields.io/github/v/release/shedc/python-masterthermconnect?style=flat
[latest-release-shield]: https://img.shields.io/github/v/release/shedc/python-masterthermconnect?include_prereleases&style=flat

[workflow-main-shield]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-main.yml/badge.svg
[workflow-main-link]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-main.yml
[workflow-stable-shield]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-release.yml/badge.svg
[workflow-stable-link]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-release.yml
[workflow-latest-shield]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-prerelease.yml/badge.svg
[workflow-latest-link]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-prerelease.yml
