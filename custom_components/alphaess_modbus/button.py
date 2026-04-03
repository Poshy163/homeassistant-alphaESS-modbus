"""Button platform for the AlphaESS Modbus integration."""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DISPATCH_RESET_PAYLOAD,
    DOMAIN,
    REG_DISPATCH_START,
    REG_SYSTEM_TIME_DDHH,
    REG_SYSTEM_TIME_MMSS,
    REG_SYSTEM_TIME_YYMM,
)
from .entity_definitions import BUTTON_DEFINITIONS, DISPATCH_SWITCH_KEYS
from .entity import AlphaESSBaseEntity

_LOGGER = logging.getLogger(__name__)

# Named references for clarity (avoids fragile index-based access)
_DISPATCH_RESET = BUTTON_DEFINITIONS[0]
_DISPATCH_RESET_FULL = BUTTON_DEFINITIONS[1]
_SYNC_DATETIME = BUTTON_DEFINITIONS[2]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlphaESS button entities."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.coordinator
    hub = runtime.hub

    async_add_entities(
        [
            AlphaESSDispatchResetButton(coordinator, entry, hub),
            AlphaESSDispatchResetFullButton(coordinator, entry, hub, runtime),
            AlphaESSSyncDateTimeButton(coordinator, entry, hub),
        ]
    )


class AlphaESSDispatchResetButton(AlphaESSBaseEntity, ButtonEntity):
    """Reset all dispatch registers to zero."""

    def __init__(self, coordinator, entry, hub) -> None:
        super().__init__(coordinator, entry, _DISPATCH_RESET.key)
        self._hub = hub
        self._attr_name = _DISPATCH_RESET.name
        if _DISPATCH_RESET.entity_category is not None:
            self._attr_entity_category = _DISPATCH_RESET.entity_category

    async def async_press(self) -> None:
        """Write zeros to dispatch registers."""
        await self._hub.async_write_registers(REG_DISPATCH_START, DISPATCH_RESET_PAYLOAD)
        await self.coordinator.async_request_refresh()


class AlphaESSDispatchResetFullButton(AlphaESSBaseEntity, ButtonEntity):
    """Reset dispatch registers and turn off all dispatch switches."""

    def __init__(self, coordinator, entry, hub, runtime) -> None:
        super().__init__(coordinator, entry, _DISPATCH_RESET_FULL.key)
        self._hub = hub
        self._runtime = runtime
        self._attr_name = _DISPATCH_RESET_FULL.name
        if _DISPATCH_RESET_FULL.entity_category is not None:
            self._attr_entity_category = _DISPATCH_RESET_FULL.entity_category

    async def async_press(self) -> None:
        """Write zeros to dispatch and turn off all dispatch switches."""
        from homeassistant.helpers import entity_registry as er

        await self._hub.async_write_registers(REG_DISPATCH_START, DISPATCH_RESET_PAYLOAD)

        # Look up switch entity IDs via the entity registry (multi-entry safe)
        registry = er.async_get(self.hass)
        for key in DISPATCH_SWITCH_KEYS:
            unique_id = f"{self._entry.entry_id}_{key}"
            entity_id = registry.async_get_entity_id("switch", DOMAIN, unique_id)
            if entity_id and self.hass.states.get(entity_id):
                await self.hass.services.async_call(
                    "switch", "turn_off", {"entity_id": entity_id}
                )

        await self.coordinator.async_request_refresh()


class AlphaESSSyncDateTimeButton(AlphaESSBaseEntity, ButtonEntity):
    """Synchronise inverter date/time with HA system time."""

    def __init__(self, coordinator, entry, hub) -> None:
        super().__init__(coordinator, entry, _SYNC_DATETIME.key)
        self._hub = hub
        self._attr_name = _SYNC_DATETIME.name
        if _SYNC_DATETIME.entity_category is not None:
            self._attr_entity_category = _SYNC_DATETIME.entity_category

    async def async_press(self) -> None:
        """Write current date/time in BCD encoding to the inverter."""
        now = datetime.now()
        yymm = ((now.year % 100) << 8) | now.month
        ddhh = (now.day << 8) | now.hour
        mmss = (now.minute << 8) | now.second

        await self._hub.async_write_register(REG_SYSTEM_TIME_YYMM, yymm)
        await self._hub.async_write_register(REG_SYSTEM_TIME_DDHH, ddhh)
        await self._hub.async_write_register(REG_SYSTEM_TIME_MMSS, mmss)
        await self.coordinator.async_request_refresh()
