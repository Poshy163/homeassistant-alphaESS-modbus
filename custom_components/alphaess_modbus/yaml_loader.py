"""Load sensor definitions from integration_alpha_ess.yaml at startup.

This module parses Axel Koegler's native Home Assistant packages YAML
(integration_alpha_ess.yaml) and extracts:

  * Modbus sensor definitions  → AlphaESSModbusSensorDescription
  * Template sensor metadata   → AlphaESSComputedSensorDescription

The YAML file is the single source of truth for register definitions.
Adding a new Modbus sensor to that file is all that's needed — no Python
changes required (unless the sensor needs a new computed/derived value
in coordinator.py).
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml

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

_LOGGER = logging.getLogger(__name__)

# ─────────────────────── Custom YAML loader ──────────────────────────────
# integration_alpha_ess.yaml uses !secret tags for host/port/slave.
# We need a loader that silently handles these instead of crashing.


class _AlphaYAMLLoader(yaml.SafeLoader):
    """YAML SafeLoader subclass that tolerates !secret / !include tags."""


def _secret_constructor(loader: yaml.Loader, node: yaml.Node) -> str:
    """Return a placeholder string for !secret references."""
    return f"__secret_{loader.construct_scalar(node)}__"


_AlphaYAMLLoader.add_constructor("!secret", _secret_constructor)
_AlphaYAMLLoader.add_constructor("!include", _secret_constructor)

# ─────────────────────── Mapping tables ──────────────────────────────────

_UNIT_MAP: dict[str, str] = {
    "Hz": UnitOfFrequency.HERTZ,
    "°C": UnitOfTemperature.CELSIUS,
    "W": UnitOfPower.WATT,
    "kW": UnitOfPower.KILO_WATT,
    "V": UnitOfElectricPotential.VOLT,
    "A": UnitOfElectricCurrent.AMPERE,
    "kWh": UnitOfEnergy.KILO_WATT_HOUR,
    "Wh": UnitOfEnergy.WATT_HOUR,
    "%": PERCENTAGE,
    "h": UnitOfTime.HOURS,
    "m": UnitOfTime.MINUTES,
    "min": UnitOfTime.MINUTES,
    "s": UnitOfTime.SECONDS,
    "ms": UnitOfTime.MILLISECONDS,
}

_DEVICE_CLASS_MAP: dict[str, SensorDeviceClass] = {
    "frequency": SensorDeviceClass.FREQUENCY,
    "temperature": SensorDeviceClass.TEMPERATURE,
    "power": SensorDeviceClass.POWER,
    "voltage": SensorDeviceClass.VOLTAGE,
    "current": SensorDeviceClass.CURRENT,
    "energy": SensorDeviceClass.ENERGY,
    "battery": SensorDeviceClass.BATTERY,
}

_STATE_CLASS_MAP: dict[str, SensorStateClass] = {
    "measurement": SensorStateClass.MEASUREMENT,
    "total_increasing": SensorStateClass.TOTAL_INCREASING,
    "total": SensorStateClass.TOTAL,
}

# ─────────────────────── Name → key derivation ──────────────────────────

_NAME_PREFIX = "AlphaESS "
_NAME_PREFIX_ALT = "AlphaEss "  # Some template sensors use this casing

# Explicit overrides for names whose auto-derived key doesn't match
# what coordinator.py / other code expects.
_KEY_OVERRIDES: dict[str, str] = {
    "AlphaESS PV Capacity of Grid Inverter": "pv_capacity_grid_inverter",
}

# Keys that coordinator.py's _compute_derived() knows how to calculate.
# Only template sensors matching these keys are included as computed
# sensor descriptions — the rest are ignored (they belong in
# packages_extras.yaml or the user's own config).
_COMPUTED_KEYS: frozenset[str] = frozenset({
    "current_pv_production",
    "current_house_load",
    "total_house_load",
    "excess_power",
    "clipping",
    "charging_period_1",
    "charging_period_2",
    "discharging_period_1",
    "discharging_period_2",
    "local_ip_normalised",
    "subnet_mask_normalised",
    "gateway_normalised",
    "bms_version_normalised",
    "ems_version_normalised",
    "system_date",
    "system_time",
    "battery_full",
})

# Grid-safety register address range — sensors here are marked diagnostic.
_GRID_SAFETY_ADDR_MIN = 0x1000
_GRID_SAFETY_ADDR_MAX = 0x1024

# Keywords in the derived key that indicate a diagnostic sensor.
_DIAGNOSTIC_KEYWORDS = frozenset({
    "version", "ip_method", "baud_rate", "grid_regulation",
})


def _name_to_key(name: str) -> str:
    """Derive a snake_case key from an AlphaESS sensor name.

    Examples:
        "AlphaESS Inverter Grid Frequency" → "inverter_grid_frequency"
        "AlphaESS Total Energy Feed to Grid (Meter)" → "total_energy_feed_to_grid_meter"
        "AlphaESS PV Capacity of Grid Inverter" → "pv_capacity_grid_inverter"  (override)
    """
    if name in _KEY_OVERRIDES:
        return _KEY_OVERRIDES[name]

    # Strip prefix
    stripped = name
    if stripped.startswith(_NAME_PREFIX):
        stripped = stripped[len(_NAME_PREFIX) :]
    elif stripped.startswith(_NAME_PREFIX_ALT):
        stripped = stripped[len(_NAME_PREFIX_ALT) :]

    # Remove parentheses
    stripped = stripped.replace("(", "").replace(")", "")

    # Lower-case, spaces/hyphens → underscores
    key = stripped.lower().strip().replace(" ", "_").replace("-", "_")

    # Collapse consecutive underscores, strip leading/trailing
    key = re.sub(r"_+", "_", key).strip("_")

    return key


def _strip_display_prefix(name: str) -> str:
    """Strip 'AlphaESS ' / 'AlphaEss ' prefix for entity display name.

    The entity base class already sets device name = "AlphaESS" with
    ``has_entity_name = True``, so including the prefix in the entity
    name would double it up.
    """
    if name.startswith(_NAME_PREFIX):
        return name[len(_NAME_PREFIX) :]
    if name.startswith(_NAME_PREFIX_ALT):
        return name[len(_NAME_PREFIX_ALT) :]
    return name


def _is_diagnostic(key: str, address: int) -> bool:
    """Heuristic: mark version/network/grid-safety sensors as diagnostic."""
    if _GRID_SAFETY_ADDR_MIN <= address <= _GRID_SAFETY_ADDR_MAX:
        return True
    return any(kw in key for kw in _DIAGNOSTIC_KEYWORDS)


# ─────────────────────── File loading ────────────────────────────────────

_YAML_FILENAME = "integration_alpha_ess.yaml"


def _load_yaml() -> dict[str, Any]:
    """Read and parse integration_alpha_ess.yaml from this package dir."""
    yaml_path = Path(__file__).parent / _YAML_FILENAME
    with open(yaml_path, encoding="utf-8") as fh:
        return yaml.load(fh, Loader=_AlphaYAMLLoader) or {}


# ─────────────────────── Modbus sensor loader ────────────────────────────


def load_modbus_sensor_defs() -> tuple[
    "tuple[Any, ...]",  # core  (exposed as entities)
    "tuple[Any, ...]",  # internal  (read but not exposed; currently empty)
]:
    """Parse the ``modbus:`` section of integration_alpha_ess.yaml.

    Returns ``(core_descriptions, internal_descriptions)``.
    All sensors from Axel's file are returned as *core* (exposed as
    entities).  The *internal* tuple is always empty but kept for API
    compatibility with coordinator.py / sensor.py.
    """
    from .const import AlphaESSModbusSensorDescription, RegisterType

    data = _load_yaml()

    modbus_list = data.get("modbus", [])
    if not modbus_list:
        _LOGGER.warning("No 'modbus:' section found in %s", _YAML_FILENAME)
        return (), ()

    hub = modbus_list[0]
    sensors_raw: list[dict[str, Any]] = hub.get("sensors", [])

    core: list[AlphaESSModbusSensorDescription] = []

    for entry in sensors_raw:
        try:
            name: str = entry["name"]
            address: int = int(entry["address"])
            raw_type: str = entry.get("data_type", "int16")

            reg_type = RegisterType(raw_type)
            key = _name_to_key(name)
            display_name = _strip_display_prefix(name)

            # ── Unit ─────────────────────────────────────────────────
            unit_str = entry.get("unit_of_measurement")
            unit = _UNIT_MAP.get(unit_str) if unit_str else None  # type: ignore[arg-type]

            # ── Device class ─────────────────────────────────────────
            dc_str = entry.get("device_class")
            device_class = _DEVICE_CLASS_MAP.get(dc_str) if dc_str else None  # type: ignore[arg-type]

            # ── State class ──────────────────────────────────────────
            sc_str = entry.get("state_class")
            if sc_str:
                state_class = _STATE_CLASS_MAP.get(sc_str, SensorStateClass.MEASUREMENT)
            elif raw_type == "string":
                state_class = None  # strings have no numeric state class
            else:
                state_class = SensorStateClass.MEASUREMENT

            # ── Scan interval → slow_poll ────────────────────────────
            scan_interval = int(entry.get("scan_interval", 5))
            slow_poll = scan_interval >= 30

            # ── Diagnostic ───────────────────────────────────────────
            is_diag = _is_diagnostic(key, address)

            desc = AlphaESSModbusSensorDescription(
                key=key,
                name=display_name,
                address=address,
                register_type=reg_type,
                unit=unit,
                device_class=device_class,
                state_class=state_class,
                scale=float(entry.get("scale", 1.0)),
                offset=float(entry.get("offset", 0.0)),
                precision=entry.get("precision"),
                enabled_by_default=True,
                is_diagnostic=is_diag,
                slow_poll=slow_poll,
                register_count=entry.get("count"),
            )
            core.append(desc)

        except Exception:
            _LOGGER.exception(
                "Error parsing modbus sensor: %s", entry.get("name", "???")
            )

    _LOGGER.debug(
        "Loaded %d modbus sensor definitions from %s",
        len(core),
        _YAML_FILENAME,
    )
    return tuple(core), ()  # internal is always empty


# ─────────────────────── Computed sensor loader ──────────────────────────


def load_computed_sensor_defs() -> "tuple[Any, ...]":
    """Parse the ``template:`` section for sensors computed by coordinator.py.

    Only template sensors whose derived key appears in ``_COMPUTED_KEYS``
    are returned.  Everything else (ApexCharts helpers, Today's House Load,
    template numbers, etc.) is ignored — those belong in the user's
    packages config, not in the integration.
    """
    from .const import AlphaESSComputedSensorDescription

    data = _load_yaml()

    template_list = data.get("template", [])
    result: list[AlphaESSComputedSensorDescription] = []

    for block in template_list:
        sensors = block.get("sensor", [])
        if not isinstance(sensors, list):
            continue

        for entry in sensors:
            try:
                name: str = entry.get("name", "")
                key = _name_to_key(name)

                if key not in _COMPUTED_KEYS:
                    continue

                display_name = _strip_display_prefix(name)

                unit_str = entry.get("unit_of_measurement")
                unit = _UNIT_MAP.get(unit_str) if unit_str else None  # type: ignore[arg-type]

                dc_str = entry.get("device_class")
                device_class = _DEVICE_CLASS_MAP.get(dc_str) if dc_str else None  # type: ignore[arg-type]

                sc_str = entry.get("state_class")
                state_class = _STATE_CLASS_MAP.get(sc_str) if sc_str else None  # type: ignore[arg-type]

                desc = AlphaESSComputedSensorDescription(
                    key=key,
                    name=display_name,
                    unit=unit,
                    device_class=device_class,
                    state_class=state_class,
                    enabled_by_default=True,
                    is_diagnostic=False,
                )
                result.append(desc)

            except Exception:
                _LOGGER.exception(
                    "Error parsing template sensor: %s",
                    entry.get("name", "???"),
                )

    _LOGGER.debug(
        "Loaded %d computed sensor definitions from %s",
        len(result),
        _YAML_FILENAME,
    )
    return tuple(result)
