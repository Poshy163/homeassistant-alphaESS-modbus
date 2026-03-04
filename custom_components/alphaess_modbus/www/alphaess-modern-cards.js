/**
 * AlphaESS Modern Cards v1.1.1
 *
 * Custom Lovelace cards for AlphaESS.
 */

console.debug("[alphaess-modern-cards] Loading modern AlphaESS cards module…");

const MODERN_CARDS_VERSION = "1.1.1";
const FLOW_DEADBAND_W = 30;

const DEFAULTS = {
    solar: "sensor.alphaess_current_pv_production",
    house: "sensor.alphaess_current_house_load",
    grid: "sensor.alphaess_power_grid",
    battery: "sensor.alphaess_power_battery",
    soc: "sensor.alphaess_soc_battery",
    soh: "sensor.alphaess_soh_battery",
    battery_voltage: "sensor.alphaess_battery_voltage",
    battery_current: "sensor.alphaess_battery_current",
    battery_status: "sensor.alphaess_battery_status",
    total_pv: "sensor.alphaess_total_energy_from_pv",
    total_house: "sensor.alphaess_total_house_load",
    total_grid_import:
        "sensor.alphaess_total_energy_consumption_from_grid_meter",
    total_grid_export: "sensor.alphaess_total_energy_feed_to_grid_meter",
    total_batt_charge: "sensor.alphaess_total_energy_charge_battery",
    total_batt_discharge: "sensor.alphaess_total_energy_discharge_battery",
};

function getNum(hass, entityId) {
    const st = hass?.states?.[entityId];
    if (!st || st.state === "unknown" || st.state === "unavailable") {
        return null;
    }
    const n = Number(st.state);
    return Number.isFinite(n) ? n : null;
}

function getText(hass, entityId) {
    const st = hass?.states?.[entityId];
    if (!st || st.state === "unknown" || st.state === "unavailable") {
        return "—";
    }
    return st.state;
}

function formatPower(value) {
    if (value === null) return "—";
    const abs = Math.abs(value);
    if (abs >= 1000) return `${(abs / 1000).toFixed(2)} kW`;
    return `${abs.toFixed(0)} W`;
}

function formatEnergy(value) {
    if (value === null) return "—";
    if (Math.abs(value) >= 1000) return `${(value / 1000).toFixed(2)} MWh`;
    return `${value.toFixed(1)} kWh`;
}

function isActiveFlow(value) {
    return value !== null && Math.abs(value) >= FLOW_DEADBAND_W;
}

class AlphaESSLiveKpiCard extends HTMLElement {
    setConfig(config) {
        this._config = {
            title: config?.title ?? "AlphaESS Live KPIs",
            solar_entity: config?.solar_entity ?? DEFAULTS.solar,
            house_entity: config?.house_entity ?? DEFAULTS.house,
            grid_entity: config?.grid_entity ?? DEFAULTS.grid,
            battery_entity: config?.battery_entity ?? DEFAULTS.battery,
        };
        if (!this.shadowRoot) this.attachShadow({ mode: "open" });
        this._render();
    }

    set hass(hass) {
        this._hass = hass;
        this._render();
    }

    getCardSize() {
        return 3;
    }

    _render() {
        if (!this.shadowRoot || !this._config) return;
        const hass = this._hass;
        const c = this._config;

        const solar = getNum(hass, c.solar_entity);
        const house = getNum(hass, c.house_entity);
        const grid = getNum(hass, c.grid_entity);
        const battery = getNum(hass, c.battery_entity);

        const gridState =
            grid === null || Math.abs(grid) < FLOW_DEADBAND_W
                ? "idle"
                : grid > 0
                  ? "import"
                  : "export";
        const battState =
            battery === null || Math.abs(battery) < FLOW_DEADBAND_W
                ? "idle"
                : battery > 0
                  ? "discharge"
                  : "charge";

        this.shadowRoot.innerHTML = `
      <style>
        ha-card { padding: 14px; }
        .title { font-size: 16px; font-weight: 600; margin-bottom: 12px; }
        .grid {
          display: grid;
          grid-template-columns: repeat(2, minmax(0, 1fr));
          gap: 10px;
        }
        .tile {
          border: 1px solid var(--divider-color, #3a3a3a);
          border-radius: 10px;
          padding: 10px;
          background: color-mix(in srgb, var(--card-background-color, #1f1f1f) 88%, #000 12%);
        }
        .name { font-size: 12px; color: var(--secondary-text-color, #aaa); }
        .value { font-size: 18px; font-weight: 700; margin: 4px 0 2px; }
        .sub { font-size: 11px; color: var(--secondary-text-color, #aaa); text-transform: uppercase; letter-spacing: 0.05em; }
        .solar { color: #f6c343; }
        .house { color: #5ec2d8; }
        .grid-import { color: #f29f4c; }
        .grid-export { color: #ff7b3e; }
        .grid-idle { color: #9aa0a6; }
        .batt-charge { color: #9bd36d; }
        .batt-discharge { color: #6dc17d; }
        .batt-idle { color: #9aa0a6; }
      </style>
      <ha-card>
        <div class="title">${c.title}</div>
        <div class="grid">
          <div class="tile">
            <div class="name">Solar</div>
            <div class="value solar">${formatPower(solar)}</div>
            <div class="sub">production</div>
          </div>
          <div class="tile">
            <div class="name">Home</div>
            <div class="value house">${formatPower(house)}</div>
            <div class="sub">load</div>
          </div>
          <div class="tile">
            <div class="name">Grid</div>
            <div class="value grid-${gridState}">${formatPower(grid)}</div>
            <div class="sub">${gridState}</div>
          </div>
          <div class="tile">
            <div class="name">Battery</div>
            <div class="value batt-${battState}">${formatPower(battery)}</div>
            <div class="sub">${battState}</div>
          </div>
        </div>
      </ha-card>
    `;
    }

    static getStubConfig() {
        return { title: "AlphaESS Live KPIs" };
    }
}

class AlphaESSBatteryInsightCard extends HTMLElement {
    setConfig(config) {
        this._config = {
            title: config?.title ?? "AlphaESS Battery Insight",
            soc_entity: config?.soc_entity ?? DEFAULTS.soc,
            soh_entity: config?.soh_entity ?? DEFAULTS.soh,
            battery_entity: config?.battery_entity ?? DEFAULTS.battery,
            battery_voltage_entity:
                config?.battery_voltage_entity ?? DEFAULTS.battery_voltage,
            battery_current_entity:
                config?.battery_current_entity ?? DEFAULTS.battery_current,
            battery_status_entity:
                config?.battery_status_entity ?? DEFAULTS.battery_status,
        };
        if (!this.shadowRoot) this.attachShadow({ mode: "open" });
        this._render();
    }

    set hass(hass) {
        this._hass = hass;
        this._render();
    }

    getCardSize() {
        return 3;
    }

    _render() {
        if (!this.shadowRoot || !this._config) return;
        const hass = this._hass;
        const c = this._config;

        const soc = getNum(hass, c.soc_entity);
        const soh = getNum(hass, c.soh_entity);
        const battPower = getNum(hass, c.battery_entity);
        const battVoltage = getNum(hass, c.battery_voltage_entity);
        const battCurrent = getNum(hass, c.battery_current_entity);
        const battStatus = getText(hass, c.battery_status_entity);

        const pct = soc === null ? 0 : Math.max(0, Math.min(100, soc));
        const fill = pct <= 20 ? "#e05c5c" : pct <= 50 ? "#f0a93e" : "#7dc56b";

        this.shadowRoot.innerHTML = `
      <style>
        ha-card { padding: 14px; }
        .title { font-size: 16px; font-weight: 600; margin-bottom: 12px; }
        .soc-row { display: grid; grid-template-columns: 1fr auto; gap: 8px; align-items: center; margin-bottom: 8px; }
        .soc-label { font-size: 12px; color: var(--secondary-text-color, #aaa); }
        .soc-value { font-size: 24px; font-weight: 800; }
        .bar { height: 12px; border-radius: 999px; background: #2d333b; overflow: hidden; border: 1px solid #3a404a; margin-bottom: 12px; }
        .fill { height: 100%; transition: width .35s ease; }
        .rows { display: grid; gap: 8px; }
        .row { display: grid; grid-template-columns: 1fr auto; font-size: 13px; }
        .k { color: var(--secondary-text-color, #aaa); }
        .v { font-weight: 600; }
      </style>
      <ha-card>
        <div class="title">${c.title}</div>
        <div class="soc-row">
          <div class="soc-label">State of Charge</div>
          <div class="soc-value">${soc === null ? "—" : `${Math.round(soc)}%`}</div>
        </div>
        <div class="bar"><div class="fill" style="width:${pct}%;background:${fill};"></div></div>
        <div class="rows">
          <div class="row"><div class="k">Battery Power</div><div class="v">${formatPower(battPower)}</div></div>
          <div class="row"><div class="k">Battery Voltage</div><div class="v">${battVoltage === null ? "—" : `${battVoltage.toFixed(1)} V`}</div></div>
          <div class="row"><div class="k">Battery Current</div><div class="v">${battCurrent === null ? "—" : `${battCurrent.toFixed(1)} A`}</div></div>
          <div class="row"><div class="k">State of Health</div><div class="v">${soh === null ? "—" : `${Math.round(soh)}%`}</div></div>
          <div class="row"><div class="k">Status</div><div class="v">${battStatus}</div></div>
        </div>
      </ha-card>
    `;
    }

    static getStubConfig() {
        return { title: "AlphaESS Battery Insight" };
    }
}

class AlphaESSEnergySummaryCard extends HTMLElement {
    setConfig(config) {
        this._config = {
            title: config?.title ?? "AlphaESS Energy Summary",
            total_pv_entity: config?.total_pv_entity ?? DEFAULTS.total_pv,
            total_house_entity:
                config?.total_house_entity ?? DEFAULTS.total_house,
            total_grid_import_entity:
                config?.total_grid_import_entity ?? DEFAULTS.total_grid_import,
            total_grid_export_entity:
                config?.total_grid_export_entity ?? DEFAULTS.total_grid_export,
            total_batt_charge_entity:
                config?.total_batt_charge_entity ?? DEFAULTS.total_batt_charge,
            total_batt_discharge_entity:
                config?.total_batt_discharge_entity ??
                DEFAULTS.total_batt_discharge,
        };
        if (!this.shadowRoot) this.attachShadow({ mode: "open" });
        this._render();
    }

    set hass(hass) {
        this._hass = hass;
        this._render();
    }

    getCardSize() {
        return 4;
    }

    _render() {
        if (!this.shadowRoot || !this._config) return;
        const hass = this._hass;
        const c = this._config;

        const totalPv = getNum(hass, c.total_pv_entity);
        const totalHouse = getNum(hass, c.total_house_entity);
        const totalImport = getNum(hass, c.total_grid_import_entity);
        const totalExport = getNum(hass, c.total_grid_export_entity);
        const totalCharge = getNum(hass, c.total_batt_charge_entity);
        const totalDischarge = getNum(hass, c.total_batt_discharge_entity);

        this.shadowRoot.innerHTML = `
      <style>
        ha-card { padding: 14px; }
        .title { font-size: 16px; font-weight: 600; margin-bottom: 12px; }
        .table { display: grid; gap: 8px; }
        .row {
          display: grid;
          grid-template-columns: 1fr auto;
          align-items: center;
          font-size: 13px;
          padding: 8px 10px;
          border: 1px solid var(--divider-color, #3a3a3a);
          border-radius: 8px;
        }
        .name { color: var(--secondary-text-color, #aaa); }
        .value { font-weight: 700; }
      </style>
      <ha-card>
        <div class="title">${c.title}</div>
        <div class="table">
          <div class="row"><div class="name">Total Energy from PV</div><div class="value">${formatEnergy(totalPv)}</div></div>
          <div class="row"><div class="name">Total House Load</div><div class="value">${formatEnergy(totalHouse)}</div></div>
          <div class="row"><div class="name">Grid Import</div><div class="value">${formatEnergy(totalImport)}</div></div>
          <div class="row"><div class="name">Grid Export</div><div class="value">${formatEnergy(totalExport)}</div></div>
          <div class="row"><div class="name">Battery Charge</div><div class="value">${formatEnergy(totalCharge)}</div></div>
          <div class="row"><div class="name">Battery Discharge</div><div class="value">${formatEnergy(totalDischarge)}</div></div>
        </div>
      </ha-card>
    `;
    }

    static getStubConfig() {
        return { title: "AlphaESS Energy Summary" };
    }
}

class AlphaESSRibbonFlowCard extends HTMLElement {
    setConfig(config) {
        this._config = {
            title: config?.title ?? "AlphaESS Ribbon Flow",
            solar_entity: config?.solar_entity ?? DEFAULTS.solar,
            house_entity: config?.house_entity ?? DEFAULTS.house,
            grid_entity: config?.grid_entity ?? DEFAULTS.grid,
            battery_entity: config?.battery_entity ?? DEFAULTS.battery,
        };
        if (!this.shadowRoot) this.attachShadow({ mode: "open" });
        this._render();
    }

    set hass(hass) {
        this._hass = hass;
        this._render();
    }

    getCardSize() {
        return 3;
    }

    _render() {
        if (!this.shadowRoot || !this._config) return;
        const hass = this._hass;
        const c = this._config;

        const solar = getNum(hass, c.solar_entity);
        const house = getNum(hass, c.house_entity);
        const grid = getNum(hass, c.grid_entity);
        const battery = getNum(hass, c.battery_entity);

        const solarActive = solar !== null && solar > FLOW_DEADBAND_W;
        const gridActive = isActiveFlow(grid);
        const battActive = isActiveFlow(battery);

        const gridDirection = grid > 0 ? "right" : "left";
        const batteryDirection = battery > 0 ? "left" : "right";

        this.shadowRoot.innerHTML = `
      <style>
        ha-card { padding: 14px; }
        .title { font-size: 16px; font-weight: 600; margin-bottom: 8px; }
        .house { font-size: 12px; color: var(--secondary-text-color, #aaa); margin-bottom: 10px; }
        .rows { display: grid; gap: 10px; }
        .row {
          display: grid;
          grid-template-columns: 82px 1fr auto;
          align-items: center;
          gap: 8px;
        }
        .label { font-size: 12px; color: var(--secondary-text-color, #aaa); }
        .value { font-size: 12px; font-weight: 700; }
        .lane {
          position: relative;
          height: 8px;
          border-radius: 999px;
          background: #2b323c;
          overflow: hidden;
          border: 1px solid #38404b;
        }
        .lane::after {
          content: "";
          position: absolute;
          inset: 0;
          opacity: 0.8;
        }
        .lane.solar::after { background: linear-gradient(90deg, #7d6520, #f4c94a); }
        .lane.grid::after { background: linear-gradient(90deg, #7d4720, #e57b3d); }
        .lane.batt::after { background: linear-gradient(90deg, #5a7f39, #89c76f); }
        .dot {
          position: absolute;
          top: 50%;
          width: 8px;
          height: 8px;
          margin-top: -4px;
          border-radius: 50%;
          opacity: 0;
          animation-duration: 1.8s;
          animation-iteration-count: infinite;
          animation-timing-function: linear;
          animation-play-state: paused;
        }
        .d1 { animation-delay: 0s; }
        .d2 { animation-delay: 0.6s; }
        .d3 { animation-delay: 1.2s; }
        .dot.right { animation-name: flowRight; }
        .dot.left { animation-name: flowLeft; }
        .active .dot { animation-play-state: running; opacity: 1; }
        .solar .dot { background: #f4c94a; }
        .grid .dot { background: #e57b3d; }
        .batt .dot { background: #89c76f; }

        @keyframes flowRight {
          0% { left: 0; opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { left: calc(100% - 8px); opacity: 0; }
        }
        @keyframes flowLeft {
          0% { left: calc(100% - 8px); opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { left: 0; opacity: 0; }
        }
      </style>
      <ha-card>
        <div class="title">${c.title}</div>
        <div class="house">Home load: <strong>${formatPower(house)}</strong></div>
        <div class="rows">
          <div class="row">
            <div class="label">Solar → Home</div>
            <div class="lane solar ${solarActive ? "active" : ""}">
              <span class="dot right d1"></span><span class="dot right d2"></span><span class="dot right d3"></span>
            </div>
            <div class="value">${formatPower(solar)}</div>
          </div>
          <div class="row">
            <div class="label">Grid ↔ Home</div>
            <div class="lane grid ${gridActive ? "active" : ""}">
              <span class="dot ${gridDirection} d1"></span><span class="dot ${gridDirection} d2"></span><span class="dot ${gridDirection} d3"></span>
            </div>
            <div class="value">${formatPower(grid)}</div>
          </div>
          <div class="row">
            <div class="label">Battery ↔ Home</div>
            <div class="lane batt ${battActive ? "active" : ""}">
              <span class="dot ${batteryDirection} d1"></span><span class="dot ${batteryDirection} d2"></span><span class="dot ${batteryDirection} d3"></span>
            </div>
            <div class="value">${formatPower(battery)}</div>
          </div>
        </div>
      </ha-card>
    `;
    }

    static getStubConfig() {
        return { title: "AlphaESS Ribbon Flow" };
    }
}

function registerCard(type, klass, name, description) {
    if (!customElements.get(type)) {
        customElements.define(type, klass);
    }
    window.customCards = window.customCards || [];
    if (!window.customCards.some((c) => c.type === type)) {
        window.customCards.push({
            type,
            name,
            preview: false,
            description,
            documentationURL:
                "https://github.com/Poshy163/homeassistant-alphaESS-modbus",
        });
    }
}

try {
    registerCard(
        "alphaess-live-kpi-card",
        AlphaESSLiveKpiCard,
        "AlphaESS Live KPIs",
        "Compact live power KPIs for solar, house, grid and battery.",
    );
    registerCard(
        "alphaess-battery-insight-card",
        AlphaESSBatteryInsightCard,
        "AlphaESS Battery Insight",
        "Battery-focused card with SoC bar, power, voltage/current and health.",
    );
    registerCard(
        "alphaess-energy-summary-card",
        AlphaESSEnergySummaryCard,
        "AlphaESS Energy Summary",
        "Clean totals summary for PV, house, grid import/export and battery energy.",
    );
    registerCard(
        "alphaess-ribbon-flow-card",
        AlphaESSRibbonFlowCard,
        "AlphaESS Ribbon Flow",
        "Animated lane-based power flows between solar/grid/battery and home.",
    );

    console.info(
        `%c  ALPHAESS-MODERN-CARDS  %c  v${MODERN_CARDS_VERSION}  `,
        "color: #58a6ff; font-weight: bold; background: #0f1720",
        "color: white; font-weight: bold; background: #334155",
    );
} catch (err) {
    console.error("[alphaess-modern-cards] Failed to register card(s):", err);
}
