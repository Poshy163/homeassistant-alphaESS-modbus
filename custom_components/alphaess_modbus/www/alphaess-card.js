/**
 * AlphaESS Power Flow Card
 *
 * A custom Lovelace card for Home Assistant that visualises real-time power
 * flow between Solar, Grid, Home and Battery for AlphaESS inverters.
 *
 * Appears in the "Add card" picker under the name "AlphaESS Power Flow".
 * No external dependencies — pure HTML / CSS / SVG.
 */

console.debug("[alphaess-card] Loading alphaess-power-flow-card module…");

const CARD_VERSION = "1.0.0";

/* ─── default entity IDs (auto-match the alphaess_modbus integration) ── */
const DEFAULTS = {
    solar: "sensor.alphaess_current_pv_production",
    grid: "sensor.alphaess_power_grid",
    battery: "sensor.alphaess_power_battery",
    battery_soc: "sensor.alphaess_soc_battery",
    house: "sensor.alphaess_current_house_load",
};

/* ─── colours ──────────────────────────────────────────────────────────── */
const COLORS = {
    solar: "#FABF00",
    grid_consume: "#C18349",
    grid_feedin: "#DF681F",
    battery_charge: "#A0C770",
    battery_discharge: "#78B060",
    house: "#6FB6C6",
    inactive: "#444",
    text: "var(--primary-text-color, #fff)",
    secondary: "var(--secondary-text-color, #aaa)",
    card_bg: "var(--ha-card-background, var(--card-background-color, #1c1c1c))",
};

/* ─── helpers ──────────────────────────────────────────────────────────── */
function stateValue(hass, entityId) {
    const s = hass.states[entityId];
    if (!s || s.state === "unavailable" || s.state === "unknown") return null;
    return parseFloat(s.state);
}

function fmt(value, decimals = 2) {
    if (value === null || isNaN(value)) return "—";
    const abs = Math.abs(value);
    if (abs >= 1000) return (value / 1000).toFixed(decimals) + " kW";
    return value.toFixed(0) + " W";
}

function fmtKw(value, decimals = 2) {
    if (value === null || isNaN(value)) return "—";
    return Math.abs(value).toFixed(decimals) + " kW";
}

/* ─── card class ───────────────────────────────────────────────────────── */
class AlphaESSPowerFlowCard extends HTMLElement {
    /* --- lifecycle ------------------------------------------------------- */

    constructor() {
        super();
        this.attachShadow({ mode: "open" });
        this._hass = null;
        this._config = {};
        this._rendered = false;
    }

    /* Called by HA with the YAML/UI config — may run before connectedCallback */
    setConfig(config) {
        if (!config)
            throw new Error("AlphaESS Power Flow: invalid configuration");
        this._config = {
            title: config.title ?? "AlphaESS Power Flow",
            solar_entity: config.solar_entity ?? DEFAULTS.solar,
            grid_entity: config.grid_entity ?? DEFAULTS.grid,
            battery_entity: config.battery_entity ?? DEFAULTS.battery,
            battery_soc_entity:
                config.battery_soc_entity ?? DEFAULTS.battery_soc,
            house_entity: config.house_entity ?? DEFAULTS.house,
            unit: config.unit ?? "auto", // "W", "kW", or "auto"
        };
        this._rendered = false;
        if (this.isConnected) {
            this._render();
            this._rendered = true;
        }
    }

    /* Called when the element is inserted into the DOM */
    connectedCallback() {
        if (!this._rendered && this._config) {
            this._render();
            this._rendered = true;
        }
        if (this._hass) this._updateValues();
    }

    set hass(hass) {
        this._hass = hass;
        if (!this._rendered && this._config) {
            this._render();
            this._rendered = true;
        }
        this._updateValues();
    }

    getCardSize() {
        return 5;
    }

    getGridOptions() {
        return { rows: 5, columns: 12, min_rows: 4 };
    }

    /* --- stub config for the card picker --------------------------------- */

    static getStubConfig() {
        return {
            title: "AlphaESS Power Flow",
            solar_entity: DEFAULTS.solar,
            grid_entity: DEFAULTS.grid,
            battery_entity: DEFAULTS.battery,
            battery_soc_entity: DEFAULTS.battery_soc,
            house_entity: DEFAULTS.house,
        };
    }

    /* --- built-in form editor -------------------------------------------- */

    static getConfigForm() {
        return {
            schema: [
                { name: "title", selector: { text: {} } },
                {
                    name: "solar_entity",
                    required: true,
                    selector: { entity: { domain: "sensor" } },
                },
                {
                    name: "grid_entity",
                    required: true,
                    selector: { entity: { domain: "sensor" } },
                },
                {
                    name: "battery_entity",
                    required: true,
                    selector: { entity: { domain: "sensor" } },
                },
                {
                    name: "battery_soc_entity",
                    required: true,
                    selector: { entity: { domain: "sensor" } },
                },
                {
                    name: "house_entity",
                    required: true,
                    selector: { entity: { domain: "sensor" } },
                },
                {
                    name: "unit",
                    selector: {
                        select: {
                            options: [
                                { value: "auto", label: "Auto" },
                                { value: "W", label: "Watts" },
                                { value: "kW", label: "Kilowatts" },
                            ],
                        },
                    },
                },
            ],
            computeLabel: (schema) => {
                const labels = {
                    title: "Title",
                    solar_entity: "Solar production entity",
                    grid_entity: "Grid power entity",
                    battery_entity: "Battery power entity",
                    battery_soc_entity: "Battery SoC entity",
                    house_entity: "House load entity",
                    unit: "Display unit",
                };
                return labels[schema.name] ?? schema.name;
            },
        };
    }

    /* --- format helper --------------------------------------------------- */

    _fmt(value) {
        if (value === null || isNaN(value)) return "—";
        const unit = this._config.unit ?? "auto";
        if (unit === "kW") return fmtKw(value);
        if (unit === "W") {
            if (value === null) return "—";
            return Math.abs(value).toFixed(0) + " W";
        }
        return fmt(value);
    }

    /* --- render ---------------------------------------------------------- */

    _render() {
        const shadow = this.shadowRoot;

        shadow.innerHTML = `
      <style>
        :host {
          display: block;
        }
        ha-card {
          padding: 16px;
          box-sizing: border-box;
        }
        .card-header {
          font-size: 16px;
          font-weight: 500;
          padding: 0 0 12px 0;
          color: ${COLORS.text};
        }
        .flow-container {
          position: relative;
          width: 100%;
          aspect-ratio: 5 / 3;
          min-height: 200px;
        }
        .flow-container svg {
          width: 100%;
          height: 100%;
        }

        /* ── node icons ────────────────────────────────── */
        .node-icon {
          font-size: 28px;
          text-anchor: middle;
          dominant-baseline: central;
        }
        .node-label {
          font-size: 11px;
          fill: ${COLORS.secondary};
          text-anchor: middle;
          font-family: var(--ha-card-header-font-family, inherit);
        }
        .node-value {
          font-size: 14px;
          font-weight: 600;
          fill: ${COLORS.text};
          text-anchor: middle;
          font-family: var(--ha-card-header-font-family, inherit);
        }
        .node-sub {
          font-size: 11px;
          fill: ${COLORS.secondary};
          text-anchor: middle;
          font-family: var(--ha-card-header-font-family, inherit);
        }

        /* ── flow lines ────────────────────────────────── */
        .flow-line {
          stroke-width: 2;
          fill: none;
          opacity: 0.3;
        }
        .flow-line.active {
          opacity: 0.6;
        }

        /* ── animated dots ─────────────────────────────── */
        .flow-dot {
          r: 3;
          opacity: 0;
        }
        .flow-dot.active {
          opacity: 1;
        }

        /* ── battery SoC bar ───────────────────────────── */
        .soc-bg {
          fill: #333;
          rx: 3;
          ry: 3;
        }
        .soc-fill {
          rx: 3;
          ry: 3;
          transition: width 0.5s ease;
        }
        .soc-text {
          font-size: 11px;
          font-weight: 600;
          fill: ${COLORS.text};
          text-anchor: middle;
          dominant-baseline: central;
          font-family: var(--ha-card-header-font-family, inherit);
        }

        /* ── node circles ──────────────────────────────── */
        .node-circle {
          fill: none;
          stroke-width: 2;
          opacity: 0.25;
        }
        .node-circle.active {
          opacity: 0.6;
        }

        @keyframes flowForward {
          0%   { offset-distance: 0%; opacity: 1; }
          90%  { opacity: 1; }
          100% { offset-distance: 100%; opacity: 0; }
        }
        @keyframes flowReverse {
          0%   { offset-distance: 100%; opacity: 1; }
          10%  { opacity: 1; }
          100% { offset-distance: 0%; opacity: 0; }
        }
      </style>

      <ha-card>
        ${this._config.title ? `<div class="card-header">${this._config.title}</div>` : ""}
        <div class="flow-container">
          <svg viewBox="0 0 500 300" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <!-- Flow line paths (used for dot motion) -->
              <path id="path-solar-home" d="M 250,75 L 250,195" />
              <path id="path-grid-home"  d="M 105,165 L 205,165" />
              <path id="path-batt-home"  d="M 395,165 L 295,165" />
            </defs>

            <!-- ── FLOW LINES ───────────────────────────── -->
            <use href="#path-solar-home" class="flow-line" id="line-solar-home"
                 stroke="${COLORS.solar}" />
            <use href="#path-grid-home" class="flow-line" id="line-grid-home"
                 stroke="${COLORS.inactive}" />
            <use href="#path-batt-home" class="flow-line" id="line-batt-home"
                 stroke="${COLORS.inactive}" />

            <!-- ── ANIMATED DOTS ────────────────────────── -->
            <!-- Solar → Home -->
            <circle class="flow-dot" id="dot-solar-1" fill="${COLORS.solar}">
              <animateMotion dur="1.5s" repeatCount="indefinite" keyPoints="0;1" keyTimes="0;1" calcMode="linear">
                <mpath href="#path-solar-home"/>
              </animateMotion>
            </circle>
            <circle class="flow-dot" id="dot-solar-2" fill="${COLORS.solar}">
              <animateMotion dur="1.5s" repeatCount="indefinite" begin="0.5s" keyPoints="0;1" keyTimes="0;1" calcMode="linear">
                <mpath href="#path-solar-home"/>
              </animateMotion>
            </circle>
            <circle class="flow-dot" id="dot-solar-3" fill="${COLORS.solar}">
              <animateMotion dur="1.5s" repeatCount="indefinite" begin="1s" keyPoints="0;1" keyTimes="0;1" calcMode="linear">
                <mpath href="#path-solar-home"/>
              </animateMotion>
            </circle>

            <!-- Grid ↔ Home -->
            <circle class="flow-dot" id="dot-grid-1" fill="${COLORS.grid_consume}">
              <animateMotion dur="1.5s" repeatCount="indefinite" id="anim-grid-1">
                <mpath href="#path-grid-home"/>
              </animateMotion>
            </circle>
            <circle class="flow-dot" id="dot-grid-2" fill="${COLORS.grid_consume}">
              <animateMotion dur="1.5s" repeatCount="indefinite" begin="0.5s" id="anim-grid-2">
                <mpath href="#path-grid-home"/>
              </animateMotion>
            </circle>
            <circle class="flow-dot" id="dot-grid-3" fill="${COLORS.grid_consume}">
              <animateMotion dur="1.5s" repeatCount="indefinite" begin="1s" id="anim-grid-3">
                <mpath href="#path-grid-home"/>
              </animateMotion>
            </circle>

            <!-- Battery ↔ Home -->
            <circle class="flow-dot" id="dot-batt-1" fill="${COLORS.battery_charge}">
              <animateMotion dur="1.5s" repeatCount="indefinite" id="anim-batt-1">
                <mpath href="#path-batt-home"/>
              </animateMotion>
            </circle>
            <circle class="flow-dot" id="dot-batt-2" fill="${COLORS.battery_charge}">
              <animateMotion dur="1.5s" repeatCount="indefinite" begin="0.5s" id="anim-batt-2">
                <mpath href="#path-batt-home"/>
              </animateMotion>
            </circle>
            <circle class="flow-dot" id="dot-batt-3" fill="${COLORS.battery_charge}">
              <animateMotion dur="1.5s" repeatCount="indefinite" begin="1s" id="anim-batt-3">
                <mpath href="#path-batt-home"/>
              </animateMotion>
            </circle>

            <!-- ── NODE: SOLAR (top centre) ─────────────── -->
            <circle class="node-circle" id="circle-solar" cx="250" cy="45"
                    r="32" stroke="${COLORS.solar}" />
            <text class="node-icon" x="250" y="45">☀️</text>
            <text class="node-label" x="250" y="85">Solar</text>
            <text class="node-value" id="val-solar" x="250" y="100">—</text>

            <!-- ── NODE: HOME (centre) ──────────────────── -->
            <circle class="node-circle active" cx="250" cy="165"
                    r="36" stroke="${COLORS.house}" />
            <text class="node-icon" x="250" y="163">🏠</text>
            <text class="node-label" x="250" y="210">Home</text>
            <text class="node-value" id="val-house" x="250" y="225">—</text>

            <!-- ── NODE: GRID (left) ────────────────────── -->
            <circle class="node-circle" id="circle-grid" cx="75" cy="165"
                    r="32" stroke="${COLORS.grid_consume}" />
            <text class="node-icon" x="75" y="163">⚡</text>
            <text class="node-label" x="75" y="205">Grid</text>
            <text class="node-value" id="val-grid" x="75" y="220">—</text>
            <text class="node-sub"   id="lbl-grid" x="75" y="235"></text>

            <!-- ── NODE: BATTERY (right) ────────────────── -->
            <circle class="node-circle" id="circle-batt" cx="425" cy="165"
                    r="32" stroke="${COLORS.battery_charge}" />
            <text class="node-icon" x="425" y="163">🔋</text>
            <text class="node-label" x="425" y="205">Battery</text>
            <text class="node-value" id="val-batt" x="425" y="220">—</text>
            <text class="node-sub"   id="lbl-batt" x="425" y="235"></text>

            <!-- ── BATTERY SOC BAR ──────────────────────── -->
            <rect class="soc-bg" x="393" y="250" width="64" height="14" />
            <rect class="soc-fill" id="soc-bar" x="393" y="250"
                  width="0" height="14" fill="${COLORS.battery_charge}" />
            <text class="soc-text" id="soc-text" x="425" y="257">—</text>
          </svg>
        </div>
      </ha-card>
    `;
    }

    /* --- update values from hass ----------------------------------------- */

    _updateValues() {
        if (!this._hass || !this.shadowRoot) return;
        const root = this.shadowRoot;
        const c = this._config;
        const h = this._hass;

        // Read raw state values
        const solar = stateValue(h, c.solar_entity); // W  (positive = producing)
        const grid = stateValue(h, c.grid_entity); // W  (positive = consuming, negative = feeding)
        const battery = stateValue(h, c.battery_entity); // W  (positive = discharging, negative = charging)
        const soc = stateValue(h, c.battery_soc_entity); // %
        const house = stateValue(h, c.house_entity); // W  (positive = consuming)

        // ── Update value text ───────────────────────────────
        const setTxt = (id, val) => {
            const el = root.getElementById(id);
            if (el) el.textContent = this._fmt(val);
        };
        setTxt("val-solar", solar);
        setTxt("val-house", house);
        setTxt("val-grid", grid !== null ? Math.abs(grid) : null);
        setTxt("val-batt", battery !== null ? Math.abs(battery) : null);

        // ── Grid label (importing / exporting) ──────────────
        const lblGrid = root.getElementById("lbl-grid");
        if (lblGrid) {
            if (grid === null || grid === 0) lblGrid.textContent = "";
            else if (grid > 0) lblGrid.textContent = "importing";
            else lblGrid.textContent = "exporting";
        }

        // ── Battery label (charging / discharging) ──────────
        const lblBatt = root.getElementById("lbl-batt");
        if (lblBatt) {
            if (battery === null || battery === 0) lblBatt.textContent = "";
            else if (battery > 0) lblBatt.textContent = "discharging";
            else lblBatt.textContent = "charging";
        }

        // ── Battery SoC bar ─────────────────────────────────
        const socBar = root.getElementById("soc-bar");
        const socText = root.getElementById("soc-text");
        if (socBar && socText) {
            const pct = soc !== null ? Math.max(0, Math.min(100, soc)) : 0;
            socBar.setAttribute("width", String((pct / 100) * 64));
            socText.textContent = soc !== null ? `${Math.round(soc)}%` : "—";
            // colour by level
            if (pct <= 20) socBar.setAttribute("fill", "#e74c3c");
            else if (pct <= 50) socBar.setAttribute("fill", "#f39c12");
            else socBar.setAttribute("fill", COLORS.battery_charge);
        }

        // ── Animate flows ───────────────────────────────────

        // Solar → Home
        const solarActive = solar !== null && solar > 10;
        this._toggleDots(
            root,
            ["dot-solar-1", "dot-solar-2", "dot-solar-3"],
            solarActive,
        );
        this._toggleLine(root, "line-solar-home", solarActive);
        this._toggleCircle(root, "circle-solar", solarActive);

        // Grid ↔ Home  (positive = import = grid→home; negative = export = home→grid)
        const gridActive = grid !== null && Math.abs(grid) > 10;
        const gridImporting = grid > 0;
        this._toggleDots(
            root,
            ["dot-grid-1", "dot-grid-2", "dot-grid-3"],
            gridActive,
        );
        this._toggleLine(root, "line-grid-home", gridActive);
        this._toggleCircle(root, "circle-grid", gridActive);

        // Set grid dot direction & colour
        const gridColor = gridImporting
            ? COLORS.grid_consume
            : COLORS.grid_feedin;
        ["dot-grid-1", "dot-grid-2", "dot-grid-3"].forEach((id) => {
            const dot = root.getElementById(id);
            if (dot) dot.setAttribute("fill", gridColor);
        });
        const lineGrid = root.getElementById("line-grid-home");
        if (lineGrid)
            lineGrid.setAttribute(
                "stroke",
                gridActive ? gridColor : COLORS.inactive,
            );
        // Direction: import = forward (grid→home), export = reverse (home→grid)
        this._setDotDirection(
            root,
            ["anim-grid-1", "anim-grid-2", "anim-grid-3"],
            gridImporting ? "0;1" : "1;0",
        );

        // Battery ↔ Home  (positive = discharge = batt→home; negative = charge = home→batt)
        const battActive = battery !== null && Math.abs(battery) > 10;
        const battDischarging = battery > 0;
        this._toggleDots(
            root,
            ["dot-batt-1", "dot-batt-2", "dot-batt-3"],
            battActive,
        );
        this._toggleLine(root, "line-batt-home", battActive);
        this._toggleCircle(root, "circle-batt", battActive);

        const battColor = battDischarging
            ? COLORS.battery_discharge
            : COLORS.battery_charge;
        ["dot-batt-1", "dot-batt-2", "dot-batt-3"].forEach((id) => {
            const dot = root.getElementById(id);
            if (dot) dot.setAttribute("fill", battColor);
        });
        const lineBatt = root.getElementById("line-batt-home");
        if (lineBatt)
            lineBatt.setAttribute(
                "stroke",
                battActive ? battColor : COLORS.inactive,
            );
        // Direction: discharge = forward (batt→home), charge = reverse (home→batt)
        this._setDotDirection(
            root,
            ["anim-batt-1", "anim-batt-2", "anim-batt-3"],
            battDischarging ? "0;1" : "1;0",
        );
    }

    /* --- animation helpers ---------------------------------------------- */

    _toggleDots(root, ids, active) {
        ids.forEach((id) => {
            const dot = root.getElementById(id);
            if (dot) {
                dot.classList.toggle("active", active);
                dot.setAttribute("r", active ? "4" : "0");
            }
        });
    }

    _toggleLine(root, id, active) {
        const line = root.getElementById(id);
        if (line) line.classList.toggle("active", active);
    }

    _toggleCircle(root, id, active) {
        const circle = root.getElementById(id);
        if (circle) circle.classList.toggle("active", active);
    }

    _setDotDirection(root, animIds, keyPoints) {
        animIds.forEach((id) => {
            const anim = root.getElementById(id);
            if (anim) anim.setAttribute("keyPoints", keyPoints);
        });
    }
}

/* ─── register ─────────────────────────────────────────────────────────── */

try {
    if (!customElements.get("alphaess-power-flow-card")) {
        customElements.define(
            "alphaess-power-flow-card",
            AlphaESSPowerFlowCard,
        );
        console.debug(
            "[alphaess-card] Defined custom element: alphaess-power-flow-card",
        );
    } else {
        console.warn(
            "[alphaess-card] alphaess-power-flow-card already defined, skipping",
        );
    }
} catch (err) {
    console.error(
        "[alphaess-card] Failed to define alphaess-power-flow-card:",
        err,
    );
}

try {
    window.customCards = window.customCards || [];
    if (
        !window.customCards.some((c) => c.type === "alphaess-power-flow-card")
    ) {
        window.customCards.push({
            type: "alphaess-power-flow-card",
            name: "AlphaESS Power Flow",
            preview: true,
            description:
                "Real-time power flow visualisation for AlphaESS inverters showing solar, grid, battery and home.",
            documentationURL:
                "https://github.com/Poshy163/homeassistant-alphaESS-modbus",
        });
    }
} catch (err) {
    console.error("[alphaess-card] Failed to register card in picker:", err);
}

console.info(
    `%c  ALPHAESS-POWER-FLOW-CARD  %c  v${CARD_VERSION}  `,
    "color: orange; font-weight: bold; background: #1c1c1c",
    "color: white; font-weight: bold; background: #333",
);
