"""Switch platform for the AlphaESS Modbus integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DISPATCH_RESET_PAYLOAD,
    DOMAIN,
    PARAM_DISPATCH_CUTOFF_SOC,
    PARAM_DISPATCH_DURATION,
    PARAM_DISPATCH_POWER,
    PARAM_FORCE_CHARGE_CUTOFF_SOC,
    PARAM_FORCE_CHARGE_DURATION,
    PARAM_FORCE_CHARGE_POWER,
    PARAM_FORCE_DISCHARGE_CUTOFF_SOC,
    PARAM_FORCE_DISCHARGE_DURATION,
    PARAM_FORCE_DISCHARGE_POWER,
    PARAM_FORCE_EXPORT_CUTOFF_SOC,
    PARAM_FORCE_EXPORT_DURATION,
    PARAM_FORCE_EXPORT_POWER,
    REG_DISPATCH_START,
    pack_dispatch_payload,
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
        AlphaESSForceChargeSwitch(coordinator, entry, hub, runtime),
        AlphaESSForceDischargeSwitch(coordinator, entry, hub, runtime),
        AlphaESSForceExportSwitch(coordinator, entry, hub, runtime),
        AlphaESSDispatchSwitch(coordinator, entry, hub, runtime),
        AlphaESSExcessExportSwitch(coordinator, entry, hub, runtime),
    ]

    # Register mutual-exclusion group
    for sw in switches:
        sw.set_group(switches)

    # Simple toggle switches (not part of mutual-exclusion group)
    extra: list[SwitchEntity] = [
        AlphaESSExcessExportPauseSwitch(coordinator, entry, runtime),
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
                sw.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off — reset dispatch."""
        await self._dispatch_reset()
        self._is_on = False
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


# ──────────────── Force Charging ─────────────────────────────────────────


class AlphaESSForceChargeSwitch(_AlphaESSDispatchSwitch):
    """Force the inverter to charge from grid."""

    def __init__(self, coordinator, entry, hub, runtime) -> None:
        super().__init__(coordinator, entry, hub, runtime, "force_charging_switch", "Helper Force Charging")

    async def async_turn_on(self, **kwargs: Any) -> None:
        params = self._runtime.params
        power_kw = abs(float(params.get(PARAM_FORCE_CHARGE_POWER, 5.0)))
        duration = float(params.get(PARAM_FORCE_CHARGE_DURATION, 120))
        cutoff = float(params.get(PARAM_FORCE_CHARGE_CUTOFF_SOC, 100))

        await self._dispatch_reset()
        await self._turn_off_others()
        vals = pack_dispatch_payload(mode=2, power_kw=-power_kw, duration_min=duration, cutoff_soc=cutoff)
        await self._hub.async_write_registers(REG_DISPATCH_START, vals)
        self._is_on = True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


# ──────────────── Force Discharging ──────────────────────────────────────


class AlphaESSForceDischargeSwitch(_AlphaESSDispatchSwitch):
    """Force the inverter to discharge battery."""

    def __init__(self, coordinator, entry, hub, runtime) -> None:
        super().__init__(coordinator, entry, hub, runtime, "force_discharging_switch", "Helper Force Discharging")

    async def async_turn_on(self, **kwargs: Any) -> None:
        params = self._runtime.params
        power_kw = abs(float(params.get(PARAM_FORCE_DISCHARGE_POWER, 5.0)))
        duration = float(params.get(PARAM_FORCE_DISCHARGE_DURATION, 120))
        cutoff = float(params.get(PARAM_FORCE_DISCHARGE_CUTOFF_SOC, 10))

        await self._dispatch_reset()
        await self._turn_off_others()
        vals = pack_dispatch_payload(mode=2, power_kw=power_kw, duration_min=duration, cutoff_soc=cutoff)
        await self._hub.async_write_registers(REG_DISPATCH_START, vals)
        self._is_on = True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


# ──────────────── Force Export ────────────────────────────────────────────


class AlphaESSForceExportSwitch(_AlphaESSDispatchSwitch):
    """Force the inverter to export power to grid."""

    def __init__(self, coordinator, entry, hub, runtime) -> None:
        super().__init__(coordinator, entry, hub, runtime, "force_export_switch", "Helper Force Export")

    async def async_turn_on(self, **kwargs: Any) -> None:
        params = self._runtime.params
        power_kw = abs(float(params.get(PARAM_FORCE_EXPORT_POWER, 5.0)))
        duration = float(params.get(PARAM_FORCE_EXPORT_DURATION, 120))
        cutoff = float(params.get(PARAM_FORCE_EXPORT_CUTOFF_SOC, 4))

        # Export = positive dispatch power (discharging to grid)
        await self._dispatch_reset()
        await self._turn_off_others()
        vals = pack_dispatch_payload(mode=2, power_kw=power_kw, duration_min=duration, cutoff_soc=cutoff)
        await self._hub.async_write_registers(REG_DISPATCH_START, vals)
        self._is_on = True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


# ──────────────── Dispatch (custom mode) ─────────────────────────────────


class AlphaESSDispatchSwitch(_AlphaESSDispatchSwitch):
    """Dispatch with user-selected mode and parameters."""

    def __init__(self, coordinator, entry, hub, runtime) -> None:
        super().__init__(coordinator, entry, hub, runtime, "dispatch_switch", "Helper Dispatch")

    async def async_turn_on(self, **kwargs: Any) -> None:
        params = self._runtime.params
        mode = int(params.get("dispatch_mode", 2))
        power_kw = float(params.get(PARAM_DISPATCH_POWER, 0))
        duration = float(params.get(PARAM_DISPATCH_DURATION, 120))
        cutoff = float(params.get(PARAM_DISPATCH_CUTOFF_SOC, 100))

        await self._dispatch_reset()
        await self._turn_off_others()
        vals = pack_dispatch_payload(mode=mode, power_kw=power_kw, duration_min=duration, cutoff_soc=cutoff)
        await self._hub.async_write_registers(REG_DISPATCH_START, vals)
        self._is_on = True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


# ──────────────── Excess Export ───────────────────────────────────────────


class AlphaESSExcessExportSwitch(_AlphaESSDispatchSwitch):
    """Dispatch excess PV power (above house load) to the grid."""

    def __init__(self, coordinator, entry, hub, runtime) -> None:
        super().__init__(coordinator, entry, hub, runtime, "excess_export_switch", "Helper Excess Export")

    async def async_turn_on(self, **kwargs: Any) -> None:
        params = self._runtime.params
        cutoff = float(params.get(PARAM_FORCE_EXPORT_CUTOFF_SOC, 4))
        ac_limit_kw = float(params.get("ac_limit_kw", 5.0))

        # Compute excess power from coordinator
        data = self.coordinator.data or {}
        pv_prod = float(data.get("current_pv_production", 0) or 0)
        house_load = float(data.get("current_house_load", 0) or 0)
        excess_w = max(0, pv_prod - house_load)
        excess_kw = min(excess_w / 1000.0, ac_limit_kw)

        await self._dispatch_reset()
        await self._turn_off_others()

        if excess_kw > 0:
            vals = pack_dispatch_payload(
                mode=2, power_kw=excess_kw, duration_min=480, cutoff_soc=cutoff
            )
            await self._hub.async_write_registers(REG_DISPATCH_START, vals)

        self._is_on = True
        self.async_write_ha_state()
        await self.coordinator.async_request_refresh()


# ──────────────── Excess Export Pause ─────────────────────────────────────


class AlphaESSExcessExportPauseSwitch(AlphaESSBaseEntity, SwitchEntity):
    """Simple toggle used by automations to pause excess export."""

    def __init__(self, coordinator, entry, runtime) -> None:
        super().__init__(coordinator, entry, "excess_export_pause_switch")
        self._runtime = runtime
        self._attr_name = "Helper Excess Export Pause"
        self._is_on = False

    @property
    def is_on(self) -> bool:
        return self._is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        self._is_on = False
        self.async_write_ha_state()
