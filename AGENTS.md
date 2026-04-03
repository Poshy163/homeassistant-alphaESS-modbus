# AGENTS.md

## Project Overview

Home Assistant custom integration for AlphaESS inverters via Modbus TCP. Distributed through HACS. All code lives under `custom_components/alphaess_modbus/`. There is no test suite or build system — validation happens by loading the integration in a live Home Assistant instance.

## Architecture

**Data flow:** `hub.py` (Modbus TCP via pymodbus) → `coordinator.py` (polling + derived values) → platform files (`sensor.py`, `switch.py`, `number.py`, `select.py`, `time.py`, `binary_sensor.py`, `button.py`)

- **`hub.py`** — Wraps `AsyncModbusTcpClient`. All register reads/writes go through `async_read_value()` and `async_write_register(s)()`. Uses a single asyncio lock for connection safety.
- **`coordinator.py`** — `DataUpdateCoordinator` subclass. Reads every register from the static registry each poll cycle, applies model-specific scaling (B3 correction), then computes ~20 derived sensors in `_compute_derived()`. Three-tier polling: fast (1s subset), regular (5s), slow (~60s diagnostics). Raises `UpdateFailed` after 3 consecutive total poll failures so HA properly marks entities unavailable.
- **`const.py`** — Central constants file. Contains register addresses (`REG_*`), dataclasses (`AlphaESSModbusSensorDescription`, `AlphaESSComputedSensorDescription`, `RegisterType` enum), dispatch encoding (`pack_dispatch_payload`), runtime parameter keys (`PARAM_*`), and re-exports sensor tuples from `sensor_registry.py`.
- **`sensor_registry.py`** — ~2500-line static registry of all Modbus sensor definitions. Replaces runtime YAML parsing. Each entry is an `AlphaESSModbusSensorDescription` with address, scale, offset, precision, poll tier.
- **`entity_definitions.py`** — Centralized definitions for all non-sensor platforms (numbers, selects, switches, time pickers, buttons). Platform files consume these typed dataclasses. All helper/control entities default to `EntityCategory.CONFIG`.
- **`entity.py`** — `AlphaESSBaseEntity` base class (40 lines). All entities inherit from this; provides `device_info` (enriched with serial number and EMS firmware version from coordinator data) and `unique_id = f"{entry_id}_{key}"`.
- **`services.py`** — HA service handlers for dispatch, force charge/discharge/export, period writes, datetime sync. Uses `pack_dispatch_payload()` from `const.py`. Services are cleaned up when the last config entry is unloaded.
- **`diagnostics.py`** — HA diagnostics platform. Dumps config entry data/options (host redacted), coordinator state, and runtime params for debug sharing.

## Key Patterns

- **Two kinds of entities:** "Write" entities read from coordinator + write to Modbus registers. "Local" entities store values in `runtime.params` dict (in-memory only, used by dispatch switches at activation time).
- **Dispatch switches are mutually exclusive:** `switch.py` implements a group pattern where turning on one dispatch switch turns off all others and writes a 9-register payload via `pack_dispatch_payload()`.
- **Sensor keys are the universal identifier:** The `key` field in sensor descriptions maps 1:1 to coordinator data dict keys, entity unique IDs, and B3 correction lookups. When adding a sensor, the key must be consistent across `sensor_registry.py`, `coordinator.py` derived calculations, and any platform that references it.
- **Config merging:** `hub._cfg()` merges `entry.options` over `entry.data`, so options flow overrides always take precedence.
- **Model-specific behavior:** SMILE-B3/B3-PLUS models get `B3_POWER_SCALE_CORRECTION` (0.1×) applied to 12 power keys. This is handled transparently in the coordinator.
- **Entity categories:** All helper/control entities (numbers, selects, switches, time pickers, buttons) use `EntityCategory.CONFIG`. Diagnostic sensors use `EntityCategory.DIAGNOSTIC`. Only measurement sensors have no category.
- **Service descriptions live in `strings.json`:** Service names, descriptions, and field labels are defined in the `"services"` key of `strings.json` (HA 2023.8+ convention). `services.yaml` contains only schemas and selectors.
- **Config entry selector for services:** All services that accept `entry_id` use the `config_entry` selector (integration-filtered dropdown) instead of a plain text field.
- **Reconfigure flow:** Users can change host/port/model/poll_freq via the reconfigure step without removing and re-adding the entry.

## Adding a New Modbus Sensor

1. Add a `REG_*` constant in `const.py` with the hex register address.
2. Append an `AlphaESSModbusSensorDescription(...)` entry to `CORE_SENSOR_DEFINITIONS` in `sensor_registry.py`. Set `slow_poll=True` for diagnostic registers.
3. If the sensor needs B3 scaling, add its key to `B3_POWER_KEYS` in `const.py`.
4. If it's a fast-poll power sensor, add its key to `FAST_POLL_1S_KEYS` in `const.py`.
5. For computed/derived sensors, add the calculation in `coordinator.py::_compute_derived()` and a matching `AlphaESSComputedSensorDescription` in `const.py` (see `KW_SENSOR_DESCRIPTIONS`).

## Adding a New Helper Entity (Number/Select/Switch)

Define a typed dataclass instance in `entity_definitions.py` (e.g., `WriteNumberDefinition`, `DispatchSwitchDefinition`), then append it to the appropriate `*_DEFINITIONS` tuple. The platform file will pick it up automatically. All helper definitions default `entity_category=EntityCategory.CONFIG`.

## File Reference

| File | Purpose |
|---|---|
| `const.py` | All constants, register addresses, dataclasses, dispatch encoding |
| `sensor_registry.py` | Static sensor definitions (~140 Modbus registers) |
| `entity_definitions.py` | Non-sensor entity definitions (numbers, selects, switches, times, buttons) |
| `coordinator.py` | Polling orchestration + `_compute_derived()` for template sensors |
| `hub.py` | Modbus TCP connection and read/write primitives |
| `config_flow.py` | UI setup flow + options flow + reconfigure flow with serial number auto-detection |
| `diagnostics.py` | HA diagnostics platform for debug data export |
| `services.yaml` | Service schema/selector definitions |
| `strings.json` / `translations/en.json` | UI strings for config flow, options, and service descriptions |
| `manifest.json` | HACS/HA metadata (domain, version, dependencies, pymodbus requirement) |
