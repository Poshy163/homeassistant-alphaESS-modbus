from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_MODEL, DOMAIN
from .coordinator import AlphaESSModbusCoordinator


class AlphaESSBaseEntity(CoordinatorEntity[AlphaESSModbusCoordinator]):
    """Base entity for all AlphaESS Modbus entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AlphaESSModbusCoordinator,
        entry: ConfigEntry,
        key: str,
    ) -> None:
        super().__init__(coordinator)
        self._key = key
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            manufacturer="AlphaESS",
            model=self._entry.data.get(CONF_MODEL, "Unknown"),
            name="AlphaESS",
        )
