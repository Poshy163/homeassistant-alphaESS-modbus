"""DataUpdateCoordinator for the AlphaESS Modbus integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    B3_POWER_KEYS,
    B3_POWER_SCALE_CORRECTION,
    CONF_MODEL,
    CONF_POLL_FREQ,
    CORE_SENSOR_DESCRIPTIONS,
    DEFAULT_POLL_FREQ,
    DOMAIN,
    FAST_POLL_1S_KEYS,
    INTERNAL_REGISTER_DESCRIPTIONS,
    POLL_FREQUENCY_INTERVAL_SECONDS,
    RegisterType,
    SLOW_POLL_TARGET_SECONDS,
)
from .hub import AlphaESSModbusHub

_LOGGER = logging.getLogger(__name__)


def _int32_to_ip(value: int | float | None) -> str | None:
    """Convert a 32-bit integer (or float) to a dotted-quad IP string."""
    if value is None:
        return None
    try:
        v = int(value)
        return f"{(v >> 24) & 0xFF}.{(v >> 16) & 0xFF}.{(v >> 8) & 0xFF}.{v & 0xFF}"
    except Exception:  # noqa: BLE001
        return None


def _bms_version(raw: int | None) -> str | None:
    """Format BMS version: e.g. 312 → V3.12."""
    if raw is None:
        return None
    return f"V{raw // 100}.{raw % 100:02d}"


def _format_time_period(
    start_h: int | None,
    start_m: int | None,
    stop_h: int | None,
    stop_m: int | None,
) -> str:
    """Format a charging/discharging time period as 'H:MM - H:MM'."""
    if any(v is None for v in (start_h, start_m, stop_h, stop_m)):
        return "unavailable"
    return f"{int(start_h)}:{int(start_m):02d} - {int(stop_h)}:{int(stop_m):02d}"


def _decode_bcd_datetime(
    yymm: int | None,
    ddhh: int | None,
    mmss: int | None,
) -> tuple[str | None, str | None]:
    """Decode BCD-encoded date/time registers into date and time strings."""
    if any(v is None for v in (yymm, ddhh, mmss)):
        return None, None
    yy = (yymm >> 8) & 0xFF
    mm = yymm & 0xFF
    dd = (ddhh >> 8) & 0xFF
    hh = ddhh & 0xFF
    mi = (mmss >> 8) & 0xFF
    ss = mmss & 0xFF
    date_str = f"20{yy:02d}-{mm:02d}-{dd:02d}"
    time_str = f"{hh:02d}:{mi:02d}:{ss:02d}"
    return date_str, time_str


class AlphaESSModbusCoordinator(DataUpdateCoordinator[dict[str, float | str | None]]):
    """Polls all Modbus registers and computes derived values."""

    def __init__(self, hass: HomeAssistant, hub: AlphaESSModbusHub) -> None:
        self.hub = hub
        poll_freq = str(hub.get_config_value(CONF_POLL_FREQ, DEFAULT_POLL_FREQ) or DEFAULT_POLL_FREQ)

        # Backward compatibility for older entries: assume B3/B3-PLUS users are on slower links.
        model = str(hub.get_config_value(CONF_MODEL, "") or "")
        if poll_freq not in POLL_FREQUENCY_INTERVAL_SECONDS:
            poll_freq = "slow" if model in ("SMILE-B3", "SMILE-B3-PLUS") else DEFAULT_POLL_FREQ

        interval_seconds = POLL_FREQUENCY_INTERVAL_SECONDS[poll_freq]
        slow_poll_every = max(1, round(SLOW_POLL_TARGET_SECONDS / interval_seconds))
        # In fast mode (1s coordinator), only the explicit power sensors are read
        # every second. All other regular sensors are throttled to every 5 cycles.
        regular_poll_every = max(1, round(5 / interval_seconds)) if poll_freq == "fast" else 1

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval_seconds),
        )
        self._model = model
        self._poll_freq = poll_freq
        self._slow_poll_every = slow_poll_every
        self._regular_poll_every = regular_poll_every
        self._poll_cycle: int = 0

        _LOGGER.debug(
            "AlphaESS polling profile selected: poll_freq=%s interval=%ss slow_poll_every=%s model=%s",
            self._poll_freq,
            interval_seconds,
            self._slow_poll_every,
            self._model,
        )

    def _apply_model_adjustment(self, key: str, value: float) -> float:
        """Apply model-specific scaling corrections where required."""
        if self._model in ("SMILE-B3", "SMILE-B3-PLUS") and key in B3_POWER_KEYS:
            return value * B3_POWER_SCALE_CORRECTION
        return value

    async def _async_update_data(self) -> dict[str, float | str | None]:
        """Read Modbus registers and compute derived values."""
        data: dict[str, float | str | None] = {}

        self._poll_cycle += 1
        # First refresh reads all sensors so entities are immediately available.
        is_first_refresh = self._poll_cycle == 1
        is_slow_cycle = is_first_refresh or ((self._poll_cycle % self._slow_poll_every) == 0)
        is_regular_cycle = is_first_refresh or ((self._poll_cycle % self._regular_poll_every) == 0)

        # ── Read raw Modbus registers ────────────────────────────────
        for desc in (*CORE_SENSOR_DESCRIPTIONS, *INTERNAL_REGISTER_DESCRIPTIONS):
            # Skip slow-poll sensors unless this is a slow cycle
            if desc.slow_poll and not is_slow_cycle:
                # Preserve last known value from coordinator data
                if self.data and desc.key in self.data:
                    data[desc.key] = self.data[desc.key]
                else:
                    data[desc.key] = None
                continue

            if (
                self._poll_freq == "fast"
                and desc.key not in FAST_POLL_1S_KEYS
                and not is_regular_cycle
            ):
                # In fast mode, only whitelist keys update every cycle.
                if self.data and desc.key in self.data:
                    data[desc.key] = self.data[desc.key]
                else:
                    data[desc.key] = None
                continue

            try:
                raw = await self.hub.async_read_value(
                    desc.address, desc.register_type,
                    register_count=desc.register_count,
                )
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug(
                    "Error reading %s (0x%04X): %s",
                    desc.key,
                    desc.address,
                    err,
                )
                data[desc.key] = None
                continue

            if raw is None:
                data[desc.key] = None
                continue

            # STRING registers are already decoded as str
            if desc.register_type == RegisterType.STRING:
                data[desc.key] = raw
                continue

            # Apply scale and offset
            value = raw * desc.scale + desc.offset
            value = self._apply_model_adjustment(desc.key, value)
            if desc.precision is not None:
                value = round(value, desc.precision)
            data[desc.key] = value

        # ── Compute derived / template sensors ───────────────────────
        try:
            self._compute_derived(data)
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Error computing derived sensors", exc_info=True)

        return data

    # ──────────────────── Derived value calculation ──────────────────

    @staticmethod
    def _compute_derived(data: dict[str, float | str | None]) -> None:
        """Calculate template / computed sensors from raw data."""

        def _g(key: str) -> float:
            """Get a numeric value, defaulting to 0."""
            v = data.get(key)
            return float(v) if v is not None else 0.0

        # Current PV production = PV1 + PV2 + PV3 + PV4 + PV Meter
        pv_prod = (
            _g("pv1_power")
            + _g("pv2_power")
            + _g("pv3_power")
            + _g("pv4_power")
            + _g("active_power_pv_meter")
        )
        data["current_pv_production"] = round(pv_prod)

        # Current house load = max(0, PV + Battery + Grid)
        house_load = max(0.0, pv_prod + _g("power_battery") + _g("power_grid"))
        data["current_house_load"] = round(house_load)

        # Total house load = PV total + grid consumption - grid feed
        total_house = (
            _g("total_energy_from_pv")
            + _g("total_energy_consumption_from_grid_meter")
            - _g("total_energy_feed_to_grid_meter")
        )
        data["total_house_load"] = round(max(0.0, total_house), 2)

        # Excess power = max(0, PV production − house load)
        data["excess_power"] = round(max(0.0, pv_prod - house_load))

        # Clipping = max(0, PV DC production − grid inverter AC capacity)
        pv_capacity = _g("pv_capacity_grid_inverter")
        data["clipping"] = round(max(0.0, pv_prod - pv_capacity)) if pv_capacity > 0 else 0

        # Charging period 1 & 2
        data["charging_period_1"] = _format_time_period(
            data.get("charging_period_1_start_hour"),
            data.get("charging_period_1_start_minute"),
            data.get("charging_period_1_stop_hour"),
            data.get("charging_period_1_stop_minute"),
        )
        data["charging_period_2"] = _format_time_period(
            data.get("charging_period_2_start_hour"),
            data.get("charging_period_2_start_minute"),
            data.get("charging_period_2_stop_hour"),
            data.get("charging_period_2_stop_minute"),
        )
        data["discharging_period_1"] = _format_time_period(
            data.get("discharging_period_1_start_hour"),
            data.get("discharging_period_1_start_minute"),
            data.get("discharging_period_1_stop_hour"),
            data.get("discharging_period_1_stop_minute"),
        )
        data["discharging_period_2"] = _format_time_period(
            data.get("discharging_period_2_start_hour"),
            data.get("discharging_period_2_start_minute"),
            data.get("discharging_period_2_stop_hour"),
            data.get("discharging_period_2_stop_minute"),
        )

        # IP / subnet / gateway normalised
        data["local_ip_normalised"] = _int32_to_ip(
            data.get("local_ip") if isinstance(data.get("local_ip"), (int, float)) else None  # type: ignore[arg-type]
        )
        data["subnet_mask_normalised"] = _int32_to_ip(
            data.get("subnet_mask") if isinstance(data.get("subnet_mask"), (int, float)) else None  # type: ignore[arg-type]
        )
        data["gateway_normalised"] = _int32_to_ip(
            data.get("gateway") if isinstance(data.get("gateway"), (int, float)) else None  # type: ignore[arg-type]
        )

        # BMS version normalised
        bms_raw = data.get("bms_version")
        data["bms_version_normalised"] = _bms_version(
            int(bms_raw) if bms_raw is not None else None
        )

        # EMS version normalised
        ems_h = data.get("ems_version_high")
        ems_m = data.get("ems_version_middle")
        ems_l = data.get("ems_version_low")
        if all(v is not None for v in (ems_h, ems_m, ems_l)):
            data["ems_version_normalised"] = (
                f"V{int(ems_h)}.{int(ems_m)}.{int(ems_l)}"  # type: ignore[arg-type]
            )
        else:
            data["ems_version_normalised"] = None

        # System date / time
        date_str, time_str = _decode_bcd_datetime(
            int(data.get("system_time_yymm", 0) or 0),
            int(data.get("system_time_ddhh", 0) or 0),
            int(data.get("system_time_mmss", 0) or 0),
        )
        data["system_date"] = date_str
        data["system_time"] = time_str

        # Battery full indicator
        status = data.get("battery_status")
        data["battery_full"] = "Yes" if (status is not None and int(status) == 1) else "No"

        # ── kW sensors for power diagrams (W ÷ 1000) ────────────────
        data["current_house_load_kw"] = round(house_load / 1000, 2)
        data["current_pv_production_kw"] = round(pv_prod / 1000, 2)
        data["power_grid_kw"] = round(_g("power_grid") / 1000, 2)
        data["power_grid_consumption_kw"] = round(max(0.0, _g("power_grid")) / 1000, 2)
        data["power_grid_feed_in_kw"] = round(max(0.0, -_g("power_grid")) / 1000, 2)
        data["power_battery_kw"] = round(_g("power_battery") / 1000, 2)
        data["pv1_power_kw"] = round(_g("pv1_power") / 1000, 2)
        data["pv2_power_kw"] = round(_g("pv2_power") / 1000, 2)
        data["excess_power_kw"] = round(max(0.0, pv_prod - house_load) / 1000, 2)
