from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DEFAULT_PARAMS, DOMAIN
from .coordinator import AlphaESSModbusCoordinator
from .hub import AlphaESSModbusHub
from .services import async_register_services

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SWITCH,
    Platform.BUTTON,
    Platform.BINARY_SENSOR,
    Platform.TIME,
]


@dataclass
class AlphaESSRuntimeData:
    hub: AlphaESSModbusHub
    coordinator: AlphaESSModbusCoordinator
    unsubscribe_update_listener: Callable[[], None]
    params: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_PARAMS))


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    await async_register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hub = AlphaESSModbusHub(hass, entry)
    coordinator = AlphaESSModbusCoordinator(hass, hub)

    await coordinator.async_config_entry_first_refresh()

    unsubscribe_update_listener = entry.add_update_listener(_async_options_updated)
    hass.data[DOMAIN][entry.entry_id] = AlphaESSRuntimeData(
        hub=hub,
        coordinator=coordinator,
        unsubscribe_update_listener=unsubscribe_update_listener,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    runtime_data: AlphaESSRuntimeData = hass.data[DOMAIN].pop(entry.entry_id)
    runtime_data.unsubscribe_update_listener()
    await runtime_data.hub.async_close()

    return unload_ok


async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
