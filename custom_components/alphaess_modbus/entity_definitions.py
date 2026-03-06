"""Shared entity definition registry for AlphaESS platforms.

This module centralizes metadata that was previously duplicated across
platform files, so platform setup code can consume one typed source.
"""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberMode
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTime

from .const import (
    AC_LIMIT_OPTIONS,
    DEFAULT_AC_LIMIT_KW,
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
    REG_CHARGING_CUTOFF_SOC,
    REG_CHARGING_PERIOD_1_START_HOUR,
    REG_CHARGING_PERIOD_1_START_MINUTE,
    REG_CHARGING_PERIOD_1_STOP_HOUR,
    REG_CHARGING_PERIOD_1_STOP_MINUTE,
    REG_CHARGING_PERIOD_2_START_HOUR,
    REG_CHARGING_PERIOD_2_START_MINUTE,
    REG_CHARGING_PERIOD_2_STOP_HOUR,
    REG_CHARGING_PERIOD_2_STOP_MINUTE,
    REG_DISCHARGING_CUTOFF_SOC,
    REG_DISCHARGING_PERIOD_1_START_HOUR,
    REG_DISCHARGING_PERIOD_1_START_MINUTE,
    REG_DISCHARGING_PERIOD_1_STOP_HOUR,
    REG_DISCHARGING_PERIOD_1_STOP_MINUTE,
    REG_DISCHARGING_PERIOD_2_START_HOUR,
    REG_DISCHARGING_PERIOD_2_START_MINUTE,
    REG_DISCHARGING_PERIOD_2_STOP_HOUR,
    REG_DISCHARGING_PERIOD_2_STOP_MINUTE,
    REG_MAX_FEED_TO_GRID,
    REG_TIME_PERIOD_CONTROL,
)


@dataclass(frozen=True, kw_only=True)
class WriteNumberDefinition:
    """Number entity that reads from coordinator and writes to a register."""

    key: str
    name: str
    register: int
    sensor_key: str
    min_value: float
    max_value: float
    step: float
    unit: str | None = None
    mode: NumberMode = NumberMode.SLIDER


@dataclass(frozen=True, kw_only=True)
class LocalNumberDefinition:
    """Number entity that stores its value in runtime params."""

    key: str
    name: str
    param_key: str
    min_value: float
    max_value: float
    step: float
    unit: str | None = None
    mode: NumberMode = NumberMode.SLIDER
    use_ac_limit_max: bool = False


@dataclass(frozen=True, kw_only=True)
class RegisterSelectDefinition:
    """Select entity backed by a Modbus register and option map."""

    key: str
    name: str
    register: int
    sensor_key: str
    options: dict[str, int]


@dataclass(frozen=True, kw_only=True)
class RuntimeSelectDefinition:
    """Select entity backed by runtime params."""

    key: str
    name: str
    param_key: str
    options: dict[str, int]
    default_value: int


@dataclass(frozen=True, kw_only=True)
class AcLimitSelectDefinition:
    """Runtime AC limit select definition for scaling helper controls."""

    key: str
    name: str
    param_key: str
    options_kw: tuple[int, ...]
    default_kw: int


@dataclass(frozen=True)
class PeriodTimeDefinition:
    """Definition for a charging/discharging period time picker."""

    key: str
    name: str
    hour_key: str
    minute_key: str
    hour_register: int
    minute_register: int


@dataclass(frozen=True, kw_only=True)
class DispatchSwitchDefinition:
    """Definition for a dispatch-related switch entity."""

    key: str
    name: str
    mode: int
    power_param: str
    duration_param: str
    cutoff_param: str
    power_abs: bool = True
    negate_power: bool = False
    use_dispatch_mode_from_runtime: bool = False
    use_excess_power: bool = False


@dataclass(frozen=True, kw_only=True)
class ToggleSwitchDefinition:
    """Definition for local toggle switch entities."""

    key: str
    name: str


@dataclass(frozen=True, kw_only=True)
class ButtonDefinition:
    """Definition for button entities."""

    key: str
    name: str


@dataclass(frozen=True, kw_only=True)
class BinarySensorDefinition:
    """Definition for binary sensor entities."""

    key: str
    name: str


WRITE_NUMBER_DEFINITIONS: tuple[WriteNumberDefinition, ...] = (
    WriteNumberDefinition(
        key="set_charging_cutoff_soc",
        name="Helper Charging Cutoff SoC",
        register=REG_CHARGING_CUTOFF_SOC,
        sensor_key="charging_cutoff_soc",
        min_value=10,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
    WriteNumberDefinition(
        key="set_discharging_cutoff_soc",
        name="Helper Discharging Cutoff SoC",
        register=REG_DISCHARGING_CUTOFF_SOC,
        sensor_key="discharging_cutoff_soc",
        min_value=4,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
    WriteNumberDefinition(
        key="set_max_feed_to_grid",
        name="Helper Max Feed to Grid",
        register=REG_MAX_FEED_TO_GRID,
        sensor_key="max_feed_to_grid",
        min_value=0,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
)


LOCAL_NUMBER_DEFINITIONS: tuple[LocalNumberDefinition, ...] = (
    LocalNumberDefinition(
        key="force_charging_power",
        name="Template Force Charging Power",
        param_key=PARAM_FORCE_CHARGE_POWER,
        min_value=0,
        max_value=20,
        step=0.1,
        unit=UnitOfPower.KILO_WATT,
        use_ac_limit_max=True,
    ),
    LocalNumberDefinition(
        key="force_charging_duration",
        name="Helper Force Charging Duration",
        param_key=PARAM_FORCE_CHARGE_DURATION,
        min_value=0,
        max_value=480,
        step=5,
        unit=UnitOfTime.MINUTES,
    ),
    LocalNumberDefinition(
        key="force_charging_cutoff_soc",
        name="Helper Force Charging Cutoff SoC",
        param_key=PARAM_FORCE_CHARGE_CUTOFF_SOC,
        min_value=4,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
    LocalNumberDefinition(
        key="force_discharging_power",
        name="Template Force Discharging Power",
        param_key=PARAM_FORCE_DISCHARGE_POWER,
        min_value=0,
        max_value=20,
        step=0.1,
        unit=UnitOfPower.KILO_WATT,
        use_ac_limit_max=True,
    ),
    LocalNumberDefinition(
        key="force_discharging_duration",
        name="Helper Force Discharging Duration",
        param_key=PARAM_FORCE_DISCHARGE_DURATION,
        min_value=0,
        max_value=480,
        step=5,
        unit=UnitOfTime.MINUTES,
    ),
    LocalNumberDefinition(
        key="force_discharging_cutoff_soc",
        name="Helper Force Discharging Cutoff SoC",
        param_key=PARAM_FORCE_DISCHARGE_CUTOFF_SOC,
        min_value=4,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
    LocalNumberDefinition(
        key="force_export_power",
        name="Template Force Export Power",
        param_key=PARAM_FORCE_EXPORT_POWER,
        min_value=0,
        max_value=20,
        step=0.1,
        unit=UnitOfPower.KILO_WATT,
        use_ac_limit_max=True,
    ),
    LocalNumberDefinition(
        key="force_export_duration",
        name="Helper Force Export Duration",
        param_key=PARAM_FORCE_EXPORT_DURATION,
        min_value=0,
        max_value=480,
        step=5,
        unit=UnitOfTime.MINUTES,
    ),
    LocalNumberDefinition(
        key="force_export_cutoff_soc",
        name="Helper Force Export Cutoff SoC",
        param_key=PARAM_FORCE_EXPORT_CUTOFF_SOC,
        min_value=4,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
    LocalNumberDefinition(
        key="dispatch_power",
        name="Template Dispatch Power",
        param_key=PARAM_DISPATCH_POWER,
        min_value=-20,
        max_value=20,
        step=0.1,
        unit=UnitOfPower.KILO_WATT,
    ),
    LocalNumberDefinition(
        key="dispatch_duration",
        name="Helper Dispatch Duration",
        param_key=PARAM_DISPATCH_DURATION,
        min_value=0,
        max_value=480,
        step=5,
        unit=UnitOfTime.MINUTES,
    ),
    LocalNumberDefinition(
        key="dispatch_cutoff_soc",
        name="Helper Dispatch Cutoff SoC",
        param_key=PARAM_DISPATCH_CUTOFF_SOC,
        min_value=4,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
)


TIME_PERIOD_CONTROL_OPTIONS: dict[str, int] = {
    "Disable": 0,
    "Enable Grid Charging Battery": 1,
    "Enable Battery Discharge Time Control": 2,
    "Enable Grid Charging Battery & Battery Discharge Time Control": 3,
}


DISPATCH_MODE_OPTIONS: dict[str, int] = {
    "Battery only Charges from PV": 1,
    "State of Charge Control": 2,
    "Load Following": 3,
    "Maximise Output": 4,
    "Normal Mode": 5,
    "Optimise Consumption": 6,
    "Maximise Consumption": 7,
    "No Battery Charge": 19,
}


TIME_PERIOD_CONTROL_SELECT = RegisterSelectDefinition(
    key="time_period_control_select",
    name="Helper Charging / Discharging Settings",
    register=REG_TIME_PERIOD_CONTROL,
    sensor_key="charging_time_period_control",
    options=TIME_PERIOD_CONTROL_OPTIONS,
)


DISPATCH_MODE_SELECT = RuntimeSelectDefinition(
    key="dispatch_mode_select",
    name="Helper Dispatch Mode",
    param_key="dispatch_mode",
    options=DISPATCH_MODE_OPTIONS,
    default_value=2,
)


AC_LIMIT_SELECT = AcLimitSelectDefinition(
    key="inverter_ac_limit_select",
    name="Helper Inverter AC Limit",
    param_key="ac_limit_kw",
    options_kw=AC_LIMIT_OPTIONS,
    default_kw=DEFAULT_AC_LIMIT_KW,
)


PERIOD_TIME_DEFINITIONS: tuple[PeriodTimeDefinition, ...] = (
    PeriodTimeDefinition(
        key="helper_charging_period_1_start",
        name="Helper Charging Period 1 Start",
        hour_key="charging_period_1_start_hour",
        minute_key="charging_period_1_start_minute",
        hour_register=REG_CHARGING_PERIOD_1_START_HOUR,
        minute_register=REG_CHARGING_PERIOD_1_START_MINUTE,
    ),
    PeriodTimeDefinition(
        key="helper_charging_period_1_stop",
        name="Helper Charging Period 1 Stop",
        hour_key="charging_period_1_stop_hour",
        minute_key="charging_period_1_stop_minute",
        hour_register=REG_CHARGING_PERIOD_1_STOP_HOUR,
        minute_register=REG_CHARGING_PERIOD_1_STOP_MINUTE,
    ),
    PeriodTimeDefinition(
        key="helper_charging_period_2_start",
        name="Helper Charging Period 2 Start",
        hour_key="charging_period_2_start_hour",
        minute_key="charging_period_2_start_minute",
        hour_register=REG_CHARGING_PERIOD_2_START_HOUR,
        minute_register=REG_CHARGING_PERIOD_2_START_MINUTE,
    ),
    PeriodTimeDefinition(
        key="helper_charging_period_2_stop",
        name="Helper Charging Period 2 Stop",
        hour_key="charging_period_2_stop_hour",
        minute_key="charging_period_2_stop_minute",
        hour_register=REG_CHARGING_PERIOD_2_STOP_HOUR,
        minute_register=REG_CHARGING_PERIOD_2_STOP_MINUTE,
    ),
    PeriodTimeDefinition(
        key="helper_discharging_period_1_start",
        name="Helper Discharging Period 1 Start",
        hour_key="discharging_period_1_start_hour",
        minute_key="discharging_period_1_start_minute",
        hour_register=REG_DISCHARGING_PERIOD_1_START_HOUR,
        minute_register=REG_DISCHARGING_PERIOD_1_START_MINUTE,
    ),
    PeriodTimeDefinition(
        key="helper_discharging_period_1_stop",
        name="Helper Discharging Period 1 Stop",
        hour_key="discharging_period_1_stop_hour",
        minute_key="discharging_period_1_stop_minute",
        hour_register=REG_DISCHARGING_PERIOD_1_STOP_HOUR,
        minute_register=REG_DISCHARGING_PERIOD_1_STOP_MINUTE,
    ),
    PeriodTimeDefinition(
        key="helper_discharging_period_2_start",
        name="Helper Discharging Period 2 Start",
        hour_key="discharging_period_2_start_hour",
        minute_key="discharging_period_2_start_minute",
        hour_register=REG_DISCHARGING_PERIOD_2_START_HOUR,
        minute_register=REG_DISCHARGING_PERIOD_2_START_MINUTE,
    ),
    PeriodTimeDefinition(
        key="helper_discharging_period_2_stop",
        name="Helper Discharging Period 2 Stop",
        hour_key="discharging_period_2_stop_hour",
        minute_key="discharging_period_2_stop_minute",
        hour_register=REG_DISCHARGING_PERIOD_2_STOP_HOUR,
        minute_register=REG_DISCHARGING_PERIOD_2_STOP_MINUTE,
    ),
)


DISPATCH_SWITCH_KEYS: tuple[str, ...] = (
    "force_charging_switch",
    "force_discharging_switch",
    "force_export_switch",
    "dispatch_switch",
    "excess_export_switch",
)


DISPATCH_SWITCH_DEFINITIONS: tuple[DispatchSwitchDefinition, ...] = (
    DispatchSwitchDefinition(
        key="force_charging_switch",
        name="Helper Force Charging",
        mode=2,
        power_param=PARAM_FORCE_CHARGE_POWER,
        duration_param=PARAM_FORCE_CHARGE_DURATION,
        cutoff_param=PARAM_FORCE_CHARGE_CUTOFF_SOC,
        power_abs=True,
        negate_power=True,
    ),
    DispatchSwitchDefinition(
        key="force_discharging_switch",
        name="Helper Force Discharging",
        mode=2,
        power_param=PARAM_FORCE_DISCHARGE_POWER,
        duration_param=PARAM_FORCE_DISCHARGE_DURATION,
        cutoff_param=PARAM_FORCE_DISCHARGE_CUTOFF_SOC,
        power_abs=True,
    ),
    DispatchSwitchDefinition(
        key="force_export_switch",
        name="Helper Force Export",
        mode=2,
        power_param=PARAM_FORCE_EXPORT_POWER,
        duration_param=PARAM_FORCE_EXPORT_DURATION,
        cutoff_param=PARAM_FORCE_EXPORT_CUTOFF_SOC,
        power_abs=True,
    ),
    DispatchSwitchDefinition(
        key="dispatch_switch",
        name="Helper Dispatch",
        mode=2,
        power_param=PARAM_DISPATCH_POWER,
        duration_param=PARAM_DISPATCH_DURATION,
        cutoff_param=PARAM_DISPATCH_CUTOFF_SOC,
        use_dispatch_mode_from_runtime=True,
    ),
    DispatchSwitchDefinition(
        key="excess_export_switch",
        name="Helper Excess Export",
        mode=2,
        power_param=PARAM_FORCE_EXPORT_POWER,
        duration_param=PARAM_FORCE_EXPORT_DURATION,
        cutoff_param=PARAM_FORCE_EXPORT_CUTOFF_SOC,
        use_excess_power=True,
        power_abs=True,
    ),
)


EXCESS_EXPORT_PAUSE_SWITCH = ToggleSwitchDefinition(
    key="excess_export_pause_switch",
    name="Helper Excess Export Pause",
)


BUTTON_DEFINITIONS: tuple[ButtonDefinition, ...] = (
    ButtonDefinition(
        key="dispatch_reset_button",
        name="Helper Dispatch Reset",
    ),
    ButtonDefinition(
        key="dispatch_reset_full_button",
        name="Helper Dispatch Reset Full",
    ),
    ButtonDefinition(
        key="sync_datetime_button",
        name="Helper Synchronise Date & Time",
    ),
)


BATTERY_FULL_BINARY_SENSOR = BinarySensorDefinition(
    key="battery_full",
    name="Battery Full",
)
