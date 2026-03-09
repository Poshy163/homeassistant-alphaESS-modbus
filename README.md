# homeassistant-alphaESS-modbus

![Project Stage](https://img.shields.io/badge/project%20stage-in%20production-green.svg?style=for-the-badge)
![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)

AlphaESS inverter integration for Home Assistant via Modbus TCP, packaged for HACS.

## Start here

- Install via HACS, then add the integration from **Settings -> Devices & Services**.
- This integration now uses an internal static Python entity registry and does not require external package YAML files.
- If you migrated from legacy package-based setups, remove old `integration_alpha_ess.yaml` package includes from Home Assistant config.

## Features

- UI-based setup with config flow and options flow
- 140+ Modbus-backed sensor entities plus computed entities
- Number/select/switch/button/time helper entities for dispatch and schedule control
- Configurable polling profile (`slow`/`medium`/`fast`) for RS485 and TCP users
- Automatic slower diagnostic polling cadence based on selected polling profile
- Built-in SMILE-B3/B3-PLUS normalization for 12 legacy power sensors
- Local services for dispatch, reset, date/time sync, and period writes
- Optional package extras for utility-meter and legacy dashboard compatibility entities

## Install (HACS)

1. Open HACS in Home Assistant.
2. Go to **HACS -> Integrations -> ⋮ -> Custom repositories**.
3. Add repository URL:
   `https://github.com/Poshy163/homeassistant-alphaESS-modbus`
4. Select type **Integration** and install **AlphaESS Modbus**.
5. Restart Home Assistant.
6. Add integration from **Settings -> Devices & Services**.

## Manual Update From GitHub Release Zip

1. Open the latest GitHub release for this repository.
2. Download the asset named `alphaess_modbus-<tag>.zip`.
3. Extract the zip and copy the extracted `alphaess_modbus` folder into `config/custom_components/`.
4. Replace the existing `config/custom_components/alphaess_modbus` folder when prompted.
5. Restart Home Assistant to load the updated integration.

## Migration Notes

If you used package-era setups from `projects.hillviewlodge.ie`:

1. Remove any Home Assistant include referencing `integration_alpha_ess.yaml`.
2. Remove any local legacy AlphaESS package files that defined duplicate entities/automations.
3. Keep using this integration's entities/services directly in your own automations.

### Entity ID Migration Table

Custom components cannot create `input_*` helpers — those are Home Assistant core
user-managed helpers, not integration entity platforms. The integration replaces them
with native entity platforms. The object ID (slug after the domain) stays the same;
only the domain prefix changes.

**Find-and-replace rule**: replace `input_boolean.` → `switch.`, `input_number.` → `number.`,
`input_select.` → `select.`, `input_datetime.` → `time.`, `input_button.` → `button.` for
all `alphaess_*` entity IDs.

#### Switches (`input_boolean` → `switch`)

| Old Entity ID | New Entity ID |
|---|---|
| `input_boolean.alphaess_helper_force_charging` | `switch.alphaess_helper_force_charging` |
| `input_boolean.alphaess_helper_force_discharging` | `switch.alphaess_helper_force_discharging` |
| `input_boolean.alphaess_helper_force_export` | `switch.alphaess_helper_force_export` |
| `input_boolean.alphaess_helper_dispatch` | `switch.alphaess_helper_dispatch` |
| `input_boolean.alphaess_helper_excess_export` | `switch.alphaess_helper_excess_export` |
| `input_boolean.alphaess_helper_excess_export_pause` | `switch.alphaess_helper_excess_export_pause` |

#### Numbers (`input_number` → `number`)

| Old Entity ID | New Entity ID |
|---|---|
| `input_number.alphaess_helper_charging_cutoff_soc` | `number.alphaess_helper_charging_cutoff_soc` |
| `input_number.alphaess_helper_discharging_cutoff_soc` | `number.alphaess_helper_discharging_cutoff_soc` |
| `input_number.alphaess_helper_max_feed_to_grid` | `number.alphaess_helper_max_feed_to_grid` |
| `input_number.alphaess_template_force_charging_power` | `number.alphaess_template_force_charging_power` |
| `input_number.alphaess_helper_force_charging_duration` | `number.alphaess_helper_force_charging_duration` |
| `input_number.alphaess_helper_force_charging_cutoff_soc` | `number.alphaess_helper_force_charging_cutoff_soc` |
| `input_number.alphaess_template_force_discharging_power` | `number.alphaess_template_force_discharging_power` |
| `input_number.alphaess_helper_force_discharging_duration` | `number.alphaess_helper_force_discharging_duration` |
| `input_number.alphaess_helper_force_discharging_cutoff_soc` | `number.alphaess_helper_force_discharging_cutoff_soc` |
| `input_number.alphaess_template_force_export_power` | `number.alphaess_template_force_export_power` |
| `input_number.alphaess_helper_force_export_duration` | `number.alphaess_helper_force_export_duration` |
| `input_number.alphaess_helper_force_export_cutoff_soc` | `number.alphaess_helper_force_export_cutoff_soc` |
| `input_number.alphaess_template_dispatch_power` | `number.alphaess_template_dispatch_power` |
| `input_number.alphaess_helper_dispatch_duration` | `number.alphaess_helper_dispatch_duration` |
| `input_number.alphaess_helper_dispatch_cutoff_soc` | `number.alphaess_helper_dispatch_cutoff_soc` |

#### Selects (`input_select` → `select`)

| Old Entity ID | New Entity ID |
|---|---|
| `input_select.alphaess_helper_charging_discharging_settings` | `select.alphaess_helper_charging_discharging_settings` |
| `input_select.alphaess_helper_dispatch_mode` | `select.alphaess_helper_dispatch_mode` |
| `input_select.alphaess_helper_inverter_ac_limit` | `select.alphaess_helper_inverter_ac_limit` |

#### Time Pickers (`input_datetime` → `time`)

| Old Entity ID | New Entity ID |
|---|---|
| `input_datetime.alphaess_helper_charging_period_1_start` | `time.alphaess_helper_charging_period_1_start` |
| `input_datetime.alphaess_helper_charging_period_1_stop` | `time.alphaess_helper_charging_period_1_stop` |
| `input_datetime.alphaess_helper_charging_period_2_start` | `time.alphaess_helper_charging_period_2_start` |
| `input_datetime.alphaess_helper_charging_period_2_stop` | `time.alphaess_helper_charging_period_2_stop` |
| `input_datetime.alphaess_helper_discharging_period_1_start` | `time.alphaess_helper_discharging_period_1_start` |
| `input_datetime.alphaess_helper_discharging_period_1_stop` | `time.alphaess_helper_discharging_period_1_stop` |
| `input_datetime.alphaess_helper_discharging_period_2_start` | `time.alphaess_helper_discharging_period_2_start` |
| `input_datetime.alphaess_helper_discharging_period_2_stop` | `time.alphaess_helper_discharging_period_2_stop` |

#### Buttons (`input_button` → `button`)

| Old Entity ID | New Entity ID |
|---|---|
| `input_button.alphaess_helper_dispatch_reset` | `button.alphaess_helper_dispatch_reset` |
| `input_button.alphaess_helper_dispatch_reset_full` | `button.alphaess_helper_dispatch_reset_full` |
| `input_button.alphaess_helper_synchronise_date_time` | `button.alphaess_helper_synchronise_date_time` |

#### Timers (`timer` → `sensor`)

Package-era `timer.*` entities have no direct counterpart domain in custom
components. The integration now provides dispatch time-remaining sensors instead:

| Old Entity ID | New Entity ID |
|---|---|
| `timer.alphaess_force_charging` | `sensor.alphaess_force_charging_time_remaining` |
| `timer.alphaess_force_discharging` | `sensor.alphaess_force_discharging_time_remaining` |
| `timer.alphaess_force_export` | `sensor.alphaess_force_export_time_remaining` |
| `timer.alphaess_dispatch` | `sensor.alphaess_dispatch_time_remaining` |
| `timer.alphaess_excess_export` | `sensor.alphaess_excess_export_time_remaining` |

These sensors show remaining time in minutes (0 when idle) and update each
polling cycle. Timer state is in-memory; it resets if Home Assistant restarts
while a dispatch is active.

If your dashboard still references old package-era `today_s_*` sensors, include
`custom_components/alphaess_modbus/packages_extras.yaml` in Home Assistant packages.
It now provides legacy
compatibility aliases with the same entity IDs, including:

- `sensor.alphaess_total_energy_from_pv_meter`
- `sensor.alphaess_today_s_energy_from_pv`
- `sensor.alphaess_today_s_energy_consumption_from_grid_meter`
- `sensor.alphaess_today_s_energy_feed_to_grid_meter`
- `sensor.alphaess_today_s_energy_charge_battery`
- `sensor.alphaess_today_s_energy_discharge_battery`
- `sensor.alphaess_today_s_energy_from_pv_meter`
- `sensor.alphaess_today_s_house_load`

Example `configuration.yaml` snippet:

```yaml
homeassistant:
   packages:
      alphaess_extras: !include custom_components/alphaess_modbus/packages_extras.yaml
```

## Dashboard YAML

One ready-to-use dashboard file is included:

- `alphaess_view.yaml`: full dashboard config (contains `title` + `views`)

Paste it into the dashboard-level raw config editor.

Both files are already aligned to integration-native entities (`switch`/`number`/`select`/`time`/`button`) and do not require legacy `input_*` helpers.

## Notes

## Reduce Logbook Spam (Optional)

If your Logbook is noisy from frequent state changes, add this to your
`configuration.yaml`:

```yaml
logbook:
   exclude:
      entities:
         - sensor.alphaess_system_time
         - automation.alphaess_excess_export
```

## Credits

- Axel Koegler (SaaX-IRL) for original AlphaESS Modbus register research and documentation.
