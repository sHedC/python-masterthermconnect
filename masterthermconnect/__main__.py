"""Main Program, for Testing Mainly"""
import argparse
import asyncio
import getpass
import time

from aiohttp import ClientSession

from masterthermconnect.__version__ import __version__
from masterthermconnect.controller import MasterthermController
from masterthermconnect.exceptions import MasterthermError


def get_arguments() -> argparse.Namespace:
    """Read the Arguments passed in."""
    parser = argparse.ArgumentParser(
        prog="masterthermconnect",
        description="Python Mastertherm Connect API Module.",
        formatter_class=argparse.MetavarTypeHelpFormatter,
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Mastertherm Connect API Version: " + __version__,
        help="display the Mastertherm Connect API version",
    )
    parser.add_argument("--user", type=str, help="login user for Mastertherm")
    parser.add_argument(
        "--password", type=str, default=None, help="login password for Mastertherm"
    )
    parser.add_argument(
        "--api-version",
        type=str,
        default="v1",
        help="""API Version to use:
             mastertherm.vip-it.cz: v1 (early) or v1b (laster),
             mastertherm.online: or v2 (post 2022)""",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="list the devices connected to the account",
    )
    parser.add_argument(
        "--list-device-info",
        action="store_true",
        help="list the information for each device connected to the account",
    )
    parser.add_argument(
        "--list-device-data",
        action="store_true",
        help="list the data for each device connected to the account",
    )

    arguments = parser.parse_args()
    return arguments


async def list_devices(user, password, api_version) -> int:
    """List Devices after Connection"""
    session = ClientSession()
    controller = MasterthermController(user, password, session, api_version=api_version)

    try:
        await controller.connect()
    except MasterthermError as mte:
        print("Connection Failed " + mte.message)
        return mte.status

    print(controller.get_devices())

    await session.close()
    return 0


async def list_device_info(user, password, api_version) -> int:
    """List the Information related to the devices."""
    session = ClientSession()
    controller = MasterthermController(user, password, session, api_version=api_version)

    try:
        await controller.connect()
    except MasterthermError as mte:
        print("Connection Failed " + mte.message)
        return mte.status

    devices = controller.get_devices()
    for device_id, device_item in devices.items():
        print("Device - " + device_id)
        print(
            controller.get_device_info(device_item["module_id"], device_item["unit_id"])
        )

    await session.close()
    return 0


async def list_device_data(user, password, api_version) -> int:
    """List the Data related to the devices."""
    session = ClientSession()
    controller = MasterthermController(user, password, session, api_version=api_version)

    try:
        await controller.connect()
    except MasterthermError as mte:
        print("Connection Failed " + mte.message)
        return mte.status

    devices = controller.get_devices()
    for device_id, device_item in devices.items():
        print("Device - " + device_id)
        print(
            controller.get_device_data(device_item["module_id"], device_item["unit_id"])
        )

    # Old API has 10 hours before token expires 36,000 seconds
    i = 36000
    while i > 0:
        print(f"Waiting Remaining i={str(i)} seconds")
        devices = await controller.refresh()
        time.sleep(600)
        i -= 600

    time.sleep(600)
    devices = await controller.refresh()

    await session.close()
    return 0


def main() -> int:
    """Allow for some testing of connections from Command Line."""
    login_user = ""
    login_pass = ""
    args = get_arguments()

    if args.user is not None:
        login_user = args.user
    else:
        login_user = input("User: ")

    if args.password is not None:
        login_pass = args.password
    else:
        login_pass = getpass.getpass()

    api_version = args.api_version

    if args.list_devices:
        asyncio.run(list_devices(login_user, login_pass, api_version))

    if args.list_device_info:
        asyncio.run(list_device_info(login_user, login_pass, api_version))

    if args.list_device_data:
        asyncio.run(list_device_data(login_user, login_pass, api_version))

    return 0


if __name__ == "__main__":
    main()
