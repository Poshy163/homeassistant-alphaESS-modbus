from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DEFAULT_PARAMS, DOMAIN
from .coordinator import AlphaESSModbusCoordinator
from .hub import AlphaESSModbusHub
from .services import async_register_services

_LOGGER = logging.getLogger(__name__)

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

URL_BASE = "/alphaess_modbus"
LEGACY_URL_BASE = "/custom_components/alphaess_modbus/www"
CARD_JS = "alphaess-card.js"
CARD_ENTITIES_JS = "alphaess-entities-cards.js"
DATA_CARD_REGISTERED = f"{DOMAIN}_card_registered"
DATA_CARD_REGISTER_LOCK = f"{DOMAIN}_card_register_lock"
DATA_CARD_JS_URLS = f"{DOMAIN}_card_js_urls"


@dataclass
class AlphaESSRuntimeData:
    hub: AlphaESSModbusHub
    coordinator: AlphaESSModbusCoordinator
    unsubscribe_update_listener: Callable[[], None]
    params: dict[str, float] = field(default_factory=lambda: dict(DEFAULT_PARAMS))


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})

    # Register services — wrapped so a failure here won't block card loading.
    try:
        await async_register_services(hass)
    except Exception:
        _LOGGER.exception("Failed to register AlphaESS services")

    await _async_register_custom_cards(hass)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    await _async_register_custom_cards(hass)

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


async def _async_register_custom_cards(hass: HomeAssistant) -> None:
    # Serve the custom card JS and auto-register it as a Lovelace resource.
    # We intentionally disable cache headers and use stable URLs so users do
    # not need to manually manage resource version query strings.
    lock = hass.data.setdefault(DATA_CARD_REGISTER_LOCK, asyncio.Lock())
    async with lock:
        registered_js_urls: set[str] = hass.data.setdefault(DATA_CARD_JS_URLS, set())

        www_dir = Path(__file__).parent / "www"
        card_path = www_dir / CARD_JS
        entities_path = www_dir / CARD_ENTITIES_JS

        if not card_path.is_file():
            _LOGGER.error(
                "Card JS not found at %s – custom cards will not load",
                card_path,
            )
            return

        if not entities_path.is_file():
            _LOGGER.error(
                "Entities card JS not found at %s – custom cards will not load",
                entities_path,
            )
            return

        resources = [
            (f"{URL_BASE}/{CARD_JS}", str(card_path)),
            (f"{URL_BASE}/{CARD_ENTITIES_JS}", str(entities_path)),
            (f"{LEGACY_URL_BASE}/{CARD_JS}", str(card_path)),
            (f"{LEGACY_URL_BASE}/{CARD_ENTITIES_JS}", str(entities_path)),
        ]

        for url_path, file_path in resources:
            try:
                await hass.http.async_register_static_paths(
                    [
                        StaticPathConfig(
                            url_path,
                            file_path,
                            cache_headers=False,
                        )
                    ]
                )
            except ValueError:
                _LOGGER.debug(
                    "Static path %s already registered; continuing",
                    url_path,
                )
            except Exception:
                _LOGGER.exception(
                    "Failed to register static path %s",
                    url_path,
                )
                return

        js_urls = [
            f"{URL_BASE}/{CARD_JS}",
            f"{URL_BASE}/{CARD_ENTITIES_JS}",
        ]

        for js_url in js_urls:
            if js_url in registered_js_urls:
                continue
            try:
                if add_extra_js_url is not None:
                    add_extra_js_url(hass, js_url)
                registered_js_urls.add(js_url)
            except Exception:
                _LOGGER.exception("Failed to add AlphaESS card JS URL: %s", js_url)
                return

        hass.data[DATA_CARD_REGISTERED] = True
        _LOGGER.debug(
            "Registered AlphaESS custom cards from %s", www_dir
        )
