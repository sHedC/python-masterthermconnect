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
