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

If you still have older dashboards with `input_*` entity IDs, replace them with
native domains (`switch`/`number`/`select`/`time`/`button`) or use the
included dashboard file above.

Legacy package-era timer entities (`timer.alphaess_*`) are not part of the
integration-native model.

## Credits

- Axel Koegler (SaaX-IRL) for original AlphaESS Modbus register research and documentation.
