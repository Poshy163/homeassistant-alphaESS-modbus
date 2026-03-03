"""Sensor platform for the AlphaESS Modbus integration."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COMPUTED_SENSOR_DESCRIPTIONS,
    CORE_SENSOR_DESCRIPTIONS,
    DOMAIN,
    KW_SENSOR_DESCRIPTIONS,
    AlphaESSComputedSensorDescription,
    AlphaESSModbusSensorDescription,
)
from .entity import AlphaESSBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlphaESS Modbus sensors from a config entry."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.coordinator

    entities: list[SensorEntity] = []

    # Modbus register sensors
    for desc in CORE_SENSOR_DESCRIPTIONS:
        entities.append(AlphaESSModbusSensor(coordinator, entry, desc))

    # Computed / template sensors
    for desc in COMPUTED_SENSOR_DESCRIPTIONS:
        entities.append(AlphaESSComputedSensor(coordinator, entry, desc))

    # kW power sensors for dashboard charts
    for desc in KW_SENSOR_DESCRIPTIONS:
        entities.append(AlphaESSComputedSensor(coordinator, entry, desc))

    async_add_entities(entities)


class AlphaESSModbusSensor(AlphaESSBaseEntity, SensorEntity):
    """Sensor backed by a Modbus register."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: AlphaESSModbusSensorDescription,
    ) -> None:
        super().__init__(coordinator, entry, description.key)
        self._description = description
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_entity_registry_enabled_default = description.enabled_by_default
        if description.is_diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        if description.precision is not None:
            self._attr_suggested_display_precision = description.precision

    @property
    def native_value(self) -> float | str | None:
        """Return the sensor value from coordinator data."""
        return self.coordinator.data.get(self._description.key)


class AlphaESSComputedSensor(AlphaESSBaseEntity, SensorEntity):
    """Sensor whose value is computed from other sensor values."""

    def __init__(
        self,
        coordinator,
        entry: ConfigEntry,
        description: AlphaESSComputedSensorDescription,
    ) -> None:
        super().__init__(coordinator, entry, description.key)
        self._description = description
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = description.unit
        self._attr_device_class = description.device_class
        self._attr_state_class = description.state_class
        self._attr_entity_registry_enabled_default = description.enabled_by_default
        if description.is_diagnostic:
            self._attr_entity_category = EntityCategory.DIAGNOSTIC
        if description.precision is not None:
            self._attr_suggested_display_precision = description.precision

    @property
    def native_value(self) -> float | str | None:
        """Return the computed value from coordinator data."""
        return self.coordinator.data.get(self._description.key)
