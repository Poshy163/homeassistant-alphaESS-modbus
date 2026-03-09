"""Sensor platform for the AlphaESS Modbus integration."""
from __future__ import annotations

import logging
import time as time_mod

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COMPUTED_SENSOR_DESCRIPTIONS,
    CORE_SENSOR_DESCRIPTIONS,
    DOMAIN,
    KW_SENSOR_DESCRIPTIONS,
    RegisterType,
    AlphaESSComputedSensorDescription,
    AlphaESSModbusSensorDescription,
)
from .entity import AlphaESSBaseEntity
from .entity_definitions import DISPATCH_TIMER_DEFINITIONS

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

    # Dispatch time-remaining sensors
    for desc in DISPATCH_TIMER_DEFINITIONS:
        entities.append(
            AlphaESSDispatchTimerSensor(coordinator, entry, runtime, desc)
        )

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
        value = self.coordinator.data.get(self._description.key)
        if (
            isinstance(value, float)
            and value.is_integer()
            and self._description.precision in (None, 0)
            and self._description.register_type
            in (
                RegisterType.UINT16,
                RegisterType.INT16,
                RegisterType.UINT32,
                RegisterType.INT32,
            )
        ):
            return int(value)
        return value


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


class AlphaESSDispatchTimerSensor(AlphaESSBaseEntity, SensorEntity):
    """Sensor showing remaining dispatch time in minutes."""

    def __init__(self, coordinator, entry, runtime, description) -> None:
        super().__init__(coordinator, entry, description.key)
        self._runtime = runtime
        self._switch_key = description.switch_key
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = None
        self._attr_suggested_display_precision = 1

    @property
    def native_value(self) -> float:
        """Return remaining dispatch time in minutes, or 0 if idle."""
        started_at = self._runtime.params.get(f"_{self._switch_key}_started_at")
        duration_s = self._runtime.params.get(f"_{self._switch_key}_duration_s")
        if started_at is None or duration_s is None:
            return 0
        remaining = max(0.0, (started_at + duration_s) - time_mod.monotonic())
        return round(remaining / 60, 1)
