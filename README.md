# homeassistant-alphaESS-modbus

![Project Stage](https://img.shields.io/badge/project%20stage-in%20production-green.svg?style=for-the-badge)
![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)

AlphaESS inverter integration for Home Assistant via Modbus TCP, packaged for HACS.

## Features

- **UI-based setup** — Config flow and options flow (no YAML required)
- **120+ entities** across sensor, number, select, switch, button, and time platforms
- **DataUpdateCoordinator** with 5-second polling; grid-safety registers on a slower 60-second cycle
- **Dispatch control** — force charge / discharge / export with power, duration, and cutoff SoC
- **Charging & discharging period time pickers** — native `TimeEntity` for period start/stop times
- **Grid safety registers** — over/under-voltage & frequency protections with trip times
- **Inverter diagnostics** — firmware versions (ASCII string registers), warnings, faults, network info
- **Services** — `write_register`, `read_register`, `batch_read`

## Supported inverters

| Model | Notes |
|---|---|
| SMILE5 | |
| SMILE-G3-S3.6 | |
| SMILE-G3-B5 | |
| SMILE-G3-S5 | |
| SMILE-G3-T10 | |
| SMILE-Hi5 | |
| SMILE-Hi10 | |
| SMILE-B3 | |
| SMILE-B3-PLUS | |
| SMILE-S6-HV | |
| Other | Generic profile |

## Install (HACS)

1. Open HACS in Home Assistant.
2. Go to **HACS → Integrations → ⋮ (top-right menu) → Custom repositories**.
3. Enter the repository URL:
   ```
   https://github.com/Poshy163/homeassistant-alphaESS-modbus
   ```
   Select **Integration** as the type, then click **Add**.
4. Search for **AlphaESS Modbus** in HACS and click **Install**.
5. Restart Home Assistant.
6. Go to **Settings → Devices & Services → Add Integration** and search for **AlphaESS Modbus**.
7. Enter your inverter's IP address, port, slave ID, choose your inverter model, and submit.

## Connection

- **Modbus TCP** — IP address + port (default 502)

## Entity overview

| Platform | Count | Examples |
|---|---|---|
| Sensor | 90+ | PV power, grid power, battery SoC/SoH, energy totals, dispatch status, grid safety, firmware versions, warnings & faults |
| Number | 15 | Charging/discharging cutoff SoC, force charge/discharge/export power & duration & cutoff, dispatch power & duration & cutoff, max feed to grid |
| Select | 3 | Charging/discharging settings, dispatch mode, inverter AC limit |
| Switch | 6 | Force charging, force discharging, force export, dispatch, excess export, excess export pause |
| Button | 3 | Dispatch reset, dispatch reset full, synchronise date & time |
| Time | 8 | Charging/discharging period 1 & 2 start/stop times |


## Architecture — YAML-driven register map

This integration's sensor definitions are **not hardcoded in Python**. Instead
they are loaded at startup from
[`integration_alpha_ess.yaml`](custom_components/alphaess_modbus/integration_alpha_ess.yaml)
— the native Home Assistant packages file maintained by
[Axel Koegler](https://github.com/AxelKoegler).

### Why?

Axel's YAML already contains every Modbus register address, data type, unit,
device class, state class, scale, offset and scan interval for the AlphaESS
inverter family. Rather than duplicating all of that information in Python
constants (and having to keep both in sync), this integration treats Axel's
YAML as the **single source of truth** and parses it directly.

### How it works

```
integration_alpha_ess.yaml          (source of truth — never modified)
        │
        ▼
  yaml_loader.py                    (custom parser at startup)
        │
        ├─ modbus: sensors: [...]   → AlphaESSModbusSensorDescription (×141)
        │                              ↳ key, address, register_type, unit,
        │                                device_class, state_class, scale,
        │                                offset, precision, slow_poll, …
        │
        └─ template: sensor: [...]  → AlphaESSComputedSensorDescription (×17)
                                       ↳ key, unit, device_class, state_class
                                       (only those coordinator.py can compute)
        │
        ▼
  const.py                          (lazy-loading _LazyTuple wrappers)
        │
        ├─ CORE_SENSOR_DESCRIPTIONS           → sensor.py (entity creation)
        ├─ INTERNAL_REGISTER_DESCRIPTIONS     → coordinator.py (polling)
        └─ COMPUTED_SENSOR_DESCRIPTIONS       → sensor.py (entity creation)
        │
        ▼
  coordinator.py                    (DataUpdateCoordinator)
        │
        ├─ _async_update_data()     polls every register via Modbus TCP
        └─ _compute_derived()       calculates 17 virtual sensors:
                                      PV production, house load, excess power,
                                      clipping, charge/discharge periods,
                                      IP/subnet/gateway normalised,
                                      BMS/EMS version strings,
                                      system date/time, battery full
```

### Key design decisions

| Decision | Detail |
|---|---|
| **`integration_alpha_ess.yaml` is never modified** | The file is read-only to this integration. Axel updates it upstream; users drop the new version in and restart. |
| **Custom YAML loader** | A `SafeLoader` subclass (`_AlphaYAMLLoader`) silently handles `!secret` and `!include` tags so the file parses without a running HA instance. |
| **Name → key derivation** | Sensor names like `"AlphaESS Inverter Grid Frequency"` are converted to snake_case keys (`inverter_grid_frequency`) automatically. An override dict handles edge cases. |
| **Display name prefix stripping** | `"AlphaESS "` is stripped from entity names because `has_entity_name = True` already provides the device name as a prefix — avoiding doubled names like `sensor.alphaess_alphaess_…`. |
| **Lazy loading** | Sensor description tuples are wrapped in `_LazyTuple` objects that defer YAML parsing until first access, so `const.py` can be imported without side-effects. |
| **Slow-poll heuristic** | Registers with `scan_interval ≥ 30` in the YAML are flagged `slow_poll = True` and only read every 12th coordinator cycle (~60 s at the default 5 s interval). |
| **Diagnostic heuristic** | Grid-safety registers (address range `0x1000–0x1024`) and version/network-info sensors are automatically marked as diagnostic entities. |

### Adding a new sensor

1. Ask Axel to add the register to `integration_alpha_ess.yaml`, or add it
   yourself under `modbus: → sensors:` following the existing format.
2. Restart Home Assistant. The new sensor appears automatically — **no Python
   changes needed**.
3. If the new sensor requires a _computed/derived_ value (combining multiple
   raw registers), add the calculation to `coordinator.py →
   _compute_derived()` and the key to `_COMPUTED_KEYS` in `yaml_loader.py`.

### Files at a glance

| File | Purpose |
|---|---|
| `integration_alpha_ess.yaml` | Axel's HA packages YAML — the register map source of truth (141 Modbus sensors, 29 template sensors, automations, input helpers, utility meters) |
| `yaml_loader.py` | Parses the YAML into dataclass descriptions at startup |
| `const.py` | Constants, dataclasses (`AlphaESSModbusSensorDescription`, `RegisterType`), lazy-loading wrappers |
| `coordinator.py` | `DataUpdateCoordinator` — polls registers, computes derived values |
| `sensor.py` | Creates `AlphaESSModbusSensor` and `AlphaESSComputedSensor` entities |
| `hub.py` | `AsyncModbusTcpClient` wrapper for TCP communication |
| `packages_extras.yaml` | Optional daily utility meters and W → kW template sensors (copy to your HA config) |

## Dashboard

An example Lovelace view is provided in `alphaess_view.yaml`. Import it via **Settings → Dashboards → ⋮ → Edit → Raw configuration editor**.

## Credits

- **[Axel Koegler](https://github.com/AxelKoegler)** — original AlphaESS Modbus register research and the `integration_alpha_ess.yaml` packages file that this integration reads from.

## Notes

This integration replaces the standalone Modbus-YAML approach (based on Axel's original work) with a proper custom component featuring UI configuration, native entities, and services. The YAML file itself is still central — but instead of the user loading it as a HA package, this integration parses it internally and creates native entities with full device grouping, diagnostics, and service support.
