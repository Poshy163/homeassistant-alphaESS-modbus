"""Constants for the AlphaESS Modbus integration."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import (
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfFrequency,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
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


# ───────────────────── Modbus sensor descriptions ────────────────────────
# Organised into logical groups matching the YAML reference implementation

_SYSTEM_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="inverter_grid_frequency",
        name="Inverter Grid Frequency",
        address=REG_INVERTER_GRID_FREQUENCY,
        register_type=RegisterType.INT16,
        unit=UnitOfFrequency.HERTZ,
        device_class=SensorDeviceClass.FREQUENCY,
        scale=0.01,
        precision=2,
    ),
    AlphaESSModbusSensorDescription(
        key="inverter_temperature",
        name="Inverter Temperature",
        address=REG_INVERTER_TEMPERATURE,
        register_type=RegisterType.INT16,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        scale=0.1,  # 0.01 for SMILE-B3/SMILE-B3-PLUS
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="inverter_work_mode",
        name="Inverter Work Mode",
        address=REG_INVERTER_WORK_MODE,
        register_type=RegisterType.INT16,
    ),
)

_VERSION_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="bms_version",
        name="BMS Version",
        address=REG_BMS_VERSION,
        register_type=RegisterType.INT16,
        is_diagnostic=True,
    ),
    AlphaESSModbusSensorDescription(
        key="lmu_version",
        name="LMU Version",
        address=REG_LMU_VERSION,
        register_type=RegisterType.INT16,
        is_diagnostic=True,
    ),
    AlphaESSModbusSensorDescription(
        key="iso_version",
        name="ISO Version",
        address=REG_ISO_VERSION,
        register_type=RegisterType.INT16,
        is_diagnostic=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ems_version_high",
        name="EMS Version High",
        address=REG_EMS_VERSION_HIGH,
        register_type=RegisterType.INT16,
        is_diagnostic=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ems_version_middle",
        name="EMS Version Middle",
        address=REG_EMS_VERSION_MIDDLE,
        register_type=RegisterType.INT16,
        is_diagnostic=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ems_version_low",
        name="EMS Version Low",
        address=REG_EMS_VERSION_LOW,
        register_type=RegisterType.INT16,
        is_diagnostic=True,
    ),
    AlphaESSModbusSensorDescription(
        key="inverter_version",
        name="Inverter Version",
        address=REG_INVERTER_VERSION,
        register_type=RegisterType.STRING,
        register_count=5,
        is_diagnostic=True,
        state_class=None,
        slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="inverter_arm_version",
        name="Inverter ARM Version",
        address=REG_INVERTER_ARM_VERSION,
        register_type=RegisterType.STRING,
        register_count=5,
        is_diagnostic=True,
        state_class=None,
        slow_poll=True,
    ),
)

_SYSTEM_TIME_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="system_time_yymm",
        name="System Time YYMM",
        address=REG_SYSTEM_TIME_YYMM,
        register_type=RegisterType.INT16,
        is_diagnostic=True,
    ),
    AlphaESSModbusSensorDescription(
        key="system_time_ddhh",
        name="System Time DDHH",
        address=REG_SYSTEM_TIME_DDHH,
        register_type=RegisterType.INT16,
        is_diagnostic=True,
    ),
    AlphaESSModbusSensorDescription(
        key="system_time_mmss",
        name="System Time MMSS",
        address=REG_SYSTEM_TIME_MMSS,
        register_type=RegisterType.INT16,
        is_diagnostic=True,
    ),
)

_NETWORK_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="modbus_baud_rate",
        name="Modbus Baud Rate",
        address=REG_MODBUS_BAUD_RATE,
        register_type=RegisterType.UINT16,
        is_diagnostic=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ip_method",
        name="IP Method",
        address=REG_IP_METHOD,
        register_type=RegisterType.UINT16,
        is_diagnostic=True,
    ),
)

_POWER_GRID_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="power_phase_a_grid",
        name="Power Phase A Grid",
        address=REG_POWER_PHASE_A_GRID,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="power_phase_b_grid",
        name="Power Phase B Grid",
        address=REG_POWER_PHASE_B_GRID,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="power_phase_c_grid",
        name="Power Phase C Grid",
        address=REG_POWER_PHASE_C_GRID,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="power_grid",
        name="Power Grid",
        address=REG_POWER_GRID,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="voltage_phase_a_grid",
        name="Voltage Phase A Grid",
        address=REG_VOLTAGE_PHASE_A_GRID,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="voltage_phase_b_grid",
        name="Voltage Phase B Grid",
        address=REG_VOLTAGE_PHASE_B_GRID,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="voltage_phase_c_grid",
        name="Voltage Phase C Grid",
        address=REG_VOLTAGE_PHASE_C_GRID,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        scale=0.1,
        precision=1,
    ),
)

_POWER_BATTERY_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="power_battery",
        name="Power Battery",
        address=REG_POWER_BATTERY,
        register_type=RegisterType.INT16,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
)

_INVERTER_POWER_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="power_inverter_l1",
        name="Power Inverter L1",
        address=REG_POWER_INVERTER_L1,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="power_inverter_l2",
        name="Power Inverter L2",
        address=REG_POWER_INVERTER_L2,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="power_inverter_l3",
        name="Power Inverter L3",
        address=REG_POWER_INVERTER_L3,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="power_inverter",
        name="Power Inverter",
        address=REG_POWER_INVERTER,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="backup_power_inverter_l1",
        name="Backup Power Inverter L1",
        address=REG_BACKUP_POWER_INVERTER_L1,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="backup_power_inverter_l2",
        name="Backup Power Inverter L2",
        address=REG_BACKUP_POWER_INVERTER_L2,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="backup_power_inverter_l3",
        name="Backup Power Inverter L3",
        address=REG_BACKUP_POWER_INVERTER_L3,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="backup_power_inverter",
        name="Backup Power Inverter",
        address=REG_BACKUP_POWER_INVERTER,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="active_power_pv_meter",
        name="Active Power PV Meter",
        address=REG_ACTIVE_POWER_PV_METER,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
)

_PV_STRING_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    # PV1
    AlphaESSModbusSensorDescription(
        key="pv1_power",
        name="PV1 Power",
        address=REG_PV1_POWER,
        register_type=RegisterType.UINT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="pv1_voltage",
        name="PV1 Voltage",
        address=REG_PV1_VOLTAGE,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="pv1_current",
        name="PV1 Current",
        address=REG_PV1_CURRENT,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        scale=0.1,
        precision=2,
    ),
    # PV2
    AlphaESSModbusSensorDescription(
        key="pv2_power",
        name="PV2 Power",
        address=REG_PV2_POWER,
        register_type=RegisterType.UINT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="pv2_voltage",
        name="PV2 Voltage",
        address=REG_PV2_VOLTAGE,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="pv2_current",
        name="PV2 Current",
        address=REG_PV2_CURRENT,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        scale=0.1,
        precision=2,
    ),
    # PV3
    AlphaESSModbusSensorDescription(
        key="pv3_power",
        name="PV3 Power",
        address=REG_PV3_POWER,
        register_type=RegisterType.UINT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="pv3_voltage",
        name="PV3 Voltage",
        address=REG_PV3_VOLTAGE,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="pv3_current",
        name="PV3 Current",
        address=REG_PV3_CURRENT,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        scale=0.1,
        precision=2,
    ),
    # PV4
    AlphaESSModbusSensorDescription(
        key="pv4_power",
        name="PV4 Power",
        address=REG_PV4_POWER,
        register_type=RegisterType.UINT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="pv4_voltage",
        name="PV4 Voltage",
        address=REG_PV4_VOLTAGE,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="pv4_current",
        name="PV4 Current",
        address=REG_PV4_CURRENT,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        scale=0.1,
        precision=2,
    ),
)

_ENERGY_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="total_energy_feed_to_grid_meter",
        name="Total Energy Feed to Grid (Meter)",
        address=REG_TOTAL_ENERGY_FEED_TO_GRID_METER,
        register_type=RegisterType.UINT32,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        scale=0.01,
        precision=2,
    ),
    AlphaESSModbusSensorDescription(
        key="total_energy_consumption_from_grid_meter",
        name="Total Energy Consumption from Grid (Meter)",
        address=REG_TOTAL_ENERGY_CONSUMPTION_FROM_GRID_METER,
        register_type=RegisterType.UINT32,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        scale=0.01,
        precision=2,
    ),
    AlphaESSModbusSensorDescription(
        key="total_energy_feed_to_grid_pv",
        name="Total Energy Feed to Grid (PV)",
        address=REG_TOTAL_ENERGY_FEED_TO_GRID_PV,
        register_type=RegisterType.UINT32,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        scale=0.01,
        precision=2,
    ),
    AlphaESSModbusSensorDescription(
        key="total_energy_charge_battery",
        name="Total Energy Charge Battery",
        address=REG_TOTAL_ENERGY_CHARGE_BATTERY,
        register_type=RegisterType.UINT32,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        scale=0.1,
        precision=2,
    ),
    AlphaESSModbusSensorDescription(
        key="total_energy_discharge_battery",
        name="Total Energy Discharge Battery",
        address=REG_TOTAL_ENERGY_DISCHARGE_BATTERY,
        register_type=RegisterType.UINT32,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        scale=0.1,
        precision=2,
    ),
    AlphaESSModbusSensorDescription(
        key="total_energy_charge_battery_from_grid",
        name="Total Energy Charge Battery from Grid",
        address=REG_TOTAL_ENERGY_CHARGE_BATTERY_FROM_GRID,
        register_type=RegisterType.UINT32,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        scale=0.1,
        precision=2,
    ),
    AlphaESSModbusSensorDescription(
        key="total_energy_from_pv",
        name="Total Energy from PV",
        address=REG_TOTAL_ENERGY_FROM_PV,
        register_type=RegisterType.UINT32,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        scale=0.1,
        precision=2,
    ),
)

_BATTERY_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="soc_battery",
        name="SoC Battery",
        address=REG_SOC_BATTERY,
        register_type=RegisterType.INT16,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="soh_battery",
        name="SoH Battery",
        address=REG_SOH_BATTERY,
        register_type=RegisterType.INT16,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_status",
        name="Battery Status",
        address=REG_BATTERY_STATUS,
        register_type=RegisterType.INT16,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_voltage",
        name="Battery Voltage",
        address=REG_BATTERY_VOLTAGE,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        scale=0.1,
        precision=2,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_current",
        name="Battery Current",
        address=REG_BATTERY_CURRENT,
        register_type=RegisterType.INT16,
        unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        scale=0.1,
        precision=2,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_min_cell_temp",
        name="Battery Min Cell Temp",
        address=REG_BATTERY_MIN_CELL_TEMP,
        register_type=RegisterType.UINT16,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_max_cell_temp",
        name="Battery Max Cell Temp",
        address=REG_BATTERY_MAX_CELL_TEMP,
        register_type=RegisterType.UINT16,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_max_charge_current",
        name="Battery Max Charge Current",
        address=REG_BATTERY_MAX_CHARGE_CURRENT,
        register_type=RegisterType.UINT16,
        unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_max_discharge_current",
        name="Battery Max Discharge Current",
        address=REG_BATTERY_MAX_DISCHARGE_CURRENT,
        register_type=RegisterType.UINT16,
        unit=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        scale=0.1,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_remaining_time",
        name="Battery Remaining Time",
        address=REG_BATTERY_REMAINING_TIME,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.MINUTES,
    ),
)

_PV_SETTING_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="max_feed_to_grid",
        name="Max Feed to Grid",
        address=REG_MAX_FEED_TO_GRID,
        register_type=RegisterType.UINT16,
        unit=PERCENTAGE,
    ),
    AlphaESSModbusSensorDescription(
        key="pv_capacity_storage",
        name="PV Capacity Storage",
        address=REG_PV_CAPACITY_STORAGE,
        register_type=RegisterType.UINT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSModbusSensorDescription(
        key="pv_capacity_grid_inverter",
        name="PV Capacity of Grid Inverter",
        address=REG_PV_CAPACITY_GRID_INVERTER,
        register_type=RegisterType.UINT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
)

_GRID_METER_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="ct_rate_grid_meter",
        name="CT Rate Grid Meter",
        address=REG_CT_RATE_GRID_METER,
        register_type=RegisterType.UINT16,
        is_diagnostic=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ct_rate_pv_meter",
        name="CT Rate PV Meter",
        address=REG_CT_RATE_PV_METER,
        register_type=RegisterType.UINT16,
        is_diagnostic=True,
    ),
)

_CHARGING_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="charging_time_period_control",
        name="Charging Time Period Control",
        address=REG_TIME_PERIOD_CONTROL,
        register_type=RegisterType.INT16,
    ),
    AlphaESSModbusSensorDescription(
        key="charging_cutoff_soc",
        name="Charging Cutoff SoC",
        address=REG_CHARGING_CUTOFF_SOC,
        register_type=RegisterType.INT16,
        unit=PERCENTAGE,
    ),
    AlphaESSModbusSensorDescription(
        key="charging_period_1_start_hour",
        name="Charging Period 1 Start Hour",
        address=REG_CHARGING_PERIOD_1_START_HOUR,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.HOURS,
    ),
    AlphaESSModbusSensorDescription(
        key="charging_period_1_stop_hour",
        name="Charging Period 1 Stop Hour",
        address=REG_CHARGING_PERIOD_1_STOP_HOUR,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.HOURS,
    ),
    AlphaESSModbusSensorDescription(
        key="charging_period_2_start_hour",
        name="Charging Period 2 Start Hour",
        address=REG_CHARGING_PERIOD_2_START_HOUR,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.HOURS,
    ),
    AlphaESSModbusSensorDescription(
        key="charging_period_2_stop_hour",
        name="Charging Period 2 Stop Hour",
        address=REG_CHARGING_PERIOD_2_STOP_HOUR,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.HOURS,
    ),
    AlphaESSModbusSensorDescription(
        key="charging_period_1_start_minute",
        name="Charging Period 1 Start Minute",
        address=REG_CHARGING_PERIOD_1_START_MINUTE,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.MINUTES,
    ),
    AlphaESSModbusSensorDescription(
        key="charging_period_1_stop_minute",
        name="Charging Period 1 Stop Minute",
        address=REG_CHARGING_PERIOD_1_STOP_MINUTE,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.MINUTES,
    ),
    AlphaESSModbusSensorDescription(
        key="charging_period_2_start_minute",
        name="Charging Period 2 Start Minute",
        address=REG_CHARGING_PERIOD_2_START_MINUTE,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.MINUTES,
    ),
    AlphaESSModbusSensorDescription(
        key="charging_period_2_stop_minute",
        name="Charging Period 2 Stop Minute",
        address=REG_CHARGING_PERIOD_2_STOP_MINUTE,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.MINUTES,
    ),
)

_DISCHARGING_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="discharging_cutoff_soc",
        name="Discharging Cutoff SoC",
        address=REG_DISCHARGING_CUTOFF_SOC,
        register_type=RegisterType.INT16,
        unit=PERCENTAGE,
    ),
    AlphaESSModbusSensorDescription(
        key="discharging_period_1_start_hour",
        name="Discharging Period 1 Start Hour",
        address=REG_DISCHARGING_PERIOD_1_START_HOUR,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.HOURS,
    ),
    AlphaESSModbusSensorDescription(
        key="discharging_period_1_stop_hour",
        name="Discharging Period 1 Stop Hour",
        address=REG_DISCHARGING_PERIOD_1_STOP_HOUR,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.HOURS,
    ),
    AlphaESSModbusSensorDescription(
        key="discharging_period_2_start_hour",
        name="Discharging Period 2 Start Hour",
        address=REG_DISCHARGING_PERIOD_2_START_HOUR,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.HOURS,
    ),
    AlphaESSModbusSensorDescription(
        key="discharging_period_2_stop_hour",
        name="Discharging Period 2 Stop Hour",
        address=REG_DISCHARGING_PERIOD_2_STOP_HOUR,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.HOURS,
    ),
    AlphaESSModbusSensorDescription(
        key="discharging_period_1_start_minute",
        name="Discharging Period 1 Start Minute",
        address=REG_DISCHARGING_PERIOD_1_START_MINUTE,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.MINUTES,
    ),
    AlphaESSModbusSensorDescription(
        key="discharging_period_1_stop_minute",
        name="Discharging Period 1 Stop Minute",
        address=REG_DISCHARGING_PERIOD_1_STOP_MINUTE,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.MINUTES,
    ),
    AlphaESSModbusSensorDescription(
        key="discharging_period_2_start_minute",
        name="Discharging Period 2 Start Minute",
        address=REG_DISCHARGING_PERIOD_2_START_MINUTE,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.MINUTES,
    ),
    AlphaESSModbusSensorDescription(
        key="discharging_period_2_stop_minute",
        name="Discharging Period 2 Stop Minute",
        address=REG_DISCHARGING_PERIOD_2_STOP_MINUTE,
        register_type=RegisterType.INT16,
        unit=UnitOfTime.MINUTES,
    ),
)

_DISPATCH_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="dispatch_start",
        name="Dispatch Start",
        address=REG_DISPATCH_START,
        register_type=RegisterType.INT16,
    ),
    AlphaESSModbusSensorDescription(
        key="dispatch_active_power",
        name="Dispatch Active Power",
        address=REG_DISPATCH_ACTIVE_POWER,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        offset=-DISPATCH_POWER_OFFSET,
    ),
    AlphaESSModbusSensorDescription(
        key="dispatch_reactive_power",
        name="Dispatch Reactive Power",
        address=REG_DISPATCH_REACTIVE_POWER,
        register_type=RegisterType.INT32,
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        offset=-DISPATCH_POWER_OFFSET,
    ),
    AlphaESSModbusSensorDescription(
        key="dispatch_mode",
        name="Dispatch Mode",
        address=REG_DISPATCH_MODE,
        register_type=RegisterType.INT16,
    ),
    AlphaESSModbusSensorDescription(
        key="dispatch_soc",
        name="Dispatch SoC",
        address=REG_DISPATCH_SOC,
        register_type=RegisterType.INT16,
        unit=PERCENTAGE,
        scale=DISPATCH_SOC_SCALE,
        precision=1,
    ),
    AlphaESSModbusSensorDescription(
        key="dispatch_time",
        name="Dispatch Time",
        address=REG_DISPATCH_TIME,
        register_type=RegisterType.UINT32,
        unit=UnitOfTime.SECONDS,
    ),
)

_WARNING_FAULT_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="system_fault",
        name="System Fault",
        address=REG_SYSTEM_FAULT,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="inverter_warning_1",
        name="Inverter Warning 1",
        address=REG_INVERTER_WARNING_1,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="inverter_warning_2",
        name="Inverter Warning 2",
        address=REG_INVERTER_WARNING_2,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="inverter_fault_1",
        name="Inverter Fault 1",
        address=REG_INVERTER_FAULT_1,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="inverter_fault_2",
        name="Inverter Fault 2",
        address=REG_INVERTER_FAULT_2,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_warning",
        name="Battery Warning",
        address=REG_BATTERY_WARNING,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_1_warning",
        name="Battery 1 Warning",
        address=REG_BATTERY_1_WARNING,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_2_warning",
        name="Battery 2 Warning",
        address=REG_BATTERY_2_WARNING,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_3_warning",
        name="Battery 3 Warning",
        address=REG_BATTERY_3_WARNING,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_4_warning",
        name="Battery 4 Warning",
        address=REG_BATTERY_4_WARNING,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_5_warning",
        name="Battery 5 Warning",
        address=REG_BATTERY_5_WARNING,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_6_warning",
        name="Battery 6 Warning",
        address=REG_BATTERY_6_WARNING,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_fault",
        name="Battery Fault",
        address=REG_BATTERY_FAULT,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_1_fault",
        name="Battery 1 Fault",
        address=REG_BATTERY_1_FAULT,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_2_fault",
        name="Battery 2 Fault",
        address=REG_BATTERY_2_FAULT,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_3_fault",
        name="Battery 3 Fault",
        address=REG_BATTERY_3_FAULT,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_4_fault",
        name="Battery 4 Fault",
        address=REG_BATTERY_4_FAULT,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_5_fault",
        name="Battery 5 Fault",
        address=REG_BATTERY_5_FAULT,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="battery_6_fault",
        name="Battery 6 Fault",
        address=REG_BATTERY_6_FAULT,
        register_type=RegisterType.UINT32,
    ),
)

_GRID_SAFETY_SENSORS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="grid_regulation",
        name="Grid Regulation",
        address=REG_GRID_REGULATION,
        register_type=RegisterType.INT16,
        is_diagnostic=True, slow_poll=True,
    ),
    # Overvoltage Protection
    AlphaESSModbusSensorDescription(
        key="ovp_l1", name="OvP L1", address=REG_OVP_L1,
        register_type=RegisterType.INT16, unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, scale=0.1, precision=1,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ovp_l1_time", name="OvP L1 Time", address=REG_OVP_L1_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ovp_l2", name="OvP L2", address=REG_OVP_L2,
        register_type=RegisterType.INT16, unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, scale=0.1, precision=1,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ovp_l2_time", name="OvP L2 Time", address=REG_OVP_L2_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ovp_l3", name="OvP L3", address=REG_OVP_L3,
        register_type=RegisterType.INT16, unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, scale=0.1, precision=1,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ovp_l3_time", name="OvP L3 Time", address=REG_OVP_L3_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ovp10", name="OvP10", address=REG_OVP10,
        register_type=RegisterType.INT16, unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, scale=0.1, precision=1,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ovp10_time", name="OvP10 Time", address=REG_OVP10_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    # Undervoltage Protection
    AlphaESSModbusSensorDescription(
        key="uvp_l1", name="UvP L1", address=REG_UVP_L1,
        register_type=RegisterType.INT16, unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, scale=0.1, precision=1,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="uvp_l1_time", name="UvP L1 Time", address=REG_UVP_L1_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="uvp_l2", name="UvP L2", address=REG_UVP_L2,
        register_type=RegisterType.INT16, unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, scale=0.1, precision=1,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="uvp_l2_time", name="UvP L2 Time", address=REG_UVP_L2_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="uvp_l3", name="UvP L3", address=REG_UVP_L3,
        register_type=RegisterType.INT16, unit=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE, scale=0.1, precision=1,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="uvp_l3_time", name="UvP L3 Time", address=REG_UVP_L3_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    # Overfrequency Protection
    AlphaESSModbusSensorDescription(
        key="ofp_l1", name="OfP L1", address=REG_OFP_L1,
        register_type=RegisterType.INT16, unit=UnitOfFrequency.HERTZ,
        scale=0.01, precision=2, is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ofp_l1_time", name="OfP L1 Time", address=REG_OFP_L1_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ofp_l2", name="OfP L2", address=REG_OFP_L2,
        register_type=RegisterType.INT16, unit=UnitOfFrequency.HERTZ,
        scale=0.01, precision=2, is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ofp_l2_time", name="OfP L2 Time", address=REG_OFP_L2_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ofp_l3", name="OfP L3", address=REG_OFP_L3,
        register_type=RegisterType.INT16, unit=UnitOfFrequency.HERTZ,
        scale=0.01, precision=2, is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ofp_l3_time", name="OfP L3 Time", address=REG_OFP_L3_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    # Underfrequency Protection
    AlphaESSModbusSensorDescription(
        key="ufp_l1", name="UfP L1", address=REG_UFP_L1,
        register_type=RegisterType.INT16, unit=UnitOfFrequency.HERTZ,
        scale=0.01, precision=2, is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ufp_l1_time", name="UfP L1 Time", address=REG_UFP_L1_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ufp_l2", name="UfP L2", address=REG_UFP_L2,
        register_type=RegisterType.INT16, unit=UnitOfFrequency.HERTZ,
        scale=0.01, precision=2, is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ufp_l2_time", name="UfP L2 Time", address=REG_UFP_L2_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ufp_l3", name="UfP L3", address=REG_UFP_L3,
        register_type=RegisterType.INT16, unit=UnitOfFrequency.HERTZ,
        scale=0.01, precision=2, is_diagnostic=True, slow_poll=True,
    ),
    AlphaESSModbusSensorDescription(
        key="ufp_l3_time", name="UfP L3 Time", address=REG_UFP_L3_TIME,
        register_type=RegisterType.INT16, unit=UnitOfTime.MILLISECONDS,
        is_diagnostic=True, slow_poll=True,
    ),
)

# ─────────── Combined: all Modbus sensor descriptions ────────────────────

# Registers read by the coordinator for computed values but not exposed as entities.
INTERNAL_REGISTER_DESCRIPTIONS: tuple[AlphaESSModbusSensorDescription, ...] = (
    AlphaESSModbusSensorDescription(
        key="local_ip",
        name="Local IP",
        address=REG_LOCAL_IP,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="subnet_mask",
        name="Subnet Mask",
        address=REG_SUBNET_MASK,
        register_type=RegisterType.UINT32,
    ),
    AlphaESSModbusSensorDescription(
        key="gateway",
        name="Gateway",
        address=REG_GATEWAY,
        register_type=RegisterType.UINT32,
    ),
)

CORE_SENSOR_DESCRIPTIONS: tuple[AlphaESSModbusSensorDescription, ...] = (
    *_SYSTEM_SENSORS,
    *_VERSION_SENSORS,
    *_SYSTEM_TIME_SENSORS,
    *_NETWORK_SENSORS,
    *_POWER_GRID_SENSORS,
    *_POWER_BATTERY_SENSORS,
    *_INVERTER_POWER_SENSORS,
    *_PV_STRING_SENSORS,
    *_ENERGY_SENSORS,
    *_BATTERY_SENSORS,
    *_PV_SETTING_SENSORS,
    *_GRID_METER_SENSORS,
    *_CHARGING_SENSORS,
    *_DISCHARGING_SENSORS,
    *_DISPATCH_SENSORS,
    *_WARNING_FAULT_SENSORS,
    *_GRID_SAFETY_SENSORS,
)

# ────────── Computed / template sensor descriptions ──────────────────────

COMPUTED_SENSOR_DESCRIPTIONS: tuple[AlphaESSComputedSensorDescription, ...] = (
    AlphaESSComputedSensorDescription(
        key="current_pv_production",
        name="Current PV Production",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSComputedSensorDescription(
        key="current_house_load",
        name="Current House Load",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSComputedSensorDescription(
        key="total_house_load",
        name="Total House Load",
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        precision=2,
    ),
    AlphaESSComputedSensorDescription(
        key="excess_power",
        name="Excess Power",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
    AlphaESSComputedSensorDescription(
        key="charging_period_1",
        name="Charging Period 1",
        state_class=None,
    ),
    AlphaESSComputedSensorDescription(
        key="charging_period_2",
        name="Charging Period 2",
        state_class=None,
    ),
    AlphaESSComputedSensorDescription(
        key="discharging_period_1",
        name="Discharging Period 1",
        state_class=None,
    ),
    AlphaESSComputedSensorDescription(
        key="discharging_period_2",
        name="Discharging Period 2",
        state_class=None,
    ),
    AlphaESSComputedSensorDescription(
        key="local_ip_normalised",
        name="Local IP Normalised",
        state_class=None,
        is_diagnostic=True,
    ),
    AlphaESSComputedSensorDescription(
        key="subnet_mask_normalised",
        name="Subnet Mask Normalised",
        state_class=None,
        is_diagnostic=True,
    ),
    AlphaESSComputedSensorDescription(
        key="gateway_normalised",
        name="Gateway Normalised",
        state_class=None,
        is_diagnostic=True,
    ),
    AlphaESSComputedSensorDescription(
        key="bms_version_normalised",
        name="BMS Version Normalised",
        state_class=None,
        is_diagnostic=True,
    ),
    AlphaESSComputedSensorDescription(
        key="ems_version_normalised",
        name="EMS Version Normalised",
        state_class=None,
        is_diagnostic=True,
    ),
    AlphaESSComputedSensorDescription(
        key="system_date",
        name="System Date",
        state_class=None,
        is_diagnostic=True,
    ),
    AlphaESSComputedSensorDescription(
        key="system_time",
        name="System Time",
        state_class=None,
        is_diagnostic=True,
    ),
    AlphaESSComputedSensorDescription(
        key="clipping",
        name="Clipping",
        unit=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
    ),
)
