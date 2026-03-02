"""Modbus hub for AlphaESS inverters."""
from __future__ import annotations

import logging

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant

from .const import (
    CONF_SLAVE_ID,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    RegisterType,
)

_LOGGER = logging.getLogger(__name__)


class AlphaESSModbusHub:
    """Manage the Modbus TCP connection to an AlphaESS inverter."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        self._hass = hass
        self._entry = entry
        self._client: AsyncModbusTcpClient | None = None
        self._lock = None  # created lazily to stay in the event loop

    # ---- helpers to read merged config (data + options) ----

    def _cfg(self, key: str, default=None):
        """Return a config value, preferring options over data."""
        opts = getattr(self._entry, "options", None) or {}
        data = getattr(self._entry, "data", None) or {}
        return opts.get(key, data.get(key, default))

    # ---- connection lifecycle ----

    async def async_connect(self) -> bool:
        """Connect (or reconnect) to the inverter. Returns True on success."""
        import asyncio

        if self._lock is None:
            self._lock = asyncio.Lock()

        async with self._lock:
            # Already connected?
            if self._client is not None and self._client.connected:
                return True

            try:
                host = self._cfg(CONF_HOST, "")
                port = self._cfg(CONF_PORT, DEFAULT_PORT)
                self._client = AsyncModbusTcpClient(
                    host=host,
                    port=port,
                    timeout=5,
                )

                connected = await self._client.connect()
                if not connected:
                    _LOGGER.error(
                        "Failed to connect to AlphaESS inverter (%s)",
                        self._cfg(CONF_HOST),
                    )
                    return False

                _LOGGER.debug("Connected to AlphaESS inverter")
                return True

            except Exception:
                _LOGGER.exception("Exception connecting to AlphaESS inverter")
                self._client = None
                return False

    async def async_close(self) -> None:
        """Disconnect from the inverter."""
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                _LOGGER.debug("Exception closing Modbus client", exc_info=True)
            self._client = None

    # ---- read ----

    async def async_read_value(
        self,
        address: int,
        register_type: RegisterType,
        register_count: int | None = None,
    ) -> int | str | None:
        """Read one logical value from the inverter.

        For 32-bit types two consecutive holding registers are read.
        For STRING type, *register_count* consecutive registers are read and
        decoded as ASCII.
        Returns the decoded value, or None on failure.
        """
        if self._client is None or not self._client.connected:
            ok = await self.async_connect()
            if not ok:
                return None

        slave = self._cfg(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

        if register_type == RegisterType.STRING:
            count = register_count or 5
        elif register_type in (RegisterType.INT32, RegisterType.UINT32):
            count = 2
        else:
            count = 1

        try:
            result = await self._client.read_holding_registers(
                address=address, count=count, device_id=slave,
            )

            if result.isError():
                _LOGGER.debug(
                    "Modbus read error at 0x%04X: %s", address, result
                )
                return None

            regs = result.registers

            if register_type == RegisterType.STRING:
                # Decode registers as big-endian ASCII bytes
                raw_bytes = b""
                for r in regs:
                    raw_bytes += r.to_bytes(2, byteorder="big")
                # Strip null bytes and whitespace
                return raw_bytes.decode("ascii", errors="replace").rstrip("\x00").strip()

            if register_type == RegisterType.UINT16:
                return regs[0]

            if register_type == RegisterType.INT16:
                raw = regs[0]
                return raw - 0x10000 if raw >= 0x8000 else raw

            # 32-bit: high word first
            combined = (regs[0] << 16) | regs[1]

            if register_type == RegisterType.UINT32:
                return combined

            # INT32 — two's complement
            if combined >= 0x80000000:
                return combined - 0x100000000
            return combined

        except ModbusException as exc:
            _LOGGER.debug("Modbus exception reading 0x%04X: %s", address, exc)
            return None
        except Exception:
            _LOGGER.exception("Unexpected error reading register 0x%04X", address)
            return None

    # ---- write ----

    async def async_write_register(self, address: int, value: int) -> bool:
        """Write a single holding register. Returns True on success."""
        if self._client is None or not self._client.connected:
            ok = await self.async_connect()
            if not ok:
                return False

        slave = self._cfg(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

        try:
            result = await self._client.write_register(
                address=address, value=value, device_id=slave,
            )
            if result.isError():
                _LOGGER.error(
                    "Modbus write error at 0x%04X: %s", address, result
                )
                return False
            return True

        except ModbusException as exc:
            _LOGGER.error("Modbus exception writing 0x%04X: %s", address, exc)
            return False
        except Exception:
            _LOGGER.exception("Unexpected error writing register 0x%04X", address)
            return False

    async def async_write_registers(self, address: int, values: list[int]) -> bool:
        """Write multiple consecutive holding registers. Returns True on success."""
        if self._client is None or not self._client.connected:
            ok = await self.async_connect()
            if not ok:
                return False

        slave = self._cfg(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)

        try:
            result = await self._client.write_registers(
                address=address, values=values, device_id=slave,
            )
            if result.isError():
                _LOGGER.error(
                    "Modbus write error at 0x%04X (%d regs): %s",
                    address, len(values), result,
                )
                return False
            return True

        except ModbusException as exc:
            _LOGGER.error(
                "Modbus exception writing 0x%04X (%d regs): %s",
                address, len(values), exc,
            )
            return False
        except Exception:
            _LOGGER.exception(
                "Unexpected error writing %d registers at 0x%04X",
                len(values), address,
            )
            return False
