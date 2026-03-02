"""Time platform for the AlphaESS Modbus integration.

Provides time-picker entities for charging/discharging period start/stop
times. Values are read from the coordinator's Modbus data and written
back to the inverter via two holding registers (hour + minute).
"""
from __future__ import annotations

import logging
from datetime import time
from dataclasses import dataclass

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    REG_CHARGING_PERIOD_1_START_HOUR,
    REG_CHARGING_PERIOD_1_START_MINUTE,
    REG_CHARGING_PERIOD_1_STOP_HOUR,
    REG_CHARGING_PERIOD_1_STOP_MINUTE,
    REG_CHARGING_PERIOD_2_START_HOUR,
    REG_CHARGING_PERIOD_2_START_MINUTE,
    REG_CHARGING_PERIOD_2_STOP_HOUR,
    REG_CHARGING_PERIOD_2_STOP_MINUTE,
    REG_DISCHARGING_PERIOD_1_START_HOUR,
    REG_DISCHARGING_PERIOD_1_START_MINUTE,
    REG_DISCHARGING_PERIOD_1_STOP_HOUR,
    REG_DISCHARGING_PERIOD_1_STOP_MINUTE,
    REG_DISCHARGING_PERIOD_2_START_HOUR,
    REG_DISCHARGING_PERIOD_2_START_MINUTE,
    REG_DISCHARGING_PERIOD_2_STOP_HOUR,
    REG_DISCHARGING_PERIOD_2_STOP_MINUTE,
)
from .entity import AlphaESSBaseEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class PeriodTimeDescription:
    """Describes one period time-picker entity."""

    key: str
    name: str
    hour_key: str          # coordinator data key for the hour value
    minute_key: str        # coordinator data key for the minute value
    hour_register: int     # Modbus register to write the hour
    minute_register: int   # Modbus register to write the minute


PERIOD_TIME_DESCRIPTIONS: tuple[PeriodTimeDescription, ...] = (
    # ── Charging ─────────────────────────────────────────────────────
    PeriodTimeDescription(
        key="helper_charging_period_1_start",
        name="Helper Charging Period 1 Start",
        hour_key="charging_period_1_start_hour",
        minute_key="charging_period_1_start_minute",
        hour_register=REG_CHARGING_PERIOD_1_START_HOUR,
        minute_register=REG_CHARGING_PERIOD_1_START_MINUTE,
    ),
    PeriodTimeDescription(
        key="helper_charging_period_1_stop",
        name="Helper Charging Period 1 Stop",
        hour_key="charging_period_1_stop_hour",
        minute_key="charging_period_1_stop_minute",
        hour_register=REG_CHARGING_PERIOD_1_STOP_HOUR,
        minute_register=REG_CHARGING_PERIOD_1_STOP_MINUTE,
    ),
    PeriodTimeDescription(
        key="helper_charging_period_2_start",
        name="Helper Charging Period 2 Start",
        hour_key="charging_period_2_start_hour",
        minute_key="charging_period_2_start_minute",
        hour_register=REG_CHARGING_PERIOD_2_START_HOUR,
        minute_register=REG_CHARGING_PERIOD_2_START_MINUTE,
    ),
    PeriodTimeDescription(
        key="helper_charging_period_2_stop",
        name="Helper Charging Period 2 Stop",
        hour_key="charging_period_2_stop_hour",
        minute_key="charging_period_2_stop_minute",
        hour_register=REG_CHARGING_PERIOD_2_STOP_HOUR,
        minute_register=REG_CHARGING_PERIOD_2_STOP_MINUTE,
    ),
    # ── Discharging ──────────────────────────────────────────────────
    PeriodTimeDescription(
        key="helper_discharging_period_1_start",
        name="Helper Discharging Period 1 Start",
        hour_key="discharging_period_1_start_hour",
        minute_key="discharging_period_1_start_minute",
        hour_register=REG_DISCHARGING_PERIOD_1_START_HOUR,
        minute_register=REG_DISCHARGING_PERIOD_1_START_MINUTE,
    ),
    PeriodTimeDescription(
        key="helper_discharging_period_1_stop",
        name="Helper Discharging Period 1 Stop",
        hour_key="discharging_period_1_stop_hour",
        minute_key="discharging_period_1_stop_minute",
        hour_register=REG_DISCHARGING_PERIOD_1_STOP_HOUR,
        minute_register=REG_DISCHARGING_PERIOD_1_STOP_MINUTE,
    ),
    PeriodTimeDescription(
        key="helper_discharging_period_2_start",
        name="Helper Discharging Period 2 Start",
        hour_key="discharging_period_2_start_hour",
        minute_key="discharging_period_2_start_minute",
        hour_register=REG_DISCHARGING_PERIOD_2_START_HOUR,
        minute_register=REG_DISCHARGING_PERIOD_2_START_MINUTE,
    ),
    PeriodTimeDescription(
        key="helper_discharging_period_2_stop",
        name="Helper Discharging Period 2 Stop",
        hour_key="discharging_period_2_stop_hour",
        minute_key="discharging_period_2_stop_minute",
        hour_register=REG_DISCHARGING_PERIOD_2_STOP_HOUR,
        minute_register=REG_DISCHARGING_PERIOD_2_STOP_MINUTE,
    ),
)


# ────────── Platform setup ───────────────────────────────────────────────


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlphaESS time entities."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.coordinator
    hub = runtime.hub

    async_add_entities(
        AlphaESSPeriodTimeEntity(coordinator, entry, hub, desc)
        for desc in PERIOD_TIME_DESCRIPTIONS
    )


# ────────── Entity ───────────────────────────────────────────────────────


class AlphaESSPeriodTimeEntity(AlphaESSBaseEntity, TimeEntity):
    """Time-picker entity for a charging/discharging period start or stop."""

    def __init__(self, coordinator, entry, hub, desc: PeriodTimeDescription) -> None:
        super().__init__(coordinator, entry, desc.key)
        self._hub = hub
        self._desc = desc
        self._attr_name = desc.name
        self._attr_icon = "mdi:clock-outline"

    @property
    def native_value(self) -> time | None:
        """Return the current period time from coordinator data."""
        data = self.coordinator.data
        if data is None:
            return None
        hour = data.get(self._desc.hour_key)
        minute = data.get(self._desc.minute_key)
        if hour is None or minute is None:
            return None
        try:
            return time(int(hour), int(minute))
        except (ValueError, TypeError):
            return None

    async def async_set_value(self, value: time) -> None:
        """Write the new time to the inverter via Modbus."""
        ok_h = await self._hub.async_write_register(
            self._desc.hour_register, value.hour
        )
        ok_m = await self._hub.async_write_register(
            self._desc.minute_register, value.minute
        )
        if ok_h and ok_m:
            _LOGGER.debug(
                "Set %s to %02d:%02d",
                self._desc.key, value.hour, value.minute,
            )
            await self.coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to write %s", self._desc.key)
