"""This provides an API for the Modbus local access."""

import logging

from pymodbus.client import AsyncModbusTcpClient


_LOGGER: logging.Logger = logging.getLogger(__name__)


class MasterthermModbus:
    """Modbus API for Mastertherm Heatpumps."""

    def __init__(self, addr: str) -> None:
        """Initialise the Modbus API."""
        self._addr = addr

    async def _read_a_registers(self, slave: int) -> dict[str, any]:
        """Read the Registers for A and map."""
        reg: dict[str, any] = {}

        return reg

    async def _read_i_registers(self, slave: int) -> dict[str, any]:
        """Read the Registers for I and map."""
        reg: dict[str, any] = {}

        return reg

    async def _read_d_registers(self, slave: int) -> dict[str, any]:
        """Read the Registers for D and map."""
        reg: dict[str, any] = {}

        return reg

    async def connect(self) -> bool:
        """Connect to the Modbus Client."""
        client = AsyncModbusTcpClient(self._addr)
        try:
            await client.connect()
        except Exception as e:
            _LOGGER.error(f"Error connecting to Modbus: {e}")
            return False

        return True

    async def close(self) -> None:
        """Close the Modbus Client."""
        return

    async def get_registers(self, slave: int) -> dict[str, any]:
        """Read All A, D and I Registers and return."""
        reg: dict[str, any] = {}
        reg.update[await self._read_a_registers(slave)]
        reg.update[await self._read_d_registers(slave)]
        reg.update[await self._read_i_registers(slave)]

        return reg
