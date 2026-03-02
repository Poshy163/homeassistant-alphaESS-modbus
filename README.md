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


## Dashboard

An example Lovelace view is provided in `alphaess_view.yaml`. Import it via **Settings → Dashboards → ⋮ → Edit → Raw configuration editor**.

## Notes

This integration replaces the standalone Modbus-YAML approach (based on Axel's original work) with a proper custom component featuring UI configuration, native entities, and services.
