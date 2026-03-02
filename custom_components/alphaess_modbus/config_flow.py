from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    AC_LIMIT_OPTIONS,
    CONF_AC_LIMIT_KW,
    CONF_MODEL,
    CONF_SLAVE_ID,
    DEFAULT_AC_LIMIT_KW,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DOMAIN,
    INVERTER_MODELS,
)

DEFAULT_NAME = "AlphaESS"


class AlphaESSModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            unique = f"tcp-{user_input.get(CONF_HOST, 'unknown')}"
            await self.async_set_unique_id(unique)
            self._abort_if_unique_id_configured()

            if not user_input.get(CONF_HOST):
                errors["base"] = "invalid_connection"
            elif not user_input.get(CONF_MODEL) or user_input[CONF_MODEL] == "-- Select Inverter --":
                errors["base"] = "invalid_model"
            else:
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
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Required(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
                vol.Required(CONF_MODEL): vol.In(INVERTER_MODELS),
                vol.Required(
                    CONF_AC_LIMIT_KW,
                    default=DEFAULT_AC_LIMIT_KW,
                ): vol.In(AC_LIMIT_OPTIONS),
            }
        )

    @staticmethod
    def _build_options_schema(data: dict, options: dict) -> vol.Schema:
        """Schema for the options flow (pre-filled with current values)."""
        merged = {**data, **options}
        return vol.Schema(
            {
                vol.Required(CONF_HOST, default=merged.get(CONF_HOST, "")): str,
                vol.Optional(CONF_PORT, default=merged.get(CONF_PORT, DEFAULT_PORT)): int,
                vol.Required(CONF_SLAVE_ID, default=merged.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)): int,
                vol.Required(CONF_MODEL, default=merged.get(CONF_MODEL)): vol.In(INVERTER_MODELS),
                vol.Required(
                    CONF_AC_LIMIT_KW,
                    default=merged.get(CONF_AC_LIMIT_KW, DEFAULT_AC_LIMIT_KW),
                ): vol.In(AC_LIMIT_OPTIONS),
            }
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
