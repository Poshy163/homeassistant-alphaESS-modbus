"""Binary sensor platform for the AlphaESS Modbus integration."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity_definitions import BATTERY_FULL_BINARY_SENSOR
from .entity import AlphaESSBaseEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlphaESS binary sensor entities."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.coordinator

    async_add_entities(
        [
            AlphaESSBatteryFullSensor(coordinator, entry),
        ]
    )


class AlphaESSBatteryFullSensor(AlphaESSBaseEntity, BinarySensorEntity):
    """Binary sensor that shows True when the battery is fully charged."""

    def __init__(self, coordinator, entry) -> None:
        super().__init__(coordinator, entry, BATTERY_FULL_BINARY_SENSOR.key)
        self._attr_name = BATTERY_FULL_BINARY_SENSOR.name
        self._attr_device_class = BinarySensorDeviceClass.BATTERY_CHARGING

    @property
    def is_on(self) -> bool | None:
        """Return True if battery status indicates full (status == 1)."""
        status = self.coordinator.data.get("battery_status")
        if status is None:
            return None
        return int(status) == 1
