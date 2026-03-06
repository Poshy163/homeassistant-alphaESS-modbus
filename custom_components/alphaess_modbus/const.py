"""Constants for the AlphaESS Modbus integration."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import UnitOfPower

from .sensor_registry import (
    COMPUTED_SENSOR_DEFINITIONS,
    CORE_SENSOR_DEFINITIONS,
    INTERNAL_REGISTER_DEFINITIONS,
)

# ───────────────────────── Domain & integration ──────────────────────────

DOMAIN = "alphaess_modbus"

CONF_MODEL = "model"
CONF_AC_LIMIT_KW = "ac_limit_kw"
CONF_SLAVE_ID = "slave_id"

DEFAULT_PORT = 502
DEFAULT_SLAVE_ID = 85
DEFAULT_AC_LIMIT_KW = "5"
DEFAULT_SCAN_INTERVAL_SECONDS = 5

PLATFORMS = ["sensor", "number", "select", "switch", "button", "time"]

# ─────────────────────── Service names ───────────────────────────────────

SERVICE_FORCE_CHARGE = "force_charge"
SERVICE_FORCE_DISCHARGE = "force_discharge"
SERVICE_FORCE_EXPORT = "force_export"
SERVICE_DISPATCH = "dispatch"
SERVICE_DISPATCH_RESET = "dispatch_reset"
SERVICE_SYNC_DATETIME = "sync_datetime"
SERVICE_SET_CHARGE_PERIODS = "set_charging_periods"
SERVICE_SET_DISCHARGE_PERIODS = "set_discharging_periods"

# ─────────────────────── Inverter model list ─────────────────────────────

INVERTER_MODELS = [
    "-- Select Inverter --",
    "SMILE5",
    "SMILE-G3-S3.6",
    "SMILE-G3-B5",
    "SMILE-G3-S5",
    "SMILE-G3-T10",
    "SMILE-Hi5",
    "SMILE-Hi10",
    "SMILE-B3",
    "SMILE-B3-PLUS",
    "SMILE-S6-HV",
    "Other",
]

AC_LIMIT_OPTIONS = ["3", "4", "4.6", "5", "6", "8", "10", "12", "15", "20"]

# ─────────────────────── Register addresses ──────────────────────────────

# Grid Meter
REG_CT_RATE_GRID_METER = 0x0001
REG_TOTAL_ENERGY_FEED_TO_GRID_METER = 0x0010
REG_TOTAL_ENERGY_CONSUMPTION_FROM_GRID_METER = 0x0012
REG_VOLTAGE_PHASE_A_GRID = 0x0014
REG_VOLTAGE_PHASE_B_GRID = 0x0015
REG_VOLTAGE_PHASE_C_GRID = 0x0016
REG_POWER_PHASE_A_GRID = 0x001B
REG_POWER_PHASE_B_GRID = 0x001D
REG_POWER_PHASE_C_GRID = 0x001F
REG_POWER_GRID = 0x0021

# PV Meter
REG_CT_RATE_PV_METER = 0x0081
REG_TOTAL_ENERGY_FEED_TO_GRID_PV = 0x0090
REG_ACTIVE_POWER_PV_METER = 0x00A1

# Battery
REG_BATTERY_VOLTAGE = 0x0100
REG_BATTERY_CURRENT = 0x0101
REG_SOC_BATTERY = 0x0102
REG_BATTERY_STATUS = 0x0103
REG_BATTERY_MIN_CELL_TEMP = 0x010D
REG_BATTERY_MAX_CELL_TEMP = 0x0110
REG_BATTERY_MAX_CHARGE_CURRENT = 0x0111
REG_BATTERY_MAX_DISCHARGE_CURRENT = 0x0112
REG_BMS_VERSION = 0x0115
REG_LMU_VERSION = 0x0116
REG_ISO_VERSION = 0x0117
REG_SOH_BATTERY = 0x011B
REG_BATTERY_WARNING = 0x011C
REG_BATTERY_FAULT = 0x011E
REG_TOTAL_ENERGY_CHARGE_BATTERY = 0x0120
REG_TOTAL_ENERGY_DISCHARGE_BATTERY = 0x0122
REG_TOTAL_ENERGY_CHARGE_BATTERY_FROM_GRID = 0x0124
REG_POWER_BATTERY = 0x0126
REG_BATTERY_REMAINING_TIME = 0x0127
REG_BATTERY_1_FAULT = 0x0131
REG_BATTERY_2_FAULT = 0x0133
REG_BATTERY_3_FAULT = 0x0135
REG_BATTERY_4_FAULT = 0x0137
REG_BATTERY_5_FAULT = 0x0139
REG_BATTERY_6_FAULT = 0x013B
REG_BATTERY_1_WARNING = 0x013D
REG_BATTERY_2_WARNING = 0x013F
REG_BATTERY_3_WARNING = 0x0141
REG_BATTERY_4_WARNING = 0x0143
REG_BATTERY_5_WARNING = 0x0145
REG_BATTERY_6_WARNING = 0x0147

# Inverter
REG_POWER_INVERTER_L1 = 0x0406
REG_POWER_INVERTER_L2 = 0x0408
REG_POWER_INVERTER_L3 = 0x040A
REG_POWER_INVERTER = 0x040C
REG_BACKUP_POWER_INVERTER_L1 = 0x0414
REG_BACKUP_POWER_INVERTER_L2 = 0x0416
REG_BACKUP_POWER_INVERTER_L3 = 0x0418
REG_BACKUP_POWER_INVERTER = 0x041A
REG_INVERTER_GRID_FREQUENCY = 0x041C
REG_PV1_VOLTAGE = 0x041D
REG_PV1_CURRENT = 0x041E
REG_PV1_POWER = 0x041F
REG_PV2_VOLTAGE = 0x0421
REG_PV2_CURRENT = 0x0422
REG_PV2_POWER = 0x0423
REG_PV3_VOLTAGE = 0x0425
REG_PV3_CURRENT = 0x0426
REG_PV3_POWER = 0x0427
REG_PV4_VOLTAGE = 0x0429
REG_PV4_CURRENT = 0x042A
REG_PV4_POWER = 0x042B
REG_INVERTER_TEMPERATURE = 0x0435
REG_INVERTER_WARNING_1 = 0x0436
REG_INVERTER_WARNING_2 = 0x0438
REG_INVERTER_FAULT_1 = 0x043A
REG_INVERTER_FAULT_2 = 0x043C
REG_TOTAL_ENERGY_FROM_PV = 0x043E
REG_INVERTER_WORK_MODE = 0x0440

# EMS Version
REG_EMS_VERSION_HIGH = 0x074B
REG_EMS_VERSION_MIDDLE = 0x074C
REG_EMS_VERSION_LOW = 0x074D

# System Time
REG_SYSTEM_TIME_YYMM = 0x0740
REG_SYSTEM_TIME_DDHH = 0x0741
REG_SYSTEM_TIME_MMSS = 0x0742

# PV Settings
REG_MAX_FEED_TO_GRID = 0x0800
REG_PV_CAPACITY_STORAGE = 0x0801
REG_PV_CAPACITY_GRID_INVERTER = 0x0803

# Network
REG_IP_METHOD = 0x0808
REG_LOCAL_IP = 0x0809
REG_SUBNET_MASK = 0x080B
REG_GATEWAY = 0x080D
REG_MODBUS_BAUD_RATE = 0x0810

# Charging / Discharging
REG_TIME_PERIOD_CONTROL = 0x084F
REG_DISCHARGING_CUTOFF_SOC = 0x0850
REG_DISCHARGING_PERIOD_1_START_HOUR = 0x0851
REG_DISCHARGING_PERIOD_1_STOP_HOUR = 0x0852
REG_DISCHARGING_PERIOD_2_START_HOUR = 0x0853
REG_DISCHARGING_PERIOD_2_STOP_HOUR = 0x0854
REG_CHARGING_CUTOFF_SOC = 0x0855
REG_CHARGING_PERIOD_1_START_HOUR = 0x0856
REG_CHARGING_PERIOD_1_STOP_HOUR = 0x0857
REG_CHARGING_PERIOD_2_START_HOUR = 0x0858
REG_CHARGING_PERIOD_2_STOP_HOUR = 0x0859
REG_DISCHARGING_PERIOD_1_START_MINUTE = 0x085A
REG_DISCHARGING_PERIOD_1_STOP_MINUTE = 0x085B
REG_DISCHARGING_PERIOD_2_START_MINUTE = 0x085C
REG_DISCHARGING_PERIOD_2_STOP_MINUTE = 0x085D
REG_CHARGING_PERIOD_1_START_MINUTE = 0x085E
REG_CHARGING_PERIOD_1_STOP_MINUTE = 0x085F
REG_CHARGING_PERIOD_2_START_MINUTE = 0x0860
REG_CHARGING_PERIOD_2_STOP_MINUTE = 0x0861

# Dispatch
REG_DISPATCH_START = 0x0880
REG_DISPATCH_ACTIVE_POWER = 0x0881
REG_DISPATCH_REACTIVE_POWER = 0x0883
REG_DISPATCH_MODE = 0x0885
REG_DISPATCH_SOC = 0x0886
REG_DISPATCH_TIME = 0x0887

# System Fault
REG_SYSTEM_FAULT = 0x08D4

# Inverter Version (string registers, 5 registers = 10 ASCII chars)
REG_INVERTER_VERSION = 0x0640
REG_INVERTER_ARM_VERSION = 0x0645

# Grid Safety
REG_GRID_REGULATION = 0x1000
REG_OVP_L1 = 0x100B
REG_OVP_L1_TIME = 0x100C
REG_OVP10 = 0x100D
REG_OVP10_TIME = 0x100E
REG_UVP_L1 = 0x100F
REG_UVP_L1_TIME = 0x1010
REG_UVP_L2 = 0x1011
REG_UVP_L2_TIME = 0x1012
REG_OFP_L1 = 0x1013
REG_OFP_L1_TIME = 0x1014
REG_OFP_L2 = 0x1015
REG_OFP_L2_TIME = 0x1016
REG_UFP_L1 = 0x1017
REG_UFP_L1_TIME = 0x1018
REG_UFP_L2 = 0x1019
REG_UFP_L2_TIME = 0x101A
REG_OVP_L2 = 0x101B
REG_OVP_L2_TIME = 0x101C
REG_OVP_L3 = 0x101D
REG_OVP_L3_TIME = 0x101E
REG_UVP_L3 = 0x101F
REG_UVP_L3_TIME = 0x1020
REG_OFP_L3 = 0x1021
REG_OFP_L3_TIME = 0x1022
REG_UFP_L3 = 0x1023
REG_UFP_L3_TIME = 0x1024

# ─────────────────────── Dispatch constants ──────────────────────────────

DISPATCH_POWER_OFFSET = 32000
DISPATCH_SOC_SCALE = 0.392


def pack_dispatch_payload(
    mode: int,
    power_kw: float,
    duration_min: float,
    cutoff_soc: float,
) -> list[int]:
    """Build the 9-register payload for writing to REG_DISPATCH_START.

    Used by both switch entities and services to ensure identical encoding.
    """
    active_power = int(round(power_kw * 1000)) + DISPATCH_POWER_OFFSET
    reactive_power = DISPATCH_POWER_OFFSET  # zero reactive
    soc = int(round(cutoff_soc / DISPATCH_SOC_SCALE))
    time_s = int(duration_min * 60)
    return [
        1,  # dispatch start = ON
        (active_power >> 16) & 0xFFFF,
        active_power & 0xFFFF,
        (reactive_power >> 16) & 0xFFFF,
        reactive_power & 0xFFFF,
        mode,
        soc,
        (time_s >> 16) & 0xFFFF,
        time_s & 0xFFFF,
    ]


DISPATCH_RESET_PAYLOAD = [0] * 9

# ─────────────────────── Local parameter keys ────────────────────────────

PARAM_FORCE_CHARGE_POWER = "force_charge_power_kw"
PARAM_FORCE_CHARGE_DURATION = "force_charge_duration_min"
PARAM_FORCE_CHARGE_CUTOFF_SOC = "force_charge_cutoff_soc"
PARAM_FORCE_DISCHARGE_POWER = "force_discharge_power_kw"
PARAM_FORCE_DISCHARGE_DURATION = "force_discharge_duration_min"
PARAM_FORCE_DISCHARGE_CUTOFF_SOC = "force_discharge_cutoff_soc"
PARAM_FORCE_EXPORT_POWER = "force_export_power_kw"
PARAM_FORCE_EXPORT_DURATION = "force_export_duration_min"
PARAM_FORCE_EXPORT_CUTOFF_SOC = "force_export_cutoff_soc"
PARAM_DISPATCH_POWER = "dispatch_power_kw"
PARAM_DISPATCH_DURATION = "dispatch_duration_min"
PARAM_DISPATCH_CUTOFF_SOC = "dispatch_cutoff_soc"

DEFAULT_PARAMS: dict[str, float] = {
    PARAM_FORCE_CHARGE_POWER: 5.0,
    PARAM_FORCE_CHARGE_DURATION: 120,
    PARAM_FORCE_CHARGE_CUTOFF_SOC: 100,
    PARAM_FORCE_DISCHARGE_POWER: 5.0,
    PARAM_FORCE_DISCHARGE_DURATION: 120,
    PARAM_FORCE_DISCHARGE_CUTOFF_SOC: 10,
    PARAM_FORCE_EXPORT_POWER: 5.0,
    PARAM_FORCE_EXPORT_DURATION: 120,
    PARAM_FORCE_EXPORT_CUTOFF_SOC: 4,
    PARAM_DISPATCH_POWER: 0.0,
    PARAM_DISPATCH_DURATION: 120,
    PARAM_DISPATCH_CUTOFF_SOC: 100,
}

# ─────────────────────── Register types ──────────────────────────────────


class RegisterType(StrEnum):
    INT16 = "int16"
    UINT16 = "uint16"
    INT32 = "int32"
    UINT32 = "uint32"
    STRING = "string"


# ─────────────────────── Sensor description ──────────────────────────────


@dataclass(frozen=True, kw_only=True)
class AlphaESSModbusSensorDescription:
    """Describes a single Modbus sensor register (or pair for 32-bit)."""

    key: str
    name: str
    address: int
    register_type: RegisterType
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = SensorStateClass.MEASUREMENT
    scale: float = 1.0
    offset: float = 0.0
    precision: int | None = None
    enabled_by_default: bool = True
    is_diagnostic: bool = False
    slow_poll: bool = False
    register_count: int | None = None  # only used for STRING type


@dataclass(frozen=True, kw_only=True)
class AlphaESSComputedSensorDescription:
    """Describes a sensor computed from other sensor values."""

    key: str
    name: str
    unit: str | None = None
    device_class: SensorDeviceClass | None = None
    state_class: SensorStateClass | None = SensorStateClass.MEASUREMENT
    precision: int | None = None
    enabled_by_default: bool = True
    is_diagnostic: bool = False


# ───────────────────── Sensor descriptions (static registry) ─────────────

CORE_SENSOR_DESCRIPTIONS = CORE_SENSOR_DEFINITIONS
INTERNAL_REGISTER_DESCRIPTIONS = INTERNAL_REGISTER_DEFINITIONS
COMPUTED_SENSOR_DESCRIPTIONS = COMPUTED_SENSOR_DEFINITIONS


def get_core_sensor_descriptions() -> tuple[AlphaESSModbusSensorDescription, ...]:
    """Return all Modbus sensor descriptions (exposed as entities)."""
    return CORE_SENSOR_DESCRIPTIONS


def get_internal_register_descriptions() -> tuple[AlphaESSModbusSensorDescription, ...]:
    """Return internal register descriptions (read but not exposed)."""
    return INTERNAL_REGISTER_DESCRIPTIONS


def get_computed_sensor_descriptions() -> tuple[AlphaESSComputedSensorDescription, ...]:
    """Return computed sensor descriptions."""
    return COMPUTED_SENSOR_DESCRIPTIONS

# ──────────── kW sensors for ApexCharts power diagrams ───────────────────
# These convert core W-based sensors to kW for use in dashboard charts.
# They are computed entirely in coordinator._compute_derived().

KW_SENSOR_DESCRIPTIONS: tuple[AlphaESSComputedSensorDescription, ...] = (
    AlphaESSComputedSensorDescription(
        key="current_house_load_kw",
        name="Current House Load (kW)",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
    AlphaESSComputedSensorDescription(
        key="current_pv_production_kw",
        name="Current PV Production (kW)",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
    AlphaESSComputedSensorDescription(
        key="power_grid_consumption_kw",
        name="Grid Consumption (kW)",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
    AlphaESSComputedSensorDescription(
        key="power_grid_feed_in_kw",
        name="Grid Feed-In (kW)",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
    AlphaESSComputedSensorDescription(
        key="power_grid_kw",
        name="Grid Power (kW)",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
    AlphaESSComputedSensorDescription(
        key="power_battery_kw",
        name="Battery Power (kW)",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
    AlphaESSComputedSensorDescription(
        key="pv1_power_kw",
        name="PV1 Power (kW)",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
    AlphaESSComputedSensorDescription(
        key="pv2_power_kw",
        name="PV2 Power (kW)",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
    AlphaESSComputedSensorDescription(
        key="excess_power_kw",
        name="Excess Power (kW)",
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        precision=2,
    ),
)
