"""Diagnostics support for AlphaESS Modbus."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant

from .const import DOMAIN

REDACT_KEYS = {CONF_HOST}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.coordinator

    return {
        "config_entry": {
            "data": async_redact_data(dict(entry.data), REDACT_KEYS),
            "options": async_redact_data(dict(entry.options), REDACT_KEYS),
        },
        "coordinator": {
            "model": coordinator._model,
            "poll_freq": coordinator._poll_freq,
            "slow_poll_every": coordinator._slow_poll_every,
            "regular_poll_every": coordinator._regular_poll_every,
            "poll_cycle": coordinator._poll_cycle,
            "consecutive_failures": coordinator._consecutive_failures,
            "data": dict(coordinator.data) if coordinator.data else {},
        },
        "runtime_params": dict(runtime.params),
    }

