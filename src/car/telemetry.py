"""Telemetry schema and window aggregation.

Telemetry is stored as one row per device per day. A *device state* is the set of values that
preconditions are evaluated against: each metric aggregated over a window ("now", "24h", "7d")
ending on the query day. Missing values (NaN) stay missing so the verifier can report "unknown".
"""
from __future__ import annotations

import math

import pandas as pd

# metric -> (kind, aggregation over 7d)
METRICS: dict[str, tuple[str, str]] = {
    "temp_max_c": ("gauge", "max"),
    "thermal_throttle_events": ("count", "sum"),
    "ecc_corrected": ("count", "sum"),
    "ecc_uncorrected": ("count", "sum"),
    "ecc_uncontained": ("count", "sum"),   # class A only; NaN on class B
    "remap_pending": ("flag", "max"),      # class A only; NaN on class B
    "remap_failure": ("flag", "max"),      # class A only; NaN on class B
    "pcie_replay": ("count", "sum"),
    "pcie_link_width": ("gauge", "min"),
    "link_crc_errors": ("count", "sum"),
    "links_down": ("gauge", "max"),
    "power_brake_events": ("count", "sum"),
    "psu_degraded": ("flag", "max"),
    "host_dimm_corrected": ("count", "sum"),
    "host_dimm_uncorrected": ("count", "sum"),
}
WINDOWS = ("now", "24h", "7d")


def _agg(series: pd.Series, how: str) -> float:
    if series.isna().all():
        return math.nan
    if series.isna().any():  # a partially missing window cannot be trusted
        return math.nan
    return float(getattr(series, how)())


def device_state(telemetry: pd.DataFrame, device_id: str, day: int) -> dict[tuple[str, str], float]:
    """Return {(metric, window): value} for a device on a given day."""
    rows = telemetry[(telemetry.device_id == device_id) & (telemetry.day <= day) & (telemetry.day > day - 7)]
    rows = rows.sort_values("day")
    if rows.empty or rows.day.iloc[-1] != day:
        raise KeyError(f"no telemetry for {device_id} on day {day}")
    today = rows.iloc[-1]
    state: dict[tuple[str, str], float] = {}
    for m, (_, how) in METRICS.items():
        v = float(today[m])
        state[(m, "now")] = v
        state[(m, "24h")] = v
        state[(m, "7d")] = _agg(rows[m], how)
    return state


def describe_state(device_id: str, device_class: str, state: dict[tuple[str, str], float]) -> str:
    """Flatten a device state into text, the way a typical RAG pipeline would put telemetry in a prompt."""
    def fmt(v: float) -> str:
        return "n/a" if math.isnan(v) else (str(int(v)) if float(v).is_integer() else f"{v:.1f}")

    last24 = ", ".join(f"{m}={fmt(state[(m, '24h')])}" for m in METRICS)
    last7 = ", ".join(f"{m}={fmt(state[(m, '7d')])}" for m, (k, _) in METRICS.items() if k == "count")
    return f"Device {device_id} ({device_class}). Last 24h: {last24}. Last 7d: {last7}."
