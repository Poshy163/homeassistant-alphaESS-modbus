"""Select platform for the AlphaESS Modbus integration."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
)
from .entity_definitions import (
    AC_LIMIT_SELECT,
    DISPATCH_MODE_SELECT,
    TIME_PERIOD_CONTROL_SELECT,
)
from .entity import AlphaESSBaseEntity

_LOGGER = logging.getLogger(__name__)


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

    _REVERSE_MAP: dict[int, str] = {
        v: k for k, v in TIME_PERIOD_CONTROL_SELECT.options.items()
    }

    def __init__(self, coordinator, entry, hub) -> None:
        super().__init__(coordinator, entry, TIME_PERIOD_CONTROL_SELECT.key)
        self._hub = hub
        self._attr_name = TIME_PERIOD_CONTROL_SELECT.name
        self._attr_options = list(TIME_PERIOD_CONTROL_SELECT.options.keys())
        self._attr_entity_category = EntityCategory.CONFIG

    @property
    def current_option(self) -> str | None:
        """Read from coordinator (sensor key charging_time_period_control)."""
        raw = self.coordinator.data.get("charging_time_period_control")
        if raw is None:
            return None
        return self._REVERSE_MAP.get(int(raw))

    async def async_select_option(self, option: str) -> None:
        """Write to register."""
        value = TIME_PERIOD_CONTROL_SELECT.options[option]
        await self._hub.async_write_register(TIME_PERIOD_CONTROL_SELECT.register, value)
        await self.coordinator.async_request_refresh()


class AlphaESSDispatchModeSelect(AlphaESSBaseEntity, SelectEntity):
    """Select for dispatch mode (stored locally, used by dispatch switch)."""

    def __init__(self, coordinator, entry, runtime) -> None:
        super().__init__(coordinator, entry, DISPATCH_MODE_SELECT.key)
        self._runtime = runtime
        self._attr_name = DISPATCH_MODE_SELECT.name
        self._attr_options = list(DISPATCH_MODE_SELECT.options.keys())
        self._attr_entity_category = EntityCategory.CONFIG

        # Initialise to default if not set
        if DISPATCH_MODE_SELECT.param_key not in self._runtime.params:
            self._runtime.params[DISPATCH_MODE_SELECT.param_key] = (
                DISPATCH_MODE_SELECT.default_value
            )

    @property
    def current_option(self) -> str | None:  # noqa: D401
        """Current dispatch mode."""
        val = int(
            self._runtime.params.get(
                DISPATCH_MODE_SELECT.param_key,
                DISPATCH_MODE_SELECT.default_value,
            )
        )
        reverse = {v: k for k, v in DISPATCH_MODE_SELECT.options.items()}
        return reverse.get(val)

    async def async_select_option(self, option: str) -> None:
        """Store dispatch mode locally."""
        self._runtime.params[DISPATCH_MODE_SELECT.param_key] = (
            DISPATCH_MODE_SELECT.options[option]
        )
        self.async_write_ha_state()


class AlphaESSInverterACLimitSelect(AlphaESSBaseEntity, SelectEntity):
    """Select for inverter AC limit (limits force power numbers)."""

    def __init__(self, coordinator, entry, runtime) -> None:
        super().__init__(coordinator, entry, AC_LIMIT_SELECT.key)
        self._runtime = runtime
        self._attr_name = AC_LIMIT_SELECT.name
        self._attr_options = [f"{v} kW" for v in AC_LIMIT_SELECT.options_kw]
        self._attr_entity_category = EntityCategory.CONFIG

        # Initialise default
        if AC_LIMIT_SELECT.param_key not in self._runtime.params:
            self._runtime.params[AC_LIMIT_SELECT.param_key] = float(
                AC_LIMIT_SELECT.default_kw
            )

    @property
    def current_option(self) -> str | None:  # noqa: D401
        """Current AC limit."""
        val = self._runtime.params.get(AC_LIMIT_SELECT.param_key)
        if val is None:
            return None
        # Match the float to an option string
        for opt in AC_LIMIT_SELECT.options_kw:
            if float(opt) == float(val):
                return f"{opt} kW"
        return None

    async def async_select_option(self, option: str) -> None:
        """Store AC limit locally."""
        # Parse "5 kW" → 5.0
        kw_str = option.replace(" kW", "")
        self._runtime.params[AC_LIMIT_SELECT.param_key] = float(kw_str)
        self.async_write_ha_state()
