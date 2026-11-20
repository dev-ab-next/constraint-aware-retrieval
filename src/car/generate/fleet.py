"""Generate healthy background telemetry for a synthetic GPU fleet.

The fleet is fictional. Values are chosen to look plausible, not to match any vendor's hardware.
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

CLASS_A_ONLY = ("ecc_uncontained", "remap_pending", "remap_failure")


def generate_fleet(n_devices: int, n_days: int, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for i in range(n_devices):
        device_id = f"gpu-{i:04d}"
        device_class = "class_a" if i % 2 == 0 else "class_b"
        base_temp = rng.uniform(58, 72)
        for day in range(n_days):
            r = {
                "device_id": device_id,
                "device_class": device_class,
                "day": day,
                "temp_max_c": round(base_temp + rng.normal(0, 2.5), 1),
                "thermal_throttle_events": 0,
                # a small share of healthy devices see a few corrected errors on a given day
                "ecc_corrected": int(rng.integers(1, 15)) if rng.random() < 0.08 else 0,
                "ecc_uncorrected": 0,
                "ecc_uncontained": 0,
                "remap_pending": 0,
                "remap_failure": 0,
                "pcie_replay": int(rng.integers(1, 5)) if rng.random() < 0.05 else 0,
                "pcie_link_width": 16,
                "link_crc_errors": int(rng.integers(1, 10)) if rng.random() < 0.05 else 0,
                "links_down": 0,
                "power_brake_events": 0,
                "psu_degraded": 0,
                "host_dimm_corrected": 0,
                "host_dimm_uncorrected": 0,
            }
            r["temp_max_c"] = min(r["temp_max_c"], 79.0)
            if device_class == "class_b":
                for m in CLASS_A_ONLY:
                    r[m] = math.nan
            rows.append(r)
    return pd.DataFrame(rows)
