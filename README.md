# homeassistant-alphaESS-modbus

![Project Stage](https://img.shields.io/badge/project%20stage-in%20production-green.svg?style=for-the-badge)
![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)

AlphaESS inverter integration for Home Assistant via Modbus TCP, packaged for HACS.

## Start here

- **New users:** follow [Install (HACS)](#install-hacs), then [Modern automations package (recommended)](#modern-automations-package-recommended), then [Dashboard](#dashboard).
- **Existing Axel package users:** go to [Migration from projects.hillviewlodge.ie](#migration-from-projectshillviewlodgeie).
- **Advanced/technical details:** see [Architecture — YAML-driven register map](#architecture--yaml-driven-register-map).

## Features

- **UI-based setup** — Config flow and options flow (no YAML required)
- **120+ entities** across sensor, number, select, switch, button, and time platforms
- **9 kW sensors** — derived kilowatt versions of key power readings (house load, PV, grid, battery, PV1, PV2, excess) for easier dashboard use
- **DataUpdateCoordinator** with 5-second polling; grid-safety registers on a slower 60-second cycle
- **Dispatch control** — force charge / discharge / export with power, duration, and cutoff SoC
- **Charging & discharging period time pickers** — native `TimeEntity` for period start/stop times
- **Grid safety registers** — over/under-voltage & frequency protections with trip times
- **Inverter diagnostics** — firmware versions (ASCII string registers), warnings, faults, network info
- **Custom Lovelace cards** — auto-loaded, no manual resource registration required:
  - **Power Flow card** — animated SVG visualisation of solar, grid, battery and home power flows
  - **9 Entity cards** — grouped entity lists (Overview, Charging, Solar, Battery, Grid, Dispatch, Grid Safety, Warnings & Faults, System) matching the native HA look
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

## Modern automations package (recommended)

To get **visible and working** AlphaESS automations without legacy
`modbus.write_register` actions, use the generated modern package:

- [`custom_components/alphaess_modbus/automations_modern.yaml`](custom_components/alphaess_modbus/automations_modern.yaml)

This package uses only integration services from
`alphaess_modbus` (for example `force_charge`, `dispatch`,
`dispatch_reset`, `sync_datetime`, `set_charging_periods`,
`set_discharging_periods`).

In plain terms:
- **New way (recommended):** automations call `alphaess_modbus.*` services provided by this integration.
- **Old way (legacy package):** automations call raw `modbus.write_register` actions directly.

Because this package uses the new way only, it does not depend on the old
package action wiring and avoids those legacy unknown-action repair warnings.

### Home Assistant setup

1. Include it directly in `configuration.yaml`:

    ```yaml
    homeassistant:
       packages:
      alphaess_automations_modern: !include custom_components/alphaess_modbus/automations_modern.yaml
    ```

2. Restart Home Assistant.
3. Open **Settings → Automations & scenes** and search for `AlphaESS`.

### Important

- Do **not** include `custom_components/alphaess_modbus/integration_alpha_ess.yaml`
   as an HA package in modern setups; it contains legacy automations with
   direct `modbus.write_register` actions.
- If you still have `/config/packages/integration_alpha_ess.yaml` from older
   setups, you can safely remove it after migration.

### Auto-generation in GitHub

When `.github/workflows/sync-yaml.yml` detects and syncs a new upstream
`integration_alpha_ess.yaml`, it now also regenerates
`custom_components/alphaess_modbus/automations_modern.yaml`
automatically before opening the PR.

## Migration from projects.hillviewlodge.ie

If you currently run Axel's package-based setup from
https://projects.hillviewlodge.ie/alphaess/, use this migration path.

### 1) Remove legacy package includes

From your Home Assistant `configuration.yaml`, remove/disable includes that load
the legacy full package (for example `integration_alpha_ess.yaml` from
`/config/packages`).

After migrating, you can delete `/config/packages/integration_alpha_ess.yaml`.
It is no longer used by this integration and keeping it typically causes
duplicate/legacy automations.

You can also remove old AlphaESS-related entries from `secrets.yaml` that were
only used by the legacy package configuration.

Why: that legacy package contains direct `modbus.write_register` actions and can
cause **Spook unknown action/entity** warnings in modern setups.

### 2) Install this integration via HACS

Follow the HACS install steps above and configure the integration from
**Settings → Devices & Services**.

### 3) Keep your dashboards, then update gradually

- You can keep existing dashboard YAML while migrating.
- This repo includes [`alphaess_view.yaml`](alphaess_view.yaml) and custom cards
   if you want to switch to the maintained dashboard layout later.

### 4) Use the modern automations package (optional but recommended)

If you want packaged automations in HA (visible in **Automations & scenes**),
include:

```yaml
homeassistant:
   packages:
      alphaess_automations_modern: !include custom_components/alphaess_modbus/automations_modern.yaml
```

This package is shipped with the integration and uses integration services
(`alphaess_modbus.*`) instead of legacy direct Modbus write actions.

### 5) Restart and clean duplicates

After restart:

- Search automations for `AlphaESS`.
- Remove/disable duplicate legacy entries (often shown with `_2` suffix).
- If Spook still reports unknown legacy entities/actions, a legacy package include
   is still active somewhere.

### 6) Keep updates simple

- HACS updates this integration and its bundled files (including
   [`custom_components/alphaess_modbus/automations_modern.yaml`](custom_components/alphaess_modbus/automations_modern.yaml)).
- The workflow in
   [`.github/workflows/sync-yaml.yml`](.github/workflows/sync-yaml.yml)
   auto-syncs upstream YAML and regenerates the modern automations package for PRs.

### Quick post-migration checklist

- [ ] Legacy package include removed from `configuration.yaml`
- [ ] `/config/packages/integration_alpha_ess.yaml` deleted
- [ ] Legacy AlphaESS `secrets.yaml` entries removed (if no longer used)
- [ ] `custom_components/alphaess_modbus/automations_modern.yaml` included
- [ ] Home Assistant restarted
- [ ] No duplicate `AlphaESS` automations (for example `_2` suffix)
- [ ] No `modbus.write_register` unknown-action repairs

## Reference (details)

## Connection

- **Modbus TCP** — IP address + port (default 502)

## Entity overview

| Platform | Count | Examples |
|---|---|---|
| Sensor | 90+ | PV power, grid power, battery SoC/SoH, energy totals, dispatch status, grid safety, firmware versions, warnings & faults, kW variants |
| Number | 15 | Charging/discharging cutoff SoC, force charge/discharge/export power & duration & cutoff, dispatch power & duration & cutoff, max feed to grid |
| Select | 3 | Charging/discharging settings, dispatch mode, inverter AC limit |
| Switch | 6 | Force charging, force discharging, force export, dispatch, excess export, excess export pause |
| Button | 3 | Dispatch reset, dispatch reset full, synchronise date & time |
| Time | 8 | Charging/discharging period 1 & 2 start/stop times |

### kW sensors

Nine derived sensor entities convert raw watt readings to kilowatts for
cleaner dashboard displays and automations:

| Entity | Source |
|---|---|
| `sensor.alphaess_current_house_load_kw` | House load |
| `sensor.alphaess_current_pv_production_kw` | PV production |
| `sensor.alphaess_power_grid_consumption_kw` | Grid consumption |
| `sensor.alphaess_power_grid_feed_in_kw` | Grid feed-in |
| `sensor.alphaess_power_grid_kw` | Grid power (signed) |
| `sensor.alphaess_power_battery_kw` | Battery power (signed) |
| `sensor.alphaess_pv1_power_kw` | PV string 1 |
| `sensor.alphaess_pv2_power_kw` | PV string 2 |
| `sensor.alphaess_excess_power_kw` | Excess / surplus power |

## Architecture — YAML-driven register map

This integration's sensor definitions are **not hardcoded in Python**. Instead
they are loaded at startup from
[`integration_alpha_ess.yaml`](custom_components/alphaess_modbus/integration_alpha_ess.yaml)
— the native Home Assistant packages file maintained by
[Axel Koegler](https://github.com/SaaX-IRL).

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
        ├─ COMPUTED_SENSOR_DESCRIPTIONS       → sensor.py (entity creation)
        └─ KW_SENSOR_DESCRIPTIONS             → sensor.py (9 kW entities)
        │
        ▼
  coordinator.py                    (DataUpdateCoordinator)
        │
        ├─ _async_update_data()     polls every register via Modbus TCP
        └─ _compute_derived()       calculates 17 virtual sensors + 9 kW:
                                      PV production, house load, excess power,
                                      clipping, charge/discharge periods,
                                      IP/subnet/gateway normalised,
                                      BMS/EMS version strings,
                                      system date/time, battery full,
                                      kW variants of key power readings
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
| `const.py` | Constants, dataclasses (`AlphaESSModbusSensorDescription`, `RegisterType`), lazy-loading wrappers, kW sensor descriptions |
| `coordinator.py` | `DataUpdateCoordinator` — polls registers, computes derived values and kW conversions |
| `sensor.py` | Creates `AlphaESSModbusSensor` and `AlphaESSComputedSensor` entities (including kW sensors) |
| `hub.py` | `AsyncModbusTcpClient` wrapper for TCP communication |
| `www/alphaess-card.js` | Custom Lovelace power flow card (auto-loaded) |
| `www/alphaess-entities-cards.js` | 9 custom Lovelace entity cards (auto-loaded) |
| `packages_extras.yaml` | Optional daily utility meters and W → kW template sensors (copy to your HA config) |

## Dashboard

### Custom cards

The integration ships **10 custom Lovelace cards** that appear automatically in
the **Add card** picker after installation — no extra HACS frontend downloads,
resource registration, or YAML editing required.

The JS files are bundled inside the integration and served via Home Assistant's
static path system. The `frontend` and `http` components are declared as
dependencies in `manifest.json` to guarantee the serving infrastructure is
ready before card registration.

#### Power Flow card

**Card type:** `custom:alphaess-power-flow-card`

A real-time animated SVG card showing power flow between Solar, Grid, Home
and Battery.

**To add it:**

1. Open any dashboard and click **Edit → Add card**.
2. Search for **AlphaESS Power Flow**.
3. The card is pre-configured with default entity IDs. Adjust if needed via the
   visual editor.

**What it shows:**

- Real-time animated power flow between **Solar**, **Grid**, **Home** and
  **Battery**
- Direction-aware flowing dots (import vs export, charge vs discharge)
- Battery state-of-charge bar with colour coding
- All values update live with the integration's 5-second polling

**Configuration options** (all optional — defaults match the integration's
entity IDs):

| Option | Default | Description |
|---|---|---|
| `title` | AlphaESS Power Flow | Card header text |
| `solar_entity` | `sensor.alphaess_current_pv_production` | Solar production (W) |
| `grid_entity` | `sensor.alphaess_power_grid` | Grid power (W, positive = import) |
| `battery_entity` | `sensor.alphaess_power_battery` | Battery power (W, positive = discharge) |
| `battery_soc_entity` | `sensor.alphaess_soc_battery` | Battery state of charge (%) |
| `house_entity` | `sensor.alphaess_current_house_load` | House load (W) |
| `unit` | auto | Display unit — `auto`, `W`, or `kW` |

#### Entity cards (×9)

Nine cards that group every entity in the integration by category, matching the
native HA entities card look (icon + name + value rows, clickable for
more-info).

| Card type | Name | Description |
|---|---|---|
| `custom:alphaess-overview-card` | AlphaESS Overview | Key metrics at a glance |
| `custom:alphaess-charging-card` | AlphaESS Charging | Charging & discharging config and controls |
| `custom:alphaess-solar-card` | AlphaESS Solar | PV production, string power, energy totals |
| `custom:alphaess-battery-card` | AlphaESS Battery | SoC, SoH, power, BMS info, temperatures |
| `custom:alphaess-grid-card` | AlphaESS Grid | Grid power, voltage, frequency, energy totals |
| `custom:alphaess-dispatch-card` | AlphaESS Dispatch | Dispatch mode, power, duration, status |
| `custom:alphaess-grid-safety-card` | AlphaESS Grid Safety | Over/under-voltage & frequency protections |
| `custom:alphaess-warnings-card` | AlphaESS Warnings & Faults | Active warning and fault codes |
| `custom:alphaess-system-card` | AlphaESS System | Firmware, network, date/time, diagnostics |

**To add any of them:**

1. Open any dashboard and click **Edit → Add card**.
2. Search for the card name (e.g. **AlphaESS Battery**).
3. Each card comes pre-configured with the correct entities. Optionally change
   the title via the visual editor.

### Dashboard view YAML

An example dashboard layout is provided in
[`alphaess_view.yaml`](alphaess_view.yaml). It contains a multi-view dashboard
with views for Home, Charging, Solar, Battery, Grid, Dispatch, Grid Safety,
Warnings & Faults, and System.

**To use it:**

1. Go to **Settings → Dashboards → Add Dashboard**.
2. Choose **New dashboard from scratch**.
3. Click the pencil icon (edit), then **⋮ → Raw configuration editor**.
4. Paste the contents of `alphaess_view.yaml` and save.

> **Note:** The Home view contains example personal entities (weather, motion
> sensors, etc.) that you'll want to customise for your own setup.

## Credits

- **[Axel Koegler](https://github.com/SaaX-IRL)** — original AlphaESS Modbus register research and the `integration_alpha_ess.yaml` packages file that this integration reads from.

## Notes

This integration replaces the standalone Modbus-YAML approach (based on Axel's original work) with a proper custom component featuring UI configuration, native entities, and services. The YAML file itself is still central — but instead of the user loading it as a HA package, this integration parses it internally and creates native entities with full device grouping, diagnostics, and service support.
