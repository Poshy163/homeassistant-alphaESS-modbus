from __future__ import annotations

import logging

import voluptuous as vol
from pymodbus.client import AsyncModbusTcpClient

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    AC_LIMIT_OPTIONS,
    CONF_AC_LIMIT_KW,
    CONF_MODEL,
    CONF_POLL_FREQ,
    CONF_SLAVE_ID,
    DEFAULT_AC_LIMIT_KW,
    DEFAULT_POLL_FREQ,
    DEFAULT_PORT,
    REG_INVERTER_SN,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    INVERTER_MODELS,
    POLL_FREQUENCY_OPTIONS,
    build_entry_unique_id,
)

DEFAULT_NAME = "AlphaESS"
_LOGGER = logging.getLogger(__name__)


async def _async_read_inverter_serial(host: str, port: int, slave_id: int) -> str | None:
    """Try to read inverter serial number via Modbus (0x064A..0x0653)."""
    client = AsyncModbusTcpClient(host=host, port=port, timeout=5)
    try:
        if not await client.connect():
            return None

        result = await client.read_holding_registers(
            address=REG_INVERTER_SN,
            count=10,
            device_id=slave_id,
        )
        if result.isError():
            return None

        raw_bytes = b"".join(r.to_bytes(2, byteorder="big") for r in result.registers)
        serial = raw_bytes.decode("ascii", errors="replace").rstrip("\x00").strip()
        return serial or None
    except Exception:  # noqa: BLE001
        _LOGGER.debug("Could not read inverter serial during config flow", exc_info=True)
        return None
    finally:
        client.close()


class AlphaESSModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input.get(CONF_HOST, "") or "")
            port = int(user_input.get(CONF_PORT, DEFAULT_PORT))
            slave_id = int(user_input.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID))

            if not host:
                errors["base"] = "invalid_connection"
            elif not user_input.get(CONF_MODEL) or user_input[CONF_MODEL] == "-- Select Inverter --":
                errors["base"] = "invalid_model"
            else:
                serial_number = await _async_read_inverter_serial(host, port, slave_id)
                if serial_number is None:
                    # Inverter unreachable — show warning but allow setup
                    _LOGGER.warning(
                        "Could not connect to inverter at %s:%s to read serial; "
                        "proceeding with TCP-based unique ID",
                        host, port,
                    )
                unique = build_entry_unique_id(host, port, slave_id, serial_number=serial_number)
                await self.async_set_unique_id(unique)
                self._abort_if_unique_id_configured()
                user_input[CONF_NAME] = DEFAULT_NAME
                return self.async_create_entry(title=DEFAULT_NAME, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=self._build_config_schema(),
            errors=errors,
        )

    @staticmethod
    def _build_config_schema() -> vol.Schema:
        """Schema for the initial config flow (all fields)."""
        return vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
                vol.Required(CONF_MODEL): vol.In(INVERTER_MODELS),
                vol.Required(
                    CONF_AC_LIMIT_KW,
                    default=DEFAULT_AC_LIMIT_KW,
                ): vol.In(AC_LIMIT_OPTIONS),
                vol.Required(
                    CONF_POLL_FREQ,
                    default=DEFAULT_POLL_FREQ,
                ): vol.In(POLL_FREQUENCY_OPTIONS),
            }
        )

    @staticmethod
    def _build_options_schema(data: dict, options: dict) -> vol.Schema:
        """Schema for the options flow (pre-filled with current values)."""
        merged = {**data, **options}
        return vol.Schema(
            {
                vol.Required(CONF_HOST, default=merged.get(CONF_HOST, "")): str,
                vol.Required(CONF_PORT, default=merged.get(CONF_PORT, DEFAULT_PORT)): int,
                vol.Required(CONF_SLAVE_ID, default=merged.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)): int,
                vol.Required(CONF_MODEL, default=merged.get(CONF_MODEL)): vol.In(INVERTER_MODELS),
                vol.Required(
                    CONF_AC_LIMIT_KW,
                    default=merged.get(CONF_AC_LIMIT_KW, DEFAULT_AC_LIMIT_KW),
                ): vol.In(AC_LIMIT_OPTIONS),
                vol.Required(
                    CONF_POLL_FREQ,
                    default=merged.get(CONF_POLL_FREQ, DEFAULT_POLL_FREQ),
                ): vol.In(POLL_FREQUENCY_OPTIONS),
            }
        )

    async def async_step_reconfigure(
        self, user_input: dict | None = None
    ) -> FlowResult:
        """Handle reconfiguration of an existing entry."""
        errors: dict[str, str] = {}
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        if entry is None:
            return self.async_abort(reason="unknown")

        if user_input is not None:
            merged = {**entry.data, **user_input}
            if not merged.get(CONF_HOST):
                errors["base"] = "invalid_connection"
            else:
                self.hass.config_entries.async_update_entry(entry, data=merged)
                await self.hass.config_entries.async_reload(entry.entry_id)
                return self.async_abort(reason="reconfigure_successful")

        schema = self._build_options_schema(entry.data, entry.options)
        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> "AlphaESSModbusOptionsFlow":
        return AlphaESSModbusOptionsFlow()


class AlphaESSModbusOptionsFlow(config_entries.OptionsFlow):

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            merged = {**self.config_entry.data, **user_input}
            if not merged.get(CONF_HOST):
                errors["base"] = "invalid_connection"
            else:
                # Save without connection validation.  The update listener
                # will reload the integration (which properly closes the
                # old hub before creating a new one).
                return self.async_create_entry(title="", data=user_input)

        schema = AlphaESSModbusConfigFlow._build_options_schema(
            self.config_entry.data,
            self.config_entry.options,
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
