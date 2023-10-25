"""Main Program, for Testing Mainly."""
import argparse
import asyncio
import getpass
import json
import logging

from natsort import natsorted

from aiohttp import ClientSession, ClientTimeout

from masterthermconnect.__version__ import __version__
from masterthermconnect.api import MasterthermAPI
from masterthermconnect.controller import MasterthermController
from masterthermconnect.exceptions import MasterthermError

_LOGGER: logging.Logger = logging.getLogger(__name__)


def guess_type(value: str) -> any:
    """Convert an Augument Type to a best guess format."""
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
    return value


def get_arguments(argv) -> argparse.Namespace:
    """Read the Arguments passed in."""
    # formatter_class=argparse.MetavarTypeHelpFormatter,
    parser = argparse.ArgumentParser(
        prog="masterthermconnect",
        description=(
            "Python Mastertherm Connect API Module, used for debug purposes, "
            "allows you to get and set registers and other information for testing, "
            "use with caution!!!"
        ),
        epilog=(
            "DO NOT RUN THIS TOO FREQENTLY, IT IS POSSIBLE TO GET YOUR IP BLOCKED, "
            "I think new new API is sensitive to logging in too frequently."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Mastertherm Connect API Version: " + __version__,
        help="display the Mastertherm Connect API version",
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="Print debugging statements.",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Print verbose statements.",
        action="store_const",
        dest="loglevel",
        const=logging.INFO,
    )

    # Sub Commands are get and set:
    subparsers = parser.add_subparsers(
        title="commands",
        description=(
            "Valid commands to access the API, use -h to get "
            "more help after the command for specific help."
        ),
        help="Retrieve and Send data to or from the API.",
    )

    # Get has opitions for user/ password/ api-ver/ sensitive info and pretty
    parser_get = subparsers.add_parser(
        "get", help="Read data from the API and Display it"
    )

    parser_get.set_defaults(command="get")
    parser_get.add_argument("--user", type=str, help="login user for Mastertherm")
    parser_get.add_argument(
        "--password", type=str, help="login password for Mastertherm"
    )
    parser_get.add_argument(
        "--api-ver",
        type=str,
        choices=["v1", "v2"],
        default="v1",
        help="API Version to use: Default: v1 (pre 2022), v2 (post 2022)",
    )
    parser_get.add_argument(
        "--hide-sensitive",
        action="store_true",
        help="Hide the actual sensitive information, "
        + "used when creating debug information for sharing.",
    )
    parser_get.add_argument(
        "--pretty",
        action="store_true",
        help="Prettify the Output in JSON Format.",
    )

    subparser_get = parser_get.add_subparsers(title="get commands", required=True)
    parser_getdevice = subparser_get.add_parser(
        "devices", help="All Devices List associated with the account."
    )
    parser_getdevice.set_defaults(subcommand="devices")

    parser_getdata = subparser_get.add_parser(
        "data",
        help="Normalized data for a speicif device, e.g. data 1234 1",
    )
    parser_getdata.set_defaults(subcommand="data")
    parser_getdata.add_argument("module_id", type=str, help="Module ID e.g. 1234")
    parser_getdata.add_argument("unit_id", type=str, help="Unit Id e.g. 1")

    parser_getreg = subparser_get.add_parser(
        "reg",
        help=(
            "Registers for a specific device, "
            "e.g. get reg 1234 1 A_101,A102 or reg 1234 1 all"
        ),
    )
    parser_getreg.set_defaults(subcommand="reg")
    parser_getreg.add_argument("module_id", type=str, help="Module ID e.g. 1234")
    parser_getreg.add_argument("unit_id", type=str, help="Unit Id e.g. 1")
    parser_getreg.add_argument(
        "reg",
        type=str,
        help="List Registers e.g. A_330 or A_330,A_331 or 'all' for everything.",
    )

    # Set has opitions for user/ password/ api-ver
    parser_set = subparsers.add_parser(
        "set", help="Set data to the API and check the Result"
    )

    parser_set.set_defaults(command="set")
    parser_set.add_argument("--user", type=str, help="login user for Mastertherm")
    parser_set.add_argument(
        "--password", type=str, help="login password for Mastertherm"
    )
    parser_set.add_argument(
        "--api-ver",
        type=str,
        choices=["v1", "v2"],
        default="v1",
        help="API Version to use: Default: v1 (pre 2022), v2 (post 2022)",
    )

    subparser_set = parser_set.add_subparsers(title="set commands", required=True)
    parser_setreg = subparser_set.add_parser(
        "reg",
        help="Registers for a specific device, e.g. reg 1234 1 D_3 0",
    )
    parser_setreg.set_defaults(subcommand="reg")
    parser_setreg.add_argument("--force", action="store_true", help="Force Update.")
    parser_setreg.add_argument("module_id", type=str, help="Module ID e.g. 1234")
    parser_setreg.add_argument("unit_id", type=str, help="Unit Id e.g. 1")
    parser_setreg.add_argument("reg", type=str, help="Register to Set")
    parser_setreg.add_argument(
        "value", type=str, help="Value to Set, all values are set as strings"
    )

    parser_setdata = subparser_set.add_parser(
        "data",
        help=(
            "Data for a specific device, e.g. reg 1234 1 hp_power_state true"
            " or reg 1234 1 heating_circuits.hc0.on true "
            "Acceptable values are string, boolean, float or integer."
        ),
    )
    parser_setdata.set_defaults(subcommand="data")
    parser_setdata.add_argument("module_id", type=str, help="Module ID e.g. 1234")
    parser_setdata.add_argument("unit_id", type=str, help="Unit Id e.g. 1")
    parser_setdata.add_argument(
        "data", type=str, help="Data to Set using dot notation for parent child."
    )
    parser_setdata.add_argument(
        "value",
        type=guess_type,
        help="Value to Set, all values are string, boolean, float or integer.",
    )

    return parser.parse_args(argv)


async def connect(
    username: str, password: str, api_version: str, refresh: bool
) -> MasterthermController:
    """Connect to the Mastertherm Server."""
    # Login to the Server.
    session = ClientSession(timeout=ClientTimeout(total=10))
    controller = MasterthermController(
        username, password, session, api_version=api_version
    )

    try:
        await controller.connect()
        if refresh:
            await controller.refresh()
    except MasterthermError as mte:
        _LOGGER.error("Error %s", mte.message)
    finally:
        await session.close()

    return controller


# ruff: noqa: T201
async def set_reg(
    username: str,
    password: str,
    api_version: str,
    module_id: str,
    unit_id: str,
    register: str,
    value: str,
) -> bool:
    """Connect to the MasterthermAPI."""
    session = ClientSession()

    success = False
    try:
        api = MasterthermAPI(username, password, session, api_version=api_version)
        await api.connect()
        await api.get_device_data(module_id, unit_id)

        success = await api.set_device_data(module_id, unit_id, register, value)
        if success:
            data = await api.get_device_data(module_id, unit_id)
            print(
                f"Registration after Update: "
                f"{register} = {data['data']['varData'][unit_id.zfill(3)][register]}"
            )
        else:
            _LOGGER.error("Failed to Set the Device Registry.")
    except MasterthermError as mte:
        _LOGGER.error("Error %s", mte.message)
    finally:
        await session.close()

    return success


async def set_data(
    username: str,
    password: str,
    api_version: str,
    module_id: str,
    unit_id: str,
    data: str,
    value: any,
) -> bool:
    """Connect to the MasterthermController to set data."""
    session = ClientSession(timeout=ClientTimeout(total=10))

    success = False
    try:
        controller = MasterthermController(
            username, password, session, api_version=api_version
        )
        controller.set_refresh_rate(data_refresh_seconds=0)
        await controller.connect()
        await controller.refresh()

        success = await controller.set_device_data_item(module_id, unit_id, data, value)
        if success:
            await controller.refresh(full_load=True)
            updated_item = controller.get_device_data_item(module_id, unit_id, data)
            print(f"Data after Update: {data} = {updated_item}")
        else:
            _LOGGER.error("Failed to Set the Device Data.")
    except MasterthermError as mte:
        _LOGGER.error("Error %s", mte.message)
    finally:
        await session.close()

    return success


async def set_command(login_user: str, login_pass: str, args) -> int:
    """Set Command to set data/registry."""
    if args.subcommand == "reg":
        force = args.force
        if not force:
            force = (
                input(
                    "Setting untested registry setitngs can break your system. "
                    "Using this feature is entirely at your risk. "
                    "Type Yes to Continue: "
                )
                == "Yes"
            )

        if force:
            if not await set_reg(
                login_user,
                login_pass,
                args.api_ver,
                args.module_id,
                args.unit_id,
                args.reg,
                args.value,
            ):
                _LOGGER.error(
                    "Set Register Command Failed, %s == %s", args.reg, args.value
                )
                return 2
    elif args.subcommand == "data":
        if not await set_data(
            login_user,
            login_pass,
            args.api_ver,
            args.module_id,
            args.unit_id,
            args.data,
            args.value,
        ):
            _LOGGER.error("Set Data Command Failed, %s == %s", args.data, args.value)
            return 2

    return 0


async def get_command(login_user: str, login_pass: str, args) -> int:
    """Get Command to get data/ registry/ devices."""
    controller = await connect(login_user, login_pass, args.api_ver, True)
    if controller is None:
        _LOGGER.error("Connection Failed.")
        return 1

    if args.subcommand == "devices":
        devices = controller.get_devices()
        new_module_id = 1111
        old_module_id = ""
        new_devices = {}

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

            new_devices[device_id] = device_item

        if args.pretty:
            print(json.dumps(new_devices, indent=4))
        else:
            print(str(new_devices).replace("'", '"'))
    elif args.subcommand == "data":
        module_id = args.module_id
        unit_id = args.unit_id
        device_data = controller.get_device_data(module_id, unit_id)
        if args.pretty:
            print(json.dumps(device_data, indent=4))
        else:
            print(
                str(device_data)
                .replace("'", '"')
                .replace("True", "true")
                .replace("False", "false")
            )
    elif args.subcommand == "reg":
        module_id = args.module_id
        unit_id = args.unit_id
        device_reg = controller.get_device_registers(module_id, unit_id)

        sorted_reg = {}
        for key in natsorted(device_reg.keys()):
            sorted_reg[key] = device_reg[key]

        reg: str = args.reg
        if reg.upper() == "ALL":
            if args.pretty:
                print(json.dumps(sorted_reg, indent=4))
            else:
                print(str(sorted_reg).replace("'", '"'))
        elif reg.find(",") == -1:
            print(reg + " = " + sorted_reg.get(reg, "Not Found"))
        else:
            for key in reg.split(","):
                print(key + " = " + sorted_reg.get(key, "Not Found"))

    return 0


def main(argv=None) -> int:
    """Allow for testing connectivity from the command line."""
    # Arg Parse raises SystemExit, get return value
    try:
        args: argparse.Namespace = get_arguments(argv)
    except SystemExit as ex:
        return ex.code

    # Check we have any arguments
    try:
        if not args.command:
            return -1
    except Exception:
        print("usage: masterthermconnect -h")
        return 0

    # If User/ Pass is not provided then get from the command line.
    login_user = input("User: ") if args.user is None else args.user
    login_pass = getpass.getpass() if args.password is None else args.password
    logging.basicConfig(level=args.loglevel)

    if args.command == "get":
        return asyncio.run(get_command(login_user, login_pass, args))
    elif args.command == "set":
        return asyncio.run(set_command(login_user, login_pass, args))

    return 0


if __name__ == "__main__":
    exit(main())
