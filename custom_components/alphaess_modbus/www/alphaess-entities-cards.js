/**
 * AlphaESS Entity Cards v1.0.0
 *
 * Nine custom Lovelace cards for Home Assistant that display AlphaESS
 * inverter entities grouped by category (Battery, Solar, Grid, etc.).
 *
 * Each card appears in the "Add card" picker.
 * Clicking any entity row opens the native more-info dialog.
 * No external dependencies — pure HTML / CSS.
 */

console.debug(
    "[alphaess-entities-cards] Loading AlphaESS entity cards module…",
);

const ENTITIES_CARDS_VERSION = "1.0.0";

/* ─── icon fallback by domain ──────────────────────────────────────────── */
const DOMAIN_ICONS = {
    sensor: "mdi:eye",
    binary_sensor: "mdi:checkbox-blank-circle-outline",
    switch: "mdi:toggle-switch-outline",
    number: "mdi:ray-vertex",
    select: "mdi:format-list-bulleted",
    button: "mdi:gesture-tap-button",
    time: "mdi:clock-outline",
};

function getEntityIcon(hass, entityId) {
    const st = hass?.states?.[entityId];
    if (st?.attributes?.icon) return st.attributes.icon;
    const domain = entityId.split(".")[0];
    return DOMAIN_ICONS[domain] || "mdi:eye";
}

function getEntityState(hass, entityId) {
    const st = hass?.states?.[entityId];
    if (!st) return "—";
    const s = st.state;
    if (s === "unavailable" || s === "unknown") return "—";
    const unit = st.attributes?.unit_of_measurement;
    return unit ? `${s} ${unit}` : s;
}

/* ═══════════════════════════════════════════════════════════════════════ *
 *  CARD PRESETS — one entry per card type                                *
 * ═══════════════════════════════════════════════════════════════════════ */

const CARD_PRESETS = {
    /* ── 1. Overview ───────────────────────────────────────────────────── */
    overview: {
        title: "AlphaESS Overview",
        cardName: "AlphaESS Overview",
        description:
            "Key AlphaESS metrics at a glance — production, consumption, grid and battery.",
        entities: [
            {
                entity: "sensor.alphaess_current_pv_production",
                name: "PV Production",
            },
            {
                entity: "sensor.alphaess_current_house_load",
                name: "House Load",
            },
            { entity: "sensor.alphaess_power_grid", name: "Grid Power" },
            { entity: "sensor.alphaess_power_battery", name: "Battery Power" },
            { entity: "sensor.alphaess_soc_battery", name: "Battery SoC" },
            { entity: "sensor.alphaess_excess_power", name: "Excess Power" },
            { section: "Totals" },
            {
                entity: "sensor.alphaess_total_energy_from_pv",
                name: "Total Energy from PV",
            },
            {
                entity: "sensor.alphaess_total_house_load",
                name: "Total House Load",
            },
            {
                entity: "sensor.alphaess_total_energy_consumption_from_grid_meter",
                name: "Total Grid Consumption",
            },
            {
                entity: "sensor.alphaess_total_energy_feed_to_grid_meter",
                name: "Total Grid Feed-in",
            },
        ],
    },

    /* ── 2. Charging ───────────────────────────────────────────────────── */
    charging: {
        title: "AlphaESS Charging",
        cardName: "AlphaESS Charging",
        description:
            "Charging and discharging configuration, force charge/discharge/export controls, and time periods.",
        entities: [
            {
                entity: "select.alphaess_helper_inverter_ac_limit",
                name: "Inverter AC Limit",
            },
            {
                entity: "sensor.alphaess_charging_time_period_control",
                name: "Charging Time Period Control",
            },
            {
                entity: "number.alphaess_helper_charging_cutoff_soc",
                name: "Charging Cutoff SoC",
            },
            {
                entity: "sensor.alphaess_charging_cutoff_soc",
                name: "Charging Cutoff SoC",
            },
            {
                entity: "number.alphaess_helper_discharging_cutoff_soc",
                name: "Discharging Cutoff SoC",
            },
            {
                entity: "sensor.alphaess_discharging_cutoff_soc",
                name: "Discharging Cutoff SoC",
            },
            { section: "Periods" },
            {
                entity: "sensor.alphaess_charging_period_1",
                name: "Charging Period 1",
            },
            {
                entity: "sensor.alphaess_charging_period_2",
                name: "Charging Period 2",
            },
            {
                entity: "sensor.alphaess_discharging_period_1",
                name: "Discharging Period 1",
            },
            {
                entity: "sensor.alphaess_discharging_period_2",
                name: "Discharging Period 2",
            },
            { section: "Force Charging" },
            {
                entity: "switch.alphaess_helper_force_charging",
                name: "Force Charging",
            },
            {
                entity: "number.alphaess_helper_force_charging_duration",
                name: "Duration",
            },
            {
                entity: "number.alphaess_template_force_charging_power",
                name: "Power",
            },
            {
                entity: "number.alphaess_helper_force_charging_cutoff_soc",
                name: "Cutoff SoC",
            },
            { section: "Force Discharging" },
            {
                entity: "switch.alphaess_helper_force_discharging",
                name: "Force Discharging",
            },
            {
                entity: "number.alphaess_helper_force_discharging_duration",
                name: "Duration",
            },
            {
                entity: "number.alphaess_template_force_discharging_power",
                name: "Power",
            },
            {
                entity: "number.alphaess_helper_force_discharging_cutoff_soc",
                name: "Cutoff SoC",
            },
            { section: "Force Export" },
            {
                entity: "switch.alphaess_helper_force_export",
                name: "Force Export",
            },
            {
                entity: "number.alphaess_helper_force_export_duration",
                name: "Duration",
            },
            {
                entity: "number.alphaess_template_force_export_power",
                name: "Power",
            },
            {
                entity: "number.alphaess_helper_force_export_cutoff_soc",
                name: "Cutoff SoC",
            },
            { section: "Settings" },
            {
                entity: "select.alphaess_helper_charging_discharging_settings",
                name: "Charging / Discharging Settings",
            },
            { section: "Charging Time Settings" },
            {
                entity: "time.alphaess_helper_charging_period_1_start",
                name: "Charging Period 1 Start",
            },
            {
                entity: "time.alphaess_helper_charging_period_1_stop",
                name: "Charging Period 1 Stop",
            },
            {
                entity: "time.alphaess_helper_charging_period_2_start",
                name: "Charging Period 2 Start",
            },
            {
                entity: "time.alphaess_helper_charging_period_2_stop",
                name: "Charging Period 2 Stop",
            },
            { section: "Discharging Time Settings" },
            {
                entity: "time.alphaess_helper_discharging_period_1_start",
                name: "Discharging Period 1 Start",
            },
            {
                entity: "time.alphaess_helper_discharging_period_1_stop",
                name: "Discharging Period 1 Stop",
            },
            {
                entity: "time.alphaess_helper_discharging_period_2_start",
                name: "Discharging Period 2 Start",
            },
            {
                entity: "time.alphaess_helper_discharging_period_2_stop",
                name: "Discharging Period 2 Stop",
            },
        ],
    },

    /* ── 3. Solar ──────────────────────────────────────────────────────── */
    solar: {
        title: "AlphaESS Solar",
        cardName: "AlphaESS Solar",
        description:
            "PV string output (power, voltage, current), clipping, and solar totals.",
        entities: [
            {
                entity: "sensor.alphaess_current_pv_production",
                name: "Current PV Production",
            },
            { section: "PV1" },
            { entity: "sensor.alphaess_pv1_power", name: "PV1 Power" },
            { entity: "sensor.alphaess_pv1_voltage", name: "PV1 Voltage" },
            { entity: "sensor.alphaess_pv1_current", name: "PV1 Current" },
            { section: "PV2" },
            { entity: "sensor.alphaess_pv2_power", name: "PV2 Power" },
            { entity: "sensor.alphaess_pv2_voltage", name: "PV2 Voltage" },
            { entity: "sensor.alphaess_pv2_current", name: "PV2 Current" },
            { section: "PV3" },
            { entity: "sensor.alphaess_pv3_power", name: "PV3 Power" },
            { entity: "sensor.alphaess_pv3_voltage", name: "PV3 Voltage" },
            { entity: "sensor.alphaess_pv3_current", name: "PV3 Current" },
            { section: "PV4" },
            { entity: "sensor.alphaess_pv4_power", name: "PV4 Power" },
            { entity: "sensor.alphaess_pv4_voltage", name: "PV4 Voltage" },
            { entity: "sensor.alphaess_pv4_current", name: "PV4 Current" },
            { section: true },
            {
                entity: "sensor.alphaess_active_power_pv_meter",
                name: "Active Power PV (Meter)",
            },
            { entity: "sensor.alphaess_clipping", name: "Clipping" },
            { section: "Totals & Capacity" },
            {
                entity: "sensor.alphaess_pv_capacity_storage",
                name: "PV Capacity Storage",
            },
            {
                entity: "sensor.alphaess_pv_capacity_of_grid_inverter",
                name: "PV Capacity of Grid Inverter",
            },
            {
                entity: "sensor.alphaess_ct_rate_pv_meter",
                name: "CT Rate PV (Meter)",
            },
            {
                entity: "sensor.alphaess_total_energy_from_pv",
                name: "Total Energy from PV",
            },
            {
                entity: "sensor.alphaess_total_energy_feed_to_grid_pv",
                name: "Total Energy Feed to Grid (PV)",
            },
        ],
    },

    /* ── 4. Battery ────────────────────────────────────────────────────── */
    battery: {
        title: "AlphaESS Battery",
        cardName: "AlphaESS Battery",
        description:
            "Battery state of charge, power, health, temperatures, and energy totals.",
        entities: [
            { entity: "sensor.alphaess_soc_battery", name: "SoC Battery" },
            { entity: "sensor.alphaess_power_battery", name: "Battery Power" },
            {
                entity: "sensor.alphaess_battery_voltage",
                name: "Battery Voltage",
            },
            {
                entity: "sensor.alphaess_battery_current",
                name: "Battery Current",
            },
            { entity: "sensor.alphaess_soh_battery", name: "SoH Battery" },
            {
                entity: "sensor.alphaess_battery_status",
                name: "Battery Status",
            },
            { entity: "sensor.alphaess_battery_full", name: "Battery Full" },
            {
                entity: "sensor.alphaess_battery_min_cell_temp",
                name: "Battery Min Cell Temp",
            },
            {
                entity: "sensor.alphaess_battery_max_cell_temp",
                name: "Battery Max Cell Temp",
            },
            {
                entity: "sensor.alphaess_battery_max_charge_current",
                name: "Battery Max Charge Current",
            },
            {
                entity: "sensor.alphaess_battery_max_discharge_current",
                name: "Battery Max Discharge Current",
            },
            {
                entity: "sensor.alphaess_battery_remaining_time",
                name: "Battery Remaining Time",
            },
            { section: "Totals" },
            {
                entity: "sensor.alphaess_total_energy_charge_battery",
                name: "Total Energy Charge Battery",
            },
            {
                entity: "sensor.alphaess_total_energy_charge_battery_from_grid",
                name: "Total Energy Charge from Grid",
            },
            {
                entity: "sensor.alphaess_total_energy_discharge_battery",
                name: "Total Energy Discharge Battery",
            },
        ],
    },

    /* ── 5. Grid ───────────────────────────────────────────────────────── */
    grid: {
        title: "AlphaESS Grid",
        cardName: "AlphaESS Grid",
        description:
            "Grid power per phase, voltages, frequency, feed-in limits, and grid energy totals.",
        entities: [
            {
                entity: "sensor.alphaess_ct_rate_grid_meter",
                name: "CT Rate Grid Meter",
            },
            {
                entity: "sensor.alphaess_inverter_grid_frequency",
                name: "Inverter Grid Frequency",
            },
            {
                entity: "number.alphaess_helper_max_feed_to_grid",
                name: "Max Feed to Grid",
            },
            {
                entity: "sensor.alphaess_max_feed_to_grid",
                name: "Max Feed to Grid",
            },
            { entity: "sensor.alphaess_power_grid", name: "Power Grid" },
            { section: "Phase Power" },
            {
                entity: "sensor.alphaess_power_phase_a_grid",
                name: "Power Phase A",
            },
            {
                entity: "sensor.alphaess_power_phase_b_grid",
                name: "Power Phase B",
            },
            {
                entity: "sensor.alphaess_power_phase_c_grid",
                name: "Power Phase C",
            },
            { section: "Phase Voltage" },
            {
                entity: "sensor.alphaess_voltage_phase_a_grid",
                name: "Voltage Phase A",
            },
            {
                entity: "sensor.alphaess_voltage_phase_b_grid",
                name: "Voltage Phase B",
            },
            {
                entity: "sensor.alphaess_voltage_phase_c_grid",
                name: "Voltage Phase C",
            },
            { section: "Totals" },
            {
                entity: "sensor.alphaess_total_energy_consumption_from_grid_meter",
                name: "Total Consumption from Grid",
            },
            {
                entity: "sensor.alphaess_total_energy_feed_to_grid_meter",
                name: "Total Feed to Grid",
            },
            {
                entity: "sensor.alphaess_total_house_load",
                name: "Total House Load",
            },
        ],
    },

    /* ── 6. Dispatch ───────────────────────────────────────────────────── */
    dispatch: {
        title: "AlphaESS Dispatch",
        cardName: "AlphaESS Dispatch",
        description:
            "Dispatch mode controls, excess export settings, and dispatch status sensors.",
        entities: [
            {
                entity: "select.alphaess_helper_dispatch_mode",
                name: "Dispatch Mode",
            },
            {
                entity: "number.alphaess_helper_dispatch_duration",
                name: "Duration",
            },
            {
                entity: "number.alphaess_template_dispatch_power",
                name: "Power",
            },
            {
                entity: "number.alphaess_helper_dispatch_cutoff_soc",
                name: "Cutoff SoC",
            },
            { entity: "switch.alphaess_helper_dispatch", name: "Dispatch" },
            {
                entity: "button.alphaess_helper_dispatch_reset_full",
                name: "Dispatch Reset",
            },
            { section: "Excess Export" },
            {
                entity: "switch.alphaess_helper_excess_export",
                name: "Excess Export",
            },
            {
                entity: "switch.alphaess_helper_excess_export_pause",
                name: "Excess Export Pause",
            },
            { entity: "sensor.alphaess_excess_power", name: "Excess Power" },
            { section: "Status" },
            {
                entity: "sensor.alphaess_dispatch_start",
                name: "Dispatch Start",
            },
            {
                entity: "sensor.alphaess_dispatch_active_power",
                name: "Dispatch Active Power",
            },
            {
                entity: "sensor.alphaess_dispatch_reactive_power",
                name: "Dispatch Reactive Power",
            },
            { entity: "sensor.alphaess_dispatch_mode", name: "Dispatch Mode" },
            { entity: "sensor.alphaess_dispatch_soc", name: "Dispatch SoC" },
            { entity: "sensor.alphaess_dispatch_time", name: "Dispatch Time" },
        ],
    },

    /* ── 7. Grid Safety ────────────────────────────────────────────────── */
    grid_safety: {
        title: "AlphaESS Grid Safety",
        cardName: "AlphaESS Grid Safety",
        description:
            "Grid regulation, voltage protection (OvP/UvP), and frequency protection (OfP/UfP).",
        entities: [
            {
                entity: "sensor.alphaess_grid_regulation",
                name: "Grid Regulation",
            },
            { section: "Overvoltage Protection" },
            { entity: "sensor.alphaess_ovp_l1", name: "OvP L1" },
            { entity: "sensor.alphaess_ovp_l1_time", name: "OvP L1 Time" },
            { entity: "sensor.alphaess_ovp_l2", name: "OvP L2" },
            { entity: "sensor.alphaess_ovp_l2_time", name: "OvP L2 Time" },
            { entity: "sensor.alphaess_ovp_l3", name: "OvP L3" },
            { entity: "sensor.alphaess_ovp_l3_time", name: "OvP L3 Time" },
            { entity: "sensor.alphaess_ovp10", name: "OvP10" },
            { entity: "sensor.alphaess_ovp10_time", name: "OvP10 Time" },
            { section: "Undervoltage Protection" },
            { entity: "sensor.alphaess_uvp_l1", name: "UvP L1" },
            { entity: "sensor.alphaess_uvp_l1_time", name: "UvP L1 Time" },
            { entity: "sensor.alphaess_uvp_l2", name: "UvP L2" },
            { entity: "sensor.alphaess_uvp_l2_time", name: "UvP L2 Time" },
            { entity: "sensor.alphaess_uvp_l3", name: "UvP L3" },
            { entity: "sensor.alphaess_uvp_l3_time", name: "UvP L3 Time" },
            { section: "Overfrequency Protection" },
            { entity: "sensor.alphaess_ofp_l1", name: "OfP L1" },
            { entity: "sensor.alphaess_ofp_l1_time", name: "OfP L1 Time" },
            { entity: "sensor.alphaess_ofp_l2", name: "OfP L2" },
            { entity: "sensor.alphaess_ofp_l2_time", name: "OfP L2 Time" },
            { entity: "sensor.alphaess_ofp_l3", name: "OfP L3" },
            { entity: "sensor.alphaess_ofp_l3_time", name: "OfP L3 Time" },
            { section: "Underfrequency Protection" },
            { entity: "sensor.alphaess_ufp_l1", name: "UfP L1" },
            { entity: "sensor.alphaess_ufp_l1_time", name: "UfP L1 Time" },
            { entity: "sensor.alphaess_ufp_l2", name: "UfP L2" },
            { entity: "sensor.alphaess_ufp_l2_time", name: "UfP L2 Time" },
            { entity: "sensor.alphaess_ufp_l3", name: "UfP L3" },
            { entity: "sensor.alphaess_ufp_l3_time", name: "UfP L3 Time" },
        ],
    },

    /* ── 8. Warnings & Faults ──────────────────────────────────────────── */
    warnings: {
        title: "AlphaESS Warnings & Faults",
        cardName: "AlphaESS Warnings & Faults",
        description:
            "System faults, inverter warnings/faults, and battery warnings/faults.",
        entities: [
            { entity: "sensor.alphaess_system_fault", name: "System Fault" },
            { section: "Inverter" },
            {
                entity: "sensor.alphaess_inverter_warning_1",
                name: "Inverter Warning 1",
            },
            {
                entity: "sensor.alphaess_inverter_warning_2",
                name: "Inverter Warning 2",
            },
            {
                entity: "sensor.alphaess_inverter_fault_1",
                name: "Inverter Fault 1",
            },
            {
                entity: "sensor.alphaess_inverter_fault_2",
                name: "Inverter Fault 2",
            },
            { section: "Battery Warnings" },
            {
                entity: "sensor.alphaess_battery_warning",
                name: "Battery Warning",
            },
            {
                entity: "sensor.alphaess_battery_1_warning",
                name: "Battery Warning 1",
            },
            {
                entity: "sensor.alphaess_battery_2_warning",
                name: "Battery Warning 2",
            },
            {
                entity: "sensor.alphaess_battery_3_warning",
                name: "Battery Warning 3",
            },
            {
                entity: "sensor.alphaess_battery_4_warning",
                name: "Battery Warning 4",
            },
            {
                entity: "sensor.alphaess_battery_5_warning",
                name: "Battery Warning 5",
            },
            {
                entity: "sensor.alphaess_battery_6_warning",
                name: "Battery Warning 6",
            },
            { section: "Battery Faults" },
            { entity: "sensor.alphaess_battery_fault", name: "Battery Fault" },
            {
                entity: "sensor.alphaess_battery_1_fault",
                name: "Battery Fault 1",
            },
            {
                entity: "sensor.alphaess_battery_2_fault",
                name: "Battery Fault 2",
            },
            {
                entity: "sensor.alphaess_battery_3_fault",
                name: "Battery Fault 3",
            },
            {
                entity: "sensor.alphaess_battery_4_fault",
                name: "Battery Fault 4",
            },
            {
                entity: "sensor.alphaess_battery_5_fault",
                name: "Battery Fault 5",
            },
            {
                entity: "sensor.alphaess_battery_6_fault",
                name: "Battery Fault 6",
            },
        ],
    },

    /* ── 9. System ─────────────────────────────────────────────────────── */
    system: {
        title: "AlphaESS System",
        cardName: "AlphaESS System",
        description:
            "Inverter power, backup power, house load, network info, and firmware versions.",
        entities: [
            {
                entity: "sensor.alphaess_inverter_temperature",
                name: "Inverter Temperature",
            },
            {
                entity: "sensor.alphaess_power_inverter",
                name: "Power Inverter",
            },
            {
                entity: "sensor.alphaess_power_inverter_l1",
                name: "Power Inverter L1",
            },
            {
                entity: "sensor.alphaess_power_inverter_l2",
                name: "Power Inverter L2",
            },
            {
                entity: "sensor.alphaess_power_inverter_l3",
                name: "Power Inverter L3",
            },
            { section: "Backup Power" },
            {
                entity: "sensor.alphaess_backup_power_inverter",
                name: "Backup Power Inverter",
            },
            {
                entity: "sensor.alphaess_backup_power_inverter_l1",
                name: "Backup Power Inverter L1",
            },
            {
                entity: "sensor.alphaess_backup_power_inverter_l2",
                name: "Backup Power Inverter L2",
            },
            {
                entity: "sensor.alphaess_backup_power_inverter_l3",
                name: "Backup Power Inverter L3",
            },
            { section: true },
            {
                entity: "sensor.alphaess_current_house_load",
                name: "Current House Load",
            },
            {
                entity: "sensor.alphaess_inverter_work_mode",
                name: "Inverter Work Mode",
            },
            { section: "Date & Time" },
            { entity: "sensor.alphaess_system_date", name: "System Date" },
            { entity: "sensor.alphaess_system_time", name: "System Time" },
            {
                entity: "button.alphaess_helper_synchronise_date_time",
                name: "Synchronise Date & Time",
            },
            { section: "Network" },
            { entity: "sensor.alphaess_ip_method", name: "IP Method" },
            { entity: "sensor.alphaess_local_ip_normalised", name: "Local IP" },
            {
                entity: "sensor.alphaess_subnet_mask_normalised",
                name: "Subnet Mask",
            },
            { entity: "sensor.alphaess_gateway_normalised", name: "Gateway" },
            {
                entity: "sensor.alphaess_modbus_baud_rate",
                name: "Modbus Baud Rate",
            },
            { section: "Firmware" },
            {
                entity: "sensor.alphaess_bms_version_normalised",
                name: "BMS Version",
            },
            {
                entity: "sensor.alphaess_ems_version_normalised",
                name: "EMS Version",
            },
            { entity: "sensor.alphaess_lmu_version", name: "LMU Version" },
            { entity: "sensor.alphaess_iso_version", name: "ISO Version" },
            {
                entity: "sensor.alphaess_inverter_version",
                name: "Inverter Version",
            },
            {
                entity: "sensor.alphaess_inverter_arm_version",
                name: "Inverter ARM Version",
            },
        ],
    },
};

/* ═══════════════════════════════════════════════════════════════════════ *
 *  BASE CARD CLASS                                                       *
 * ═══════════════════════════════════════════════════════════════════════ */

class AlphaESSEntitiesCard extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: "open" });
        this._hass = null;
        this._config = {};
        this._presetKey = null; // set by subclass
        this._rendered = false;
    }

    /* --- lifecycle ------------------------------------------------------- */

    /* Called by HA with the YAML/UI config — may run before connectedCallback */
    setConfig(config) {
        if (!this._presetKey) throw new Error("AlphaESS card: unknown preset");
        const preset = CARD_PRESETS[this._presetKey];
        if (!preset)
            throw new Error(
                `AlphaESS card: unknown preset key '${this._presetKey}'`,
            );
        this._config = {
            title: config.title ?? preset.title,
            entities: config.entities ?? preset.entities,
        };
        this._rendered = false;
        if (this.isConnected) {
            this._render();
            this._rendered = true;
        }
    }

    /* Called when the element is inserted into the DOM */
    connectedCallback() {
        if (!this._rendered && this._config && this._config.entities) {
            this._render();
            this._rendered = true;
        }
        if (this._hass) this._update();
    }

    set hass(hass) {
        this._hass = hass;
        if (!this._rendered && this._config && this._config.entities) {
            this._render();
            this._rendered = true;
        }
        this._update();
    }

    getCardSize() {
        const count =
            this._config.entities?.filter((e) => e.entity).length || 0;
        return Math.min(8, Math.max(3, Math.ceil(count / 5) + 2));
    }

    getGridOptions() {
        return {
            columns: 6,
            min_columns: 3,
            max_columns: 12,
        };
    }

    /* --- render ---------------------------------------------------------- */

    _render() {
        const entities = this._config.entities || [];
        let rowsHtml = "";

        for (const item of entities) {
            if (item.section !== undefined) {
                const label =
                    typeof item.section === "string" ? item.section : "";
                rowsHtml += `<div class="section-divider">${label ? `<span class="section-label">${label}</span>` : ""}</div>`;
            } else if (item.entity) {
                rowsHtml += `<div class="entity-row" data-entity="${item.entity}"><ha-icon class="entity-icon" icon="mdi:eye"></ha-icon><span class="name">${item.name || item.entity}</span><span class="state">—</span></div>`;
            }
        }

        this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }
        ha-card {
          overflow: hidden;
          display: flex;
          flex-direction: column;
          box-sizing: border-box;
        }
        .card-header {
          padding: 12px 16px 4px;
          font-size: 16px;
          font-weight: 500;
          color: var(--ha-card-header-color, var(--primary-text-color));
          line-height: 1.4;
          flex-shrink: 0;
        }
        .entities-container {
          padding-bottom: 8px;
          overflow-y: auto;
                    max-height: 520px;
        }

        /* entity rows */
        .entity-row {
          display: flex;
          align-items: center;
          padding: 8px 16px;
          cursor: pointer;
          min-height: 40px;
          box-sizing: border-box;
        }
        .entity-row:hover {
          background: var(--secondary-background-color, rgba(255,255,255,0.05));
        }
        .entity-row:active {
          background: var(--divider-color, rgba(255,255,255,0.1));
        }
        .entity-icon {
          color: var(--paper-item-icon-color, #44739e);
          margin-right: 16px;
          flex-shrink: 0;
          --mdc-icon-size: 24px;
        }
        .entity-icon.active-icon {
          color: var(--state-icon-active-color, var(--paper-item-icon-active-color, #FDD835));
        }
        .entity-row .name {
          flex: 1;
          font-size: 14px;
          color: var(--primary-text-color);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          margin-right: 8px;
        }
        .entity-row .state {
          font-size: 14px;
          color: var(--primary-text-color);
          text-align: right;
          white-space: nowrap;
          flex-shrink: 0;
        }

        /* section dividers */
        .section-divider {
          padding: 4px 16px 2px;
          border-top: 1px solid var(--divider-color, rgba(255,255,255,0.12));
          margin-top: 4px;
        }
        .section-divider:first-child {
          border-top: none;
          margin-top: 0;
        }
        .section-label {
          font-size: 12px;
          font-weight: 600;
          color: var(--secondary-text-color);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }
      </style>

      <ha-card>
        ${this._config.title ? `<div class="card-header">${this._config.title}</div>` : ""}
        <div class="entities-container">${rowsHtml}</div>
      </ha-card>
    `;

        /* attach click → more-info */
        this.shadowRoot.querySelectorAll(".entity-row").forEach((row) => {
            row.addEventListener("click", () => {
                const entityId = row.dataset.entity;
                if (entityId) this._fireMoreInfo(entityId);
            });
        });
    }

    /* --- update values from hass ----------------------------------------- */

    _update() {
        if (!this._hass || !this.shadowRoot) return;
        const rows = this.shadowRoot.querySelectorAll(".entity-row");
        rows.forEach((row) => {
            const entityId = row.dataset.entity;
            if (!entityId) return;

            const stateEl = row.querySelector(".state");
            const iconEl = row.querySelector("ha-icon");

            if (stateEl) {
                stateEl.textContent = getEntityState(this._hass, entityId);
            }
            if (iconEl) {
                iconEl.setAttribute(
                    "icon",
                    getEntityIcon(this._hass, entityId),
                );
                const stateObj = this._hass.states?.[entityId];
                const isActive =
                    stateObj &&
                    (stateObj.state === "on" || stateObj.state === "home");
                iconEl.classList.toggle("active-icon", isActive);
            }
        });
    }

    /* --- more-info event ------------------------------------------------- */

    _fireMoreInfo(entityId) {
        this.dispatchEvent(
            new CustomEvent("hass-more-info", {
                bubbles: true,
                composed: true,
                detail: { entityId },
            }),
        );
    }
}

/* ═══════════════════════════════════════════════════════════════════════ *
 *  REGISTER ALL 9 CARDS                                                  *
 * ═══════════════════════════════════════════════════════════════════════ */

function registerAlphaESSCard(presetKey) {
    const preset = CARD_PRESETS[presetKey];
    if (!preset) {
        console.error(
            `[alphaess-entities-cards] Unknown preset key: ${presetKey}`,
        );
        return;
    }
    const tag = `alphaess-${presetKey.replace(/_/g, "-")}-card`;

    try {
        if (customElements.get(tag)) {
            console.warn(
                `[alphaess-entities-cards] ${tag} already defined, skipping`,
            );
            return;
        }

        const CardClass = class extends AlphaESSEntitiesCard {
            constructor() {
                super();
                this._presetKey = presetKey;
            }

            static getStubConfig() {
                return { title: preset.title };
            }

            static getConfigForm() {
                return {
                    schema: [{ name: "title", selector: { text: {} } }],
                    computeLabel: (schema) => {
                        const labels = { title: "Title" };
                        return labels[schema.name] ?? schema.name;
                    },
                };
            }
        };

        customElements.define(tag, CardClass);
        console.debug(
            `[alphaess-entities-cards] Defined custom element: ${tag}`,
        );

        window.customCards = window.customCards || [];
        if (!window.customCards.some((c) => c.type === tag)) {
            window.customCards.push({
                type: tag,
                name: preset.cardName,
                preview: true,
                description: preset.description,
                documentationURL:
                    "https://github.com/Poshy163/homeassistant-alphaESS-modbus",
            });
        }
    } catch (err) {
        console.error(
            `[alphaess-entities-cards] Failed to register ${tag}:`,
            err,
        );
    }
}

Object.keys(CARD_PRESETS).forEach(registerAlphaESSCard);

console.info(
    `%c  ALPHAESS-ENTITY-CARDS  %c  v${ENTITIES_CARDS_VERSION}  `,
    "color: #6FB6C6; font-weight: bold; background: #1c1c1c",
    "color: white; font-weight: bold; background: #333",
);
