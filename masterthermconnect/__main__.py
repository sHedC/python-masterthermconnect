"""Main Program, for Testing Mainly"""
import argparse
import asyncio
import getpass
import json

from aiohttp import ClientSession

from masterthermconnect.__version__ import __version__
from masterthermconnect.controller import MasterthermController
from masterthermconnect.exceptions import MasterthermError


def get_arguments() -> argparse.Namespace:
    """Read the Arguments passed in."""
    # formatter_class=argparse.MetavarTypeHelpFormatter,
    parser = argparse.ArgumentParser(
        prog="masterthermconnect",
        description="Python Mastertherm Connect API Module, used for debug purposes",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Mastertherm Connect API Version: " + __version__,
        help="display the Mastertherm Connect API version",
    )
    parser.add_argument(
        "--api-ver",
        type=str,
        choices=["v1", "v2"],
        default="v1",
        help="API Version to use: Default: v1 (pre 2022), v2 (post 2022)",
    )
    parser.add_argument(
        "--hide-sensitive",
        action="store_true",
        help="Hide the actual sensitive information, "
        + "used when creating debug information for sharing.",
    )
    parser.add_argument("--user", type=str, help="login user for Mastertherm")
    parser.add_argument("--password", type=str, help="login password for Mastertherm")

    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="list the devices connected to the account",
    )
    parser.add_argument(
        "--list-device-data",
        action="store_true",
        help="list the data for each device connected to the account",
    )
    parser.add_argument(
        "--list-device-reg",
        type=str,
        help="List Registers e.g. A_330 or A_330,A_331 or 'all' for everything.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pritify the Output in JSON Format.",
    )

    arguments = parser.parse_args()
    return arguments


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
    except MasterthermError as mte:
        print("Connection Failed " + mte.message)
    finally:
        await session.close()

    return None


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

    print("DO NOT RUN THIS TOO FREQENTLY, IT IS POSSIBLE TO GET YOUR IP BLOCKED")
    print("The App and Web App run once every 30 seconds.")

    controller = asyncio.run(connect(login_user, login_pass, args.api_ver, True))

    if args.list_devices:
        devices = controller.get_devices()
        new_module_id = 1111
        old_module_id = ""
        for device_id, device_item in devices.items():
            module_id = device_item["module_id"]
            unit_id = device_item["unit_id"]

            if module_id != old_module_id:
                old_module_id = module_id
                new_module_id = new_module_id + 1

            if args.hide_sensitive:
                device_id = f"{str(new_module_id)}_{unit_id}"
                device_item["module_id"] = str(new_module_id)
                device_item["module_name"] = "Hidden Name"
                device_item["name"] = "First"
                device_item["surname"] = "Last"
                device_item["latitude"] = "1.1"
                device_item["longitude"] = "-0.1"

            if args.pretty:
                print(device_id + ": " + json.dumps(device_item, indent=4))
            else:
                print(device_id + ": " + str(device_item).replace("'", '"'))

    if args.list_device_data:
        devices = controller.get_devices()
        new_module_id = 1111
        old_module_id = ""
        for device_id, device_item in devices.items():
            module_id = device_item["module_id"]
            unit_id = device_item["unit_id"]

            device_data = controller.get_device_data(module_id, unit_id)
            if module_id != old_module_id:
                old_module_id = module_id
                new_module_id = new_module_id + 1

            if args.hide_sensitive:
                device_id = f"{str(new_module_id)}_{unit_id}"

            if args.pretty:
                print(device_id + ": " + json.dumps(device_data, indent=4))
            else:
                print(device_id + ": " + str(device_data).replace("'", '"'))

    if args.list_device_reg:
        devices = controller.get_devices()
        new_module_id = 1111
        old_module_id = ""
        for device_id, device_item in devices.items():
            module_id = device_item["module_id"]
            unit_id = device_item["unit_id"]

            device_reg = controller.get_device_registers(module_id, unit_id)
            if module_id != old_module_id:
                old_module_id = module_id
                new_module_id = new_module_id + 1

            if args.hide_sensitive:
                device_id = f"{str(new_module_id)}_{unit_id}"

            sorted_reg = {}
            for key in sorted(device_reg.keys()):
                sorted_reg[key] = device_reg[key]

            reg: str = args.list_device_reg
            if reg.upper() == "ALL":
                print(device_id + ": " + str(sorted_reg).replace("'", '"'))
            elif reg.find(",") == -1:
                print(device_id + ": " + reg + " = " + sorted_reg.get(reg, "Not Found"))
            else:
                for key in reg.split(","):
                    print(
                        device_id
                        + ": "
                        + key
                        + " = "
                        + sorted_reg.get(key, "Not Found")
                    )

    return 0


if __name__ == "__main__":
    main()
