"""Main Program, for Testing Mainly"""
import argparse
import asyncio
import getpass

from aiohttp import ClientSession

from masterthermconnect.__version__ import __version__
from masterthermconnect.controller import Controller
from masterthermconnect.exceptions import MasterThermError

def get_arguments() -> argparse.Namespace:
    """Read the Arguments passed in."""
    parser = argparse.ArgumentParser(
        prog="masterthermconnect",
        description="Python MasterTherm Connect API Module.",
        formatter_class=argparse.MetavarTypeHelpFormatter
    )
    parser.add_argument(
        "--version", action="version",
        version="MasterTherm Connect API Version: "+__version__,
        help="display the MasterTherm Connect API version"
    )
    parser.add_argument(
        "--user", type=str,
        help="login user for MasterTherm"
    )
    parser.add_argument(
        "--password", type=str, default=None,
        help="login password for MasterTherm"
    )
    parser.add_argument(
        "--list-devices", action="store_true",
        help="list the devices connected to the account"
    )

    arguments = parser.parse_args()
    return arguments

async def list_devices(user, password) -> int:
    """List Devices after Connection"""
    session = ClientSession()
    controller = Controller(session, user, password)

    try:
        await controller.connect()
    except MasterThermError as mte:
        print("Connection Failed " + mte.message)
        return mte.status

    print(controller.get_devices())

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

    if args.list_devices:
        asyncio.run(list_devices(login_user, login_pass))

    return 0

if __name__ == "__main__":
    main()
