"""Number platform for the AlphaESS Modbus integration."""
from __future__ import annotations

import logging

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEFAULT_PARAMS,
    DOMAIN,
)
from .entity_definitions import (
    LOCAL_NUMBER_DEFINITIONS,
    WRITE_NUMBER_DEFINITIONS,
    LocalNumberDefinition,
    WriteNumberDefinition,
)
from .entity import AlphaESSBaseEntity

_LOGGER = logging.getLogger(__name__)


# ───────────────────── Platform setup ────────────────────────────────────


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlphaESS number entities."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.coordinator
    hub = runtime.hub

    entities: list[NumberEntity] = []

    for desc in WRITE_NUMBER_DEFINITIONS:
        entities.append(AlphaESSWriteNumber(coordinator, entry, hub, desc))

    for desc in LOCAL_NUMBER_DEFINITIONS:
        entities.append(AlphaESSLocalNumber(coordinator, entry, runtime, desc))

    async_add_entities(entities)


# ───────────────────── Entity classes ────────────────────────────────────


class AlphaESSWriteNumber(AlphaESSBaseEntity, NumberEntity):
    """Number that reads from a Modbus register and writes back on change."""

    def __init__(self, coordinator, entry, hub, description: WriteNumberDefinition) -> None:
        super().__init__(coordinator, entry, description.key)
        self._hub = hub
        self._desc = description
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = description.unit
        self._attr_native_min_value = description.min_value
        self._attr_native_max_value = description.max_value
        self._attr_native_step = description.step
        self._attr_mode = description.mode
        if description.entity_category is not None:
            self._attr_entity_category = description.entity_category

    @property
    def native_value(self) -> float | None:
        """Return current Modbus register value via coordinator."""
        val = self.coordinator.data.get(self._desc.sensor_key)
        if val is None:
            return None
        return float(val)

    async def async_set_native_value(self, value: float) -> None:
        """Write the new value to the Modbus register."""
        await self._hub.async_write_register(self._desc.register, int(value))
        await self.coordinator.async_request_refresh()


class AlphaESSLocalNumber(AlphaESSBaseEntity, NumberEntity):
    """Number stored locally in runtime params (used by switches)."""

    def __init__(self, coordinator, entry, runtime, description: LocalNumberDefinition) -> None:
        super().__init__(coordinator, entry, description.key)
        self._runtime = runtime
        self._desc = description
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = description.unit
        self._attr_native_min_value = description.min_value
        self._attr_native_max_value = description.max_value
        self._attr_native_step = description.step
        self._attr_mode = description.mode
        if description.entity_category is not None:
            self._attr_entity_category = description.entity_category

        # Ensure default exists
        if description.param_key not in self._runtime.params:
            self._runtime.params[description.param_key] = DEFAULT_PARAMS.get(
                description.param_key, 0
            )

    @property
    def native_value(self) -> float | None:
        """Return current param value."""
        return self._runtime.params.get(self._desc.param_key)

    @property
    def native_max_value(self) -> float:
        """Dynamic max based on AC limit if applicable."""
        if self._desc.use_ac_limit_max:
            ac_limit = self._runtime.params.get("ac_limit_kw")
            if ac_limit is not None:
                return float(ac_limit)
        return self._desc.max_value

    async def async_set_native_value(self, value: float) -> None:
        """Store the value locally."""
        self._runtime.params[self._desc.param_key] = value
        self.async_write_ha_state()
