from __future__ import annotations

from datetime import datetime
from typing import Any

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DISPATCH_RESET_PAYLOAD,
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
    REG_DISPATCH_START,
    REG_SYSTEM_TIME_DDHH,
    REG_SYSTEM_TIME_MMSS,
    REG_SYSTEM_TIME_YYMM,
    SERVICE_DISPATCH,
    SERVICE_DISPATCH_RESET,
    SERVICE_FORCE_CHARGE,
    SERVICE_FORCE_DISCHARGE,
    SERVICE_FORCE_EXPORT,
    SERVICE_SET_CHARGE_PERIODS,
    SERVICE_SET_DISCHARGE_PERIODS,
    SERVICE_SYNC_DATETIME,
    pack_dispatch_payload,
)

CONF_ENTRY_ID = "entry_id"


FORCE_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENTRY_ID): str,
        vol.Optional("power_kw", default=5.0): vol.Coerce(float),
        vol.Optional("duration_min", default=120): vol.Coerce(int),
        vol.Optional("cutoff_soc", default=100): vol.Coerce(int),
    }
)

DISPATCH_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENTRY_ID): str,
        vol.Optional("mode", default=2): vol.Coerce(int),
        vol.Optional("power_kw", default=0.0): vol.Coerce(float),
        vol.Optional("duration_min", default=120): vol.Coerce(int),
        vol.Optional("cutoff_soc", default=100): vol.Coerce(int),
    }
)

PERIOD_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ENTRY_ID): str,
        vol.Required("period_1_start"): cv.string,
        vol.Required("period_1_stop"): cv.string,
        vol.Required("period_2_start"): cv.string,
        vol.Required("period_2_stop"): cv.string,
    }
)


async def async_register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_FORCE_CHARGE):
        return

    hass.services.async_register(DOMAIN, SERVICE_FORCE_CHARGE, _wrap(hass, async_service_force_charge), schema=FORCE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_FORCE_DISCHARGE, _wrap(hass, async_service_force_discharge), schema=FORCE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_FORCE_EXPORT, _wrap(hass, async_service_force_export), schema=FORCE_SCHEMA)
    hass.services.async_register(DOMAIN, SERVICE_DISPATCH, _wrap(hass, async_service_dispatch), schema=DISPATCH_SCHEMA)
    hass.services.async_register(
        DOMAIN,
        SERVICE_DISPATCH_RESET,
        _wrap(hass, async_service_dispatch_reset),
        schema=vol.Schema({vol.Optional(CONF_ENTRY_ID): str}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SYNC_DATETIME,
        _wrap(hass, async_service_sync_datetime),
        schema=vol.Schema({vol.Optional(CONF_ENTRY_ID): str}),
    )
    hass.services.async_register(DOMAIN, SERVICE_SET_CHARGE_PERIODS, _wrap(hass, async_service_set_charge_periods), schema=PERIOD_SCHEMA)
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_DISCHARGE_PERIODS,
        _wrap(hass, async_service_set_discharge_periods),
        schema=PERIOD_SCHEMA,
    )


def _wrap(hass: HomeAssistant, func):
    async def handler(call: ServiceCall) -> None:
        await func(hass, dict(call.data))

    return handler


def _get_runtime(hass: HomeAssistant, data: dict) -> Any | None:
    entries: dict[str, Any] = hass.data.get(DOMAIN, {})
    if not entries:
        return None

    entry_id = data.get(CONF_ENTRY_ID)
    if entry_id:
        return entries.get(entry_id)

    return next(iter(entries.values()))


async def async_service_force_charge(hass: HomeAssistant, data: dict) -> None:
    runtime = _get_runtime(hass, data)
    if runtime is None:
        return

    values = pack_dispatch_payload(
        mode=2,
        power_kw=-abs(float(data.get("power_kw", 5.0))),
        duration_min=int(data.get("duration_min", 120)),
        cutoff_soc=int(data.get("cutoff_soc", 100)),
    )
    await runtime.hub.async_write_registers(REG_DISPATCH_START, values)
    await runtime.coordinator.async_request_refresh()


async def async_service_force_discharge(hass: HomeAssistant, data: dict) -> None:
    runtime = _get_runtime(hass, data)
    if runtime is None:
        return

    values = pack_dispatch_payload(
        mode=2,
        power_kw=abs(float(data.get("power_kw", 5.0))),
        duration_min=int(data.get("duration_min", 120)),
        cutoff_soc=int(data.get("cutoff_soc", 10)),
    )
    await runtime.hub.async_write_registers(REG_DISPATCH_START, values)
    await runtime.coordinator.async_request_refresh()


async def async_service_force_export(hass: HomeAssistant, data: dict) -> None:
    await async_service_force_discharge(hass, data)


async def async_service_dispatch(hass: HomeAssistant, data: dict) -> None:
    runtime = _get_runtime(hass, data)
    if runtime is None:
        return

    values = pack_dispatch_payload(
        mode=int(data.get("mode", 2)),
        power_kw=float(data.get("power_kw", 0.0)),
        duration_min=int(data.get("duration_min", 120)),
        cutoff_soc=int(data.get("cutoff_soc", 100)),
    )
    await runtime.hub.async_write_registers(REG_DISPATCH_START, values)
    await runtime.coordinator.async_request_refresh()


async def async_service_dispatch_reset(hass: HomeAssistant, data: dict) -> None:
    runtime = _get_runtime(hass, data)
    if runtime is None:
        return

    await runtime.hub.async_write_registers(REG_DISPATCH_START, DISPATCH_RESET_PAYLOAD)
    await runtime.coordinator.async_request_refresh()


async def async_service_sync_datetime(hass: HomeAssistant, data: dict) -> None:
    runtime = _get_runtime(hass, data)
    if runtime is None:
        return

    now = datetime.now()
    yymm = int(f"{now.year - 2000:02x}{now.month:02x}", 16)
    ddhh = int(f"{now.day:02x}{now.hour:02x}", 16)
    mmss = int(f"{now.minute:02x}{now.second:02x}", 16)

    await runtime.hub.async_write_register(REG_SYSTEM_TIME_YYMM, yymm)
    await runtime.hub.async_write_register(REG_SYSTEM_TIME_DDHH, ddhh)
    await runtime.hub.async_write_register(REG_SYSTEM_TIME_MMSS, mmss)


async def async_service_set_charge_periods(hass: HomeAssistant, data: dict) -> None:
    runtime = _get_runtime(hass, data)
    if runtime is None:
        return

    p1s_h, p1s_m = _split_time(data["period_1_start"])
    p1e_h, p1e_m = _split_time(data["period_1_stop"])
    p2s_h, p2s_m = _split_time(data["period_2_start"])
    p2e_h, p2e_m = _split_time(data["period_2_stop"])

    await runtime.hub.async_write_register(REG_CHARGING_PERIOD_1_START_HOUR, p1s_h)
    await runtime.hub.async_write_register(REG_CHARGING_PERIOD_1_STOP_HOUR, p1e_h)
    await runtime.hub.async_write_register(REG_CHARGING_PERIOD_2_START_HOUR, p2s_h)
    await runtime.hub.async_write_register(REG_CHARGING_PERIOD_2_STOP_HOUR, p2e_h)
    await runtime.hub.async_write_register(REG_CHARGING_PERIOD_1_START_MINUTE, p1s_m)
    await runtime.hub.async_write_register(REG_CHARGING_PERIOD_1_STOP_MINUTE, p1e_m)
    await runtime.hub.async_write_register(REG_CHARGING_PERIOD_2_START_MINUTE, p2s_m)
    await runtime.hub.async_write_register(REG_CHARGING_PERIOD_2_STOP_MINUTE, p2e_m)


async def async_service_set_discharge_periods(hass: HomeAssistant, data: dict) -> None:
    runtime = _get_runtime(hass, data)
    if runtime is None:
        return

    p1s_h, p1s_m = _split_time(data["period_1_start"])
    p1e_h, p1e_m = _split_time(data["period_1_stop"])
    p2s_h, p2s_m = _split_time(data["period_2_start"])
    p2e_h, p2e_m = _split_time(data["period_2_stop"])

    await runtime.hub.async_write_register(REG_DISCHARGING_PERIOD_1_START_HOUR, p1s_h)
    await runtime.hub.async_write_register(REG_DISCHARGING_PERIOD_1_STOP_HOUR, p1e_h)
    await runtime.hub.async_write_register(REG_DISCHARGING_PERIOD_2_START_HOUR, p2s_h)
    await runtime.hub.async_write_register(REG_DISCHARGING_PERIOD_2_STOP_HOUR, p2e_h)
    await runtime.hub.async_write_register(REG_DISCHARGING_PERIOD_1_START_MINUTE, p1s_m)
    await runtime.hub.async_write_register(REG_DISCHARGING_PERIOD_1_STOP_MINUTE, p1e_m)
    await runtime.hub.async_write_register(REG_DISCHARGING_PERIOD_2_START_MINUTE, p2s_m)
    await runtime.hub.async_write_register(REG_DISCHARGING_PERIOD_2_STOP_MINUTE, p2e_m)


def _split_time(value: str) -> tuple[int, int]:
    hour, minute = value.split(":", maxsplit=1)
    return int(hour), int(minute)
