"""Switch platform for the AlphaESS Modbus integration."""
from __future__ import annotations

import logging
import time as time_mod
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DISPATCH_RESET_PAYLOAD,
    DOMAIN,
    REG_DISPATCH_START,
    pack_dispatch_payload,
)
from .entity_definitions import (
    DISPATCH_SWITCH_DEFINITIONS,
    DispatchSwitchDefinition,
    EXCESS_EXPORT_PAUSE_SWITCH,
)
from .entity import AlphaESSBaseEntity

_LOGGER = logging.getLogger(__name__)


# ──────────────── Platform setup ─────────────────────────────────────────


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlphaESS switch entities."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.coordinator
    hub = runtime.hub

    switches: list[_AlphaESSDispatchSwitch] = [
        AlphaESSDispatchProfileSwitch(coordinator, entry, hub, runtime, desc)
        for desc in DISPATCH_SWITCH_DEFINITIONS
    ]

    # Register mutual-exclusion group
    for sw in switches:
        sw.set_group(switches)

    # Simple toggle switches (not part of mutual-exclusion group)
    extra: list[SwitchEntity] = [
        AlphaESSToggleSwitch(coordinator, entry, runtime, EXCESS_EXPORT_PAUSE_SWITCH),
    ]

    async_add_entities([*switches, *extra])


# ──────────────── Base class ─────────────────────────────────────────────


class _AlphaESSDispatchSwitch(AlphaESSBaseEntity, SwitchEntity):
    """Base for mutually-exclusive dispatch switches."""

    def __init__(self, coordinator, entry, hub, runtime, key: str, name: str) -> None:
        super().__init__(coordinator, entry, key)
        self._hub = hub
        self._runtime = runtime
        self._attr_name = name
        self._is_on = False
        self._group: list[_AlphaESSDispatchSwitch] = []

    def set_group(self, group: list[_AlphaESSDispatchSwitch]) -> None:
        """Set mutual exclusion group."""
        self._group = group

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def _dispatch_reset(self) -> None:
        """Write zeros to all dispatch registers."""
        await self._hub.async_write_registers(REG_DISPATCH_START, DISPATCH_RESET_PAYLOAD)

    async def _turn_off_others(self) -> None:
        """Turn off all other switches in the group without dispatching reset again."""
        for sw in self._group:
            if sw is not self and sw._is_on:
                sw._is_on = False
                self._runtime.params.pop(f"_{sw._key}_started_at", None)
                self._runtime.params.pop(f"_{sw._key}_duration_s", None)
                sw.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off — reset dispatch."""
        await self._dispatch_reset()
        self._is_on = False
        self._runtime.params.pop(f"_{self._key}_started_at", None)
        self._runtime.params.pop(f"_{self._key}_duration_s", None)
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class AlphaESSDispatchProfileSwitch(_AlphaESSDispatchSwitch):
    """Dispatch switch driven by a shared profile definition."""

    def __init__(
        self,
        coordinator,
        entry,
        hub,
        runtime,
        description: DispatchSwitchDefinition,
    ) -> None:
        super().__init__(coordinator, entry, hub, runtime, description.key, description.name)
        self._desc = description
        if description.entity_category is not None:
            self._attr_entity_category = description.entity_category

    async def async_turn_on(self, **kwargs: Any) -> None:
        params = self._runtime.params
        cutoff = float(params.get(self._desc.cutoff_param, 100))

        if self._desc.use_excess_power:
            ac_limit_kw = float(params.get("ac_limit_kw", 5.0))
            data = self.coordinator.data or {}
            pv_prod = float(data.get("current_pv_production", 0) or 0)
            house_load = float(data.get("current_house_load", 0) or 0)
            excess_w = max(0, pv_prod - house_load)
            power_kw = min(excess_w / 1000.0, ac_limit_kw)
            duration = 480.0
        else:
            power_kw = float(params.get(self._desc.power_param, 0))
            duration = float(params.get(self._desc.duration_param, 120))

        if self._desc.power_abs:
            power_kw = abs(power_kw)
        if self._desc.negate_power:
            power_kw = -power_kw

        mode = self._desc.mode
        if self._desc.use_dispatch_mode_from_runtime:
            mode = int(params.get("dispatch_mode", self._desc.mode))

        await self._dispatch_reset()
        await self._turn_off_others()

        dispatched = False
        if (not self._desc.use_excess_power) or power_kw > 0:
            vals = pack_dispatch_payload(
                mode=mode,
                power_kw=power_kw,
                duration_min=duration,
                cutoff_soc=cutoff,
            )
            await self._hub.async_write_registers(REG_DISPATCH_START, vals)
            dispatched = True

        self._is_on = True
        if dispatched:
            params[f"_{self._desc.key}_started_at"] = time_mod.monotonic()
            params[f"_{self._desc.key}_duration_s"] = duration * 60
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


class AlphaESSToggleSwitch(AlphaESSBaseEntity, SwitchEntity):
    """Simple local toggle switch entity."""

    def __init__(self, coordinator, entry, runtime, description) -> None:
        super().__init__(coordinator, entry, description.key)
        self._runtime = runtime
        self._attr_name = description.name
        self._is_on = False
        if hasattr(description, "entity_category") and description.entity_category is not None:
            self._attr_entity_category = description.entity_category

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._is_on = False
        self.async_write_ha_state()
