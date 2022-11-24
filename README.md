# MaseterTherm Connect Module
[![License][license-shield]](LICENSE)
![Project Maintenance][maintenance-shield]
[![GitHub Activity][commits-shield]][commits]

Stable -
[![GitHub Release][stable-release-shield]][releases]
[![workflow-stable]][workflows]

Latest -
[![GitHub Release][latest-release-shield]][releases]
[![workflow-latest]][workflows]

## About
This module provides the connection and conversion tools to the API for the Mastertherm Heatpump Products.
The project was mainly built for a Plugin to Home Assistant.

There are two entry points for the Mastertherm Heat Pumps:
    - mastertherm.vip-it.cz - This is the server for pre 2022 heat pumps
    - mastertherm.online - This is the server for 2022 onward

NOTE: mastertherm.online is sensitive to too many

## Installation
python -m pip install masterthermconnect

## Usage
This is used as a libary but it can also be run directly for debug purposes:

usage: masterthermconnect [-h] [--version] [--api-ver {v1,v2}] [--hide-sensitive] [--user USER] [--password PASSWORD] [--list-devices] [--list-device-data] [--list-device-reg]

Python Mastertherm Connect API Module, used for debug purposes.<br>
options:<br>
&nbsp;&nbsp;-h, --help           show this help message and exit<br>
&nbsp;&nbsp;--version            display the Mastertherm Connect API version<br>
&nbsp;&nbsp;--api-ver {v1,v2}    API Version to use: Default: v1 (pre 2022), v2 (post 2022)<br>
&nbsp;&nbsp;--hide-sensitive     Hide the sensitive information, for debug information for sharing.<br>
&nbsp;&nbsp;--user USER          login user for Mastertherm<br>
&nbsp;&nbsp;--password PASSWORD  login password for Mastertherm<br>
&nbsp;&nbsp;--list-devices       list the devices connected to the account<br>
&nbsp;&nbsp;--list-device-data   list the data for each device connected to the account<br>
&nbsp;&nbsp;--list-device-reg    list the raw registers for each device<br>



***
[commits-shield]: https://img.shields.io/github/commit-activity/y/sHedC/python-masterthermconnect?style=for-the-badge
[commits]: https://github.com/shedc/python-masterthermconnect/commits/main
[license-shield]: https://img.shields.io/github/license/shedc/python-masterthermconnect?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-Richard%20Holmes%20%40shedc-blue.svg?style=for-the-badge

[releases]: https://github.com/shedc/python-masterthermconnect/releases
[stable-release-shield]: https://img.shields.io/github/v/release/shedc/python-masterthermconnect?style=flat
[latest-release-shield]: https://img.shields.io/github/v/release/shedc/python-masterthermconnect?include_prereleases&style=flat

[workflows]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/python-app.yml/badge.svg
[workflow-stable]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/python-app.yml/badge.svg?branch=main
[workflow-latest]: https://github.com/sHedC/python-masterthermconnect/actions/workflows/python-app.yml/badge.svg
