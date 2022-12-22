# MaseterTherm Connect Module
[![License][license-shield]](LICENSE)
![Project Maintenance][maintenance-shield]
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
This module provides the connection and conversion tools to the API for the Mastertherm Heatpump Products.
The project was mainly built for a Plugin to Home Assistant.

There are two entry points for the Mastertherm Heat Pumps:
    - mastertherm.vip-it.cz - This is the server for pre 2022 heat pumps
    - mastertherm.online - This is the server for 2022 onward

NOTES:
    - materhterm.online is sensitive to too many requests, for this reason by default it defaults to updates every 10 minutes, the App updates every 2 minutes. To help the Info updates every 30 min and data can be set in the options.
    - if multiple requests are sent at the same time (i.e. from home assistant/ the app and web) some will be refused by the servers, its temporary.  The updates have been built to report but ignore these.

## Installation
Latest Release Version: python -m pip install masterthermconnect
Specific Version or Pre-Release: python -m pip install masterthermconnect==1.1.0rc2

## Usage

### Command Line
This is used as a libary but it can also be run directly for debug purposes:

DO NOT RUN THIS TOO FREQUENTLY, the new API may lock you're IP out.  The app and web app refresh every 30 seconds. I don't know how many times in succession would lock you out, probably frequent calls over a period of time such as an hour.

usage: masterthermconnect [-h] [--version] [--api-ver {v1,v2}] [--hide-sensitive] [--user USER] [--password PASSWORD] [--list-devices] [--list-device-data] [--list-device-reg]

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

### API Version
TBC


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
