# MaseterTherm Connect Module
[![License][license-shield]](LICENSE)
[![GitHub Activity][commits-shield]][commits]

Main -
[![workflow-main]][workflows-main]

Latest -
[![GitHub Release][latest-release-shield]][releases]
[![workflow-latest]][workflows-latest]

Stable -
[![GitHub Release][stable-release-shield]][releases]
[![workflow-stable]][workflows-stable]

## About
If you feel like donating to a charity, I would love you to sponsor my wife and the Salvation Army here:
<a href="https://www.justgiving.com/fundraising/jackie-holmes1933"><img src="images/salvationarmy.jpg" alt="Charity Link" style="width:125px;height:20px;"></a>


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
This is used as a libary but it can also be run directly for debug purposes:

DO NOT RUN THIS TOO FREQUENTLY, the new API may lock you're IP out for an unknown period of time.  The app and web app refresh every 30 seconds. I don't know how many times in succession would lock you out, probably frequent calls over a period of time such as an hour.

usage: masterthermconnect [-h] [--version] [--api-ver {v1,v2}] [--hide-sensitive] [--user USER] [--password PASSWORD] [--list-devices] [--list-device-data] [--list-device-reg LIST_DEVICE_REG] [--pretty]

Python Mastertherm Connect API Module, used for debug purposes.<br>
options:<br>
&nbsp;&nbsp;-h, --help                          show this help message and exit<br>
&nbsp;&nbsp;--version                           display the Mastertherm Connect API version<br>
&nbsp;&nbsp;--api-ver {v1,v2}                   API Version to use: Default: v1 (pre 2022), v2 (post 2022)<br>
&nbsp;&nbsp;--hide-sensitive                    Hide the sensitive information, for debug information for sharing.<br>
&nbsp;&nbsp;--user USER                         login user for Mastertherm<br>
&nbsp;&nbsp;--password PASSWORD                 login password for Mastertherm<br>
&nbsp;&nbsp;--list-devices                      list the devices connected to the account<br>
&nbsp;&nbsp;--list-device-data                  list the data for each device connected to the account<br>
&nbsp;&nbsp;--list-device-reg LIST_DEVICE_REG   list Registers e.g. A_330 or A_330,A_331 or 'all' for everything.<br>
&nbsp;&nbsp;---pretty                           Pritify the Output in JSON Format.<br>

If you can login using mastertherm.online then use the api version v2, for mastertherm.vip-it.cz use v1 or do not provide.

### API Version
TBC

## Sensor Details
Current version is read only, updates do not work but that will come.

The sensors are based on observations from the Web and Android Applications, the current testing has been done on some basic setup we have not tested options with Solar and Pool but have tried to add sensors based on the apps.
1. One Main circuit with heating and cooling and domestic hot water with attached room thermostats
2. Main Circuit for heating and two optional circuits for Barn and House Domestic Hot Water, no room thermostats

#### Main Circuit
These are the main entities for the heat pump, currently we understand the following.

Entity | Type | Description
-- | -- | --
hp_power_state | Switch | Turn on and off the Heat Pump
hp_function | Select | The function is heating/ cooling or auto
season | Sensor | Shows the Season, Winter or Summer or Auto Winter and Auto Summer
operating_mode | Sensor | The current Operating Mode which shows 5 states: heating/ cooling/ pool/ hot water and defrost protection
cooling_mode | Binary Sensor | Whether the pump is in cooling mode or not (if not its heating)
compressor_running | Binary Sensor | Main compressor running
compressor2_running | Binary Sensor | Compressor 2 if installed
circulation_pump_running | Binary Sensor | Circulating water to where it is being requested, this is always true if any circuit is requesting heating or cooling
fan_running | Binary Sensor | Internal Fan is running
defrost_mode | Binary Sensor | If the heat pump is in defrost mode
aux_heater_1 | Binary Sensor | If installed indicates if the auxillary heater is on
aux_heater_2 | Binary Sensor | If installed indicates if the second auxillary heater is on
outside_temp | Sensor | The outside temperature
requested_temp | Sensor | This is the temperature that the heat pump is requesting, it is calcuated by an unknown algorithm and can go higher than expected. An example here is when heating is initially requested it goes higher than needed then reduces as room temperature is reached.
dewp_control | Binary Sensor | If Dew Point Control is active
hdo_on | Binary Sensor | Something to do with High Tarrif Rates, do not know about this indicator

#### Domestic Hot Water
Entity | Type | Description
-- | -- | --
heating | Binary Sensor | Whether hot water is requested, also activates if HC1 to 6 is for hot water
enabled | Binary Sensor | Not sure on mine always shows disabled.
current_temp | Sensor | The current temperature of the hot water, should be taken from the sensor in the water tank
required_temp | Sensor | The temperature that was set as required for your hot water.

#### Run Time Info
Entity | Type | Description
-- | -- | --
compressor_run_time | Sensor | Number of hours the compressor has run for
compressor_start_counter | Sensor | Probably the number of times the compressor has started
pump_runtime | Sensor | The number of hours the circulation pump has run
aux1_runtime | Sensor | The house the auxillary heaters have run
aux2_runtime | Sensor | The house the auxillary heaters have run

#### Season Info
The switches here define if Winter/ Summer or Auto

Entity | Type | Description
-- | -- | --
hp_season | Switch | If set on then winter, if set off then summer
hp_seasonset | Switch | If set on then Seasion is auto set.

#### Error Info
Work in Progress, error information just decoded from he web application.

Entity | Type | Description
-- | -- | --

#### Heating Circuits
The main circuit is HC0, this is linked to the main pump but some details in this circuit are hidden if any of HC1 to HC6 optional circuits are installed.

HC1 to HC6 are used to provide things like heating/ cooling to different room zones or multiple water tanks for hot water.

Entity | Type | Description
-- | -- | --
name | sensor | The name of the circuit, hc0 is usually Home
on | Swtich | If the circuit is turns on or not
cooling | Binary Sensor | Circuit is in cooling mode
circulation_valve | Binary Sensor | If this circuit is requesting then this is open, this also triggers the main circulation pump
water_requested | Sensor | The requested water temperature based on heating and cooling curves
water_temp | Sensor | The actual water temperature for the circuit
ambient_temp | Sensor | based on the control pannel but not sure this is the right name, still testing
ambient_requested | Sensor | again based on the control pannel but not sure, still testing
auto | Sensor | No idea, it can be set on the thermostats but not sure what it does.

#### Pool and Solar
Some entities have been added based on debugging and best guess.

***
[commits-shield]: https://img.shields.io/github/commit-activity/y/sHedC/python-masterthermconnect?style=for-the-badge
[commits]: https://github.com/shedc/python-masterthermconnect/commits/main
[license-shield]: https://img.shields.io/github/license/shedc/python-masterthermconnect?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Richard%20Holmes%20%40shedc-blue.svg?style=for-the-badge

[releases]: https://github.com/shedc/python-masterthermconnect/releases
[stable-release-shield]: https://img.shields.io/github/v/release/shedc/python-masterthermconnect?style=flat
[latest-release-shield]: https://img.shields.io/github/v/release/shedc/python-masterthermconnect?include_prereleases&style=flat

[workflows-stable]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-release.yml/badge.svg
[workflow-stable]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-release.yml/badge.svg
[workflows-latest]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-prerelease.yml/badge.svg
[workflow-latest]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-prerelease.yml/badge.svg
[workflows-main]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-main.yml/badge.svg
[workflow-main]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/push-main.yml/badge.svg
