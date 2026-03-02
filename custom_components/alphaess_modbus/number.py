"""Number platform for the AlphaESS Modbus integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DEFAULT_PARAMS,
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
    REG_CHARGING_CUTOFF_SOC,
    REG_DISCHARGING_CUTOFF_SOC,
    REG_MAX_FEED_TO_GRID,
)
from .entity import AlphaESSBaseEntity

_LOGGER = logging.getLogger(__name__)


# ───────────────────── Description dataclasses ───────────────────────────


@dataclass(frozen=True, kw_only=True)
class AlphaESSWriteNumberDescription:
    """Number entity that reads from coordinator and writes to a register."""

    key: str
    name: str
    register: int
    sensor_key: str  # coordinator data key for current value
    min_value: float
    max_value: float
    step: float
    unit: str | None = None
    mode: NumberMode = NumberMode.SLIDER


@dataclass(frozen=True, kw_only=True)
class AlphaESSLocalNumberDescription:
    """Number entity that stores its value locally in runtime params."""

    key: str
    name: str
    param_key: str  # key in runtime_data.params
    min_value: float
    max_value: float
    step: float
    unit: str | None = None
    mode: NumberMode = NumberMode.SLIDER
    use_ac_limit_max: bool = False  # if True, max comes from AC limit select


# ───────────────────── Write-to-register numbers ─────────────────────────

WRITE_NUMBER_DESCRIPTIONS: tuple[AlphaESSWriteNumberDescription, ...] = (
    AlphaESSWriteNumberDescription(
        key="set_charging_cutoff_soc",
        name="Helper Charging Cutoff SoC",
        register=REG_CHARGING_CUTOFF_SOC,
        sensor_key="charging_cutoff_soc",
        min_value=10,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
    AlphaESSWriteNumberDescription(
        key="set_discharging_cutoff_soc",
        name="Helper Discharging Cutoff SoC",
        register=REG_DISCHARGING_CUTOFF_SOC,
        sensor_key="discharging_cutoff_soc",
        min_value=4,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
    AlphaESSWriteNumberDescription(
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

# ───────────────────── Local parameter numbers ───────────────────────────

LOCAL_NUMBER_DESCRIPTIONS: tuple[AlphaESSLocalNumberDescription, ...] = (
    # Force Charging
    AlphaESSLocalNumberDescription(
        key="force_charging_power",
        name="Template Force Charging Power",
        param_key=PARAM_FORCE_CHARGE_POWER,
        min_value=0,
        max_value=20,
        step=0.1,
        unit=UnitOfPower.KILO_WATT,
        use_ac_limit_max=True,
    ),
    AlphaESSLocalNumberDescription(
        key="force_charging_duration",
        name="Helper Force Charging Duration",
        param_key=PARAM_FORCE_CHARGE_DURATION,
        min_value=0,
        max_value=480,
        step=5,
        unit=UnitOfTime.MINUTES,
    ),
    AlphaESSLocalNumberDescription(
        key="force_charging_cutoff_soc",
        name="Helper Force Charging Cutoff SoC",
        param_key=PARAM_FORCE_CHARGE_CUTOFF_SOC,
        min_value=4,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
    # Force Discharging
    AlphaESSLocalNumberDescription(
        key="force_discharging_power",
        name="Template Force Discharging Power",
        param_key=PARAM_FORCE_DISCHARGE_POWER,
        min_value=0,
        max_value=20,
        step=0.1,
        unit=UnitOfPower.KILO_WATT,
        use_ac_limit_max=True,
    ),
    AlphaESSLocalNumberDescription(
        key="force_discharging_duration",
        name="Helper Force Discharging Duration",
        param_key=PARAM_FORCE_DISCHARGE_DURATION,
        min_value=0,
        max_value=480,
        step=5,
        unit=UnitOfTime.MINUTES,
    ),
    AlphaESSLocalNumberDescription(
        key="force_discharging_cutoff_soc",
        name="Helper Force Discharging Cutoff SoC",
        param_key=PARAM_FORCE_DISCHARGE_CUTOFF_SOC,
        min_value=4,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
    # Force Export
    AlphaESSLocalNumberDescription(
        key="force_export_power",
        name="Template Force Export Power",
        param_key=PARAM_FORCE_EXPORT_POWER,
        min_value=0,
        max_value=20,
        step=0.1,
        unit=UnitOfPower.KILO_WATT,
        use_ac_limit_max=True,
    ),
    AlphaESSLocalNumberDescription(
        key="force_export_duration",
        name="Helper Force Export Duration",
        param_key=PARAM_FORCE_EXPORT_DURATION,
        min_value=0,
        max_value=480,
        step=5,
        unit=UnitOfTime.MINUTES,
    ),
    AlphaESSLocalNumberDescription(
        key="force_export_cutoff_soc",
        name="Helper Force Export Cutoff SoC",
        param_key=PARAM_FORCE_EXPORT_CUTOFF_SOC,
        min_value=4,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
    # Dispatch
    AlphaESSLocalNumberDescription(
        key="dispatch_power",
        name="Template Dispatch Power",
        param_key=PARAM_DISPATCH_POWER,
        min_value=-20,
        max_value=20,
        step=0.1,
        unit=UnitOfPower.KILO_WATT,
    ),
    AlphaESSLocalNumberDescription(
        key="dispatch_duration",
        name="Helper Dispatch Duration",
        param_key=PARAM_DISPATCH_DURATION,
        min_value=0,
        max_value=480,
        step=5,
        unit=UnitOfTime.MINUTES,
    ),
    AlphaESSLocalNumberDescription(
        key="dispatch_cutoff_soc",
        name="Helper Dispatch Cutoff SoC",
        param_key=PARAM_DISPATCH_CUTOFF_SOC,
        min_value=4,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    ),
)


# ───────────────────── Platform setup ────────────────────────────────────


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AlphaESS number entities."""
    runtime = hass.data[DOMAIN][entry.entry_id]
    coordinator = runtime.coordinator
    hub = runtime.hub

    entities: list[NumberEntity] = []

    for desc in WRITE_NUMBER_DESCRIPTIONS:
        entities.append(AlphaESSWriteNumber(coordinator, entry, hub, desc))

    for desc in LOCAL_NUMBER_DESCRIPTIONS:
        entities.append(AlphaESSLocalNumber(coordinator, entry, runtime, desc))

    async_add_entities(entities)


# ───────────────────── Entity classes ────────────────────────────────────


class AlphaESSWriteNumber(AlphaESSBaseEntity, NumberEntity):
    """Number that reads from a Modbus register and writes back on change."""

    def __init__(self, coordinator, entry, hub, description: AlphaESSWriteNumberDescription) -> None:
        super().__init__(coordinator, entry, description.key)
        self._hub = hub
        self._desc = description
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = description.unit
        self._attr_native_min_value = description.min_value
        self._attr_native_max_value = description.max_value
        self._attr_native_step = description.step
        self._attr_mode = description.mode

    @property
    def native_value(self) -> float | None:
        """Return current Modbus register value via coordinator."""
        val = self.coordinator.data.get(self._desc.sensor_key)
        if val is None:
            return None
        return float(val)

    async def async_set_native_value(self, value: float) -> None:
        """Write the new value to the Modbus register."""
        await self._hub.async_write_register(self._desc.register, int(value))
        await self.coordinator.async_request_refresh()


class AlphaESSLocalNumber(AlphaESSBaseEntity, NumberEntity):
    """Number stored locally in runtime params (used by switches)."""

    def __init__(self, coordinator, entry, runtime, description: AlphaESSLocalNumberDescription) -> None:
        super().__init__(coordinator, entry, description.key)
        self._runtime = runtime
        self._desc = description
        self._attr_name = description.name
        self._attr_native_unit_of_measurement = description.unit
        self._attr_native_min_value = description.min_value
        self._attr_native_max_value = description.max_value
        self._attr_native_step = description.step
        self._attr_mode = description.mode

        # Ensure default exists
        if description.param_key not in self._runtime.params:
            self._runtime.params[description.param_key] = DEFAULT_PARAMS.get(
                description.param_key, 0
            )

    @property
    def native_value(self) -> float | None:
        """Return current param value."""
        return self._runtime.params.get(self._desc.param_key)

    @property
    def native_max_value(self) -> float:
        """Dynamic max based on AC limit if applicable."""
        if self._desc.use_ac_limit_max:
            ac_limit = self._runtime.params.get("ac_limit_kw")
            if ac_limit is not None:
                return float(ac_limit)
        return self._desc.max_value

    async def async_set_native_value(self, value: float) -> None:
        """Store the value locally."""
        self._runtime.params[self._desc.param_key] = value
        self.async_write_ha_state()
