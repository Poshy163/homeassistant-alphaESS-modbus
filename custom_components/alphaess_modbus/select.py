"""Select platform for the AlphaESS Modbus integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    AC_LIMIT_OPTIONS,
    DEFAULT_AC_LIMIT_KW,
    DOMAIN,
    REG_TIME_PERIOD_CONTROL,
)
from .entity import AlphaESSBaseEntity

_LOGGER = logging.getLogger(__name__)


# ────────── Option maps ──────────────────────────────────────────────────

TIME_PERIOD_CONTROL_OPTIONS: dict[str, int] = {
    "Disable": 0,
    "Enable Grid Charging Battery": 1,
    "Enable Battery Discharge Time Control": 2,
    "Enable Grid Charging Battery & Battery Discharge Time Control": 3,
}

DISPATCH_MODE_OPTIONS: dict[str, int] = {
    "Battery only Charges from PV": 1,
    "State of Charge Control": 2,
    "Load Following": 3,
    "Maximise Output": 4,
    "Normal Mode": 5,
    "Optimise Consumption": 6,
    "Maximise Consumption": 7,
    "No Battery Charge": 19,
}


# ────────── Platform setup ───────────────────────────────────────────────


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlphaESS select entities."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.coordinator
    hub = runtime.hub

    entities: list[SelectEntity] = [
        AlphaESSTimePeriodControlSelect(coordinator, entry, hub),
        AlphaESSDispatchModeSelect(coordinator, entry, runtime),
        AlphaESSInverterACLimitSelect(coordinator, entry, runtime),
    ]
    async_add_entities(entities)


# ────────── Entity classes ───────────────────────────────────────────────


class AlphaESSTimePeriodControlSelect(AlphaESSBaseEntity, SelectEntity):
    """Select that writes to the charging time period control register."""

    _REVERSE_MAP: dict[int, str] = {v: k for k, v in TIME_PERIOD_CONTROL_OPTIONS.items()}

    def __init__(self, coordinator, entry, hub) -> None:
        super().__init__(coordinator, entry, "time_period_control_select")
        self._hub = hub
        self._attr_name = "Helper Charging / Discharging Settings"
        self._attr_options = list(TIME_PERIOD_CONTROL_OPTIONS.keys())

    @property
    def current_option(self) -> str | None:
        """Read from coordinator (sensor key charging_time_period_control)."""
        raw = self.coordinator.data.get("charging_time_period_control")
        if raw is None:
            return None
        return self._REVERSE_MAP.get(int(raw))

    async def async_select_option(self, option: str) -> None:
        """Write to register."""
        value = TIME_PERIOD_CONTROL_OPTIONS[option]
        await self._hub.async_write_register(REG_TIME_PERIOD_CONTROL, value)
        await self.coordinator.async_request_refresh()


class AlphaESSDispatchModeSelect(AlphaESSBaseEntity, SelectEntity):
    """Select for dispatch mode (stored locally, used by dispatch switch)."""

    def __init__(self, coordinator, entry, runtime) -> None:
        super().__init__(coordinator, entry, "dispatch_mode_select")
        self._runtime = runtime
        self._attr_name = "Helper Dispatch Mode"
        self._attr_options = list(DISPATCH_MODE_OPTIONS.keys())

        # Initialise to default if not set
        if "dispatch_mode" not in self._runtime.params:
            self._runtime.params["dispatch_mode"] = 2  # SoC Control default

    @property
    def current_option(self) -> str | None:  # noqa: D401
        """Current dispatch mode."""
        val = int(self._runtime.params.get("dispatch_mode", 2))
        reverse = {v: k for k, v in DISPATCH_MODE_OPTIONS.items()}
        return reverse.get(val)

    async def async_select_option(self, option: str) -> None:
        """Store dispatch mode locally."""
        self._runtime.params["dispatch_mode"] = DISPATCH_MODE_OPTIONS[option]
        self.async_write_ha_state()


class AlphaESSInverterACLimitSelect(AlphaESSBaseEntity, SelectEntity):
    """Select for inverter AC limit (limits force power numbers)."""

    def __init__(self, coordinator, entry, runtime) -> None:
        super().__init__(coordinator, entry, "inverter_ac_limit_select")
        self._runtime = runtime
        self._attr_name = "Helper Inverter AC Limit"
        self._attr_options = [f"{v} kW" for v in AC_LIMIT_OPTIONS]

        # Initialise default
        if "ac_limit_kw" not in self._runtime.params:
            self._runtime.params["ac_limit_kw"] = float(DEFAULT_AC_LIMIT_KW)

    @property
    def current_option(self) -> str | None:  # noqa: D401
        """Current AC limit."""
        val = self._runtime.params.get("ac_limit_kw")
        if val is None:
            return None
        # Match the float to an option string
        for opt in AC_LIMIT_OPTIONS:
            if float(opt) == float(val):
                return f"{opt} kW"
        return None

    async def async_select_option(self, option: str) -> None:
        """Store AC limit locally."""
        # Parse "5 kW" → 5.0
        kw_str = option.replace(" kW", "")
        self._runtime.params["ac_limit_kw"] = float(kw_str)
        self.async_write_ha_state()
