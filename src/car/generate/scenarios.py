"""Fault scenarios injected into the synthetic fleet, and the questions an operator might ask about them.

Each scenario changes one device's telemetry so that a *target* procedure applies, then produces a
natural-language question. Questions describe the symptom the way an operator would ("memory errors",
"running hot"); the decisive numbers live in the telemetry, sometimes repeated in the question.

Ground-truth labels are NOT taken from the target: after injection, every procedure is evaluated against
the device's true state (see queries.py). The target is only a sanity check that the scenario worked.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

Setter = Callable[[int, str, float], None]  # (day_offset <= 0, metric, value)


@dataclass(frozen=True)
class Scenario:
    name: str
    category: str
    topic: str
    target: str
    device_class: str | None  # required class, or None for any
    inject: Callable[[np.random.Generator, Setter], dict]
    questions: tuple[str, ...]


def _ri(rng, lo, hi):  # inclusive
    return int(rng.integers(lo, hi + 1))


MEM_Q = (
    "{dev} is reporting GPU memory errors. What should we do?",
    "We're seeing ECC errors on {dev}. How should we handle it?",
    "What is the right response to the memory errors on {dev}?",
    "{dev} shows ECC memory errors in its health check. Next steps?",
)
THERM_Q = (
    "{dev} is running hot. What should we do?",
    "Temperature alert on {dev}. How should we respond?",
    "{dev} has a thermal warning. What's the procedure?",
)
PCIE_Q = (
    "{dev} is reporting PCIe errors. What should we do?",
    "We see PCIe replay errors on {dev}. How do we handle this?",
    "Is there a problem with the PCIe link on {dev}? What should we do?",
)
LINK_Q = (
    "{dev} has GPU interconnect errors. What should we do?",
    "Multi-GPU jobs on {dev}'s node are slow and the interconnect shows errors. Next steps?",
    "How should we handle the GPU link errors on {dev}?",
)
POWER_Q = (
    "{dev} has a power-related alert. What should we do?",
    "We see power problems on the node with {dev}. How should we respond?",
)


SCENARIOS: list[Scenario] = []


def scenario(name, category, topic, target, device_class, questions):
    def deco(fn):
        SCENARIOS.append(Scenario(name, category, topic, target, device_class, fn, questions))
        return fn
    return deco


# ---------- numerical_threshold: same symptom, the right procedure depends on a number ----------
@scenario("ecc_corrected_low", "numerical_threshold", "gpu_memory_ecc", "PROC-001", None,
          MEM_Q + ("{dev} logged {n} corrected ECC errors today. Do we need to act?",))
def _(rng, s):
    n = _ri(rng, 20, 95); s(0, "ecc_corrected", n); return {"n": n}


@scenario("ecc_corrected_high", "numerical_threshold", "gpu_memory_ecc", "PROC-002", None,
          MEM_Q + ("{dev} logged {n} corrected ECC errors today. Do we need to act?",))
def _(rng, s):
    n = _ri(rng, 105, 600); s(0, "ecc_corrected", n); return {"n": n}


@scenario("temp_warning", "numerical_threshold", "thermal", "PROC-010", None,
          THERM_Q + ("{dev} peaked at {n} °C today. What should we do?",))
def _(rng, s):
    n = _ri(rng, 83, 89); s(0, "temp_max_c", n); return {"n": n}


@scenario("temp_critical", "numerical_threshold", "thermal", "PROC-011", None,
          THERM_Q + ("{dev} peaked at {n} °C today. What should we do?",))
def _(rng, s):
    n = _ri(rng, 90, 97); s(0, "temp_max_c", n); s(0, "thermal_throttle_events", _ri(rng, 5, 40)); return {"n": n}


@scenario("pcie_replay_low", "numerical_threshold", "pcie", "PROC-014", None,
          PCIE_Q + ("{dev} had {n} PCIe replays in the last day. Is that a problem?",))
def _(rng, s):
    n = _ri(rng, 8, 45); s(0, "pcie_replay", n); return {"n": n}


@scenario("pcie_replay_high", "numerical_threshold", "pcie", "PROC-015", None,
          PCIE_Q + ("{dev} had {n} PCIe replays in the last day. Is that a problem?",))
def _(rng, s):
    n = _ri(rng, 60, 400); s(0, "pcie_replay", n); return {"n": n}


@scenario("crc_low", "numerical_threshold", "interconnect", "PROC-018", None,
          LINK_Q + ("{dev} reported {n} interconnect CRC errors today. Should we worry?",))
def _(rng, s):
    n = _ri(rng, 15, 90); s(0, "link_crc_errors", n); return {"n": n}


@scenario("crc_high", "numerical_threshold", "interconnect", "PROC-019", None,
          LINK_Q + ("{dev} reported {n} interconnect CRC errors today. Should we worry?",))
def _(rng, s):
    n = _ri(rng, 120, 900); s(0, "link_crc_errors", n); return {"n": n}


# ---------- error_type_contrast: similar wording, different kind of error ----------
@scenario("ecc_contained", "error_type_contrast", "gpu_memory_ecc", "PROC-003", "class_a",
          MEM_Q + ("{dev} hit an uncorrectable ECC error and a job crashed. What now?",))
def _(rng, s):
    s(0, "ecc_uncorrected", _ri(rng, 1, 3)); s(0, "ecc_uncontained", 0)
    s(0, "ecc_corrected", _ri(rng, 0, 30))
    if rng.random() < 0.5:
        s(0, "remap_pending", 1)
    return {}


@scenario("ecc_uncontained", "error_type_contrast", "gpu_memory_ecc", "PROC-004", "class_a",
          MEM_Q + ("{dev} hit an uncorrectable ECC error and a job crashed. What now?",))
def _(rng, s):
    n = _ri(rng, 1, 3); s(0, "ecc_uncorrected", n); s(0, "ecc_uncontained", _ri(rng, 1, n))
    s(0, "ecc_corrected", _ri(rng, 0, 30)); s(0, "remap_pending", 1)
    return {}


@scenario("remap_pending", "error_type_contrast", "gpu_memory_ecc", "PROC-007", "class_a",
          MEM_Q + ("{dev} says a memory row remap is involved. What should we do?",))
def _(rng, s):
    s(-_ri(rng, 1, 2), "ecc_corrected", _ri(rng, 20, 80)); s(0, "remap_pending", 1); s(0, "remap_failure", 0)
    return {}


@scenario("remap_failure", "error_type_contrast", "gpu_memory_ecc", "PROC-008", "class_a",
          MEM_Q + ("{dev} says a memory row remap is involved. What should we do?",))
def _(rng, s):
    s(0, "remap_failure", 1); s(0, "remap_pending", int(rng.random() < 0.5))
    s(-_ri(rng, 1, 3), "ecc_corrected", _ri(rng, 20, 80))
    return {}


@scenario("link_down", "error_type_contrast", "interconnect", "PROC-020", None, LINK_Q)
def _(rng, s):
    s(0, "links_down", _ri(rng, 1, 2)); s(0, "link_crc_errors", _ri(rng, 100, 800)); return {}


@scenario("power_brake", "error_type_contrast", "power", "PROC-022", None, POWER_Q)
def _(rng, s):
    s(0, "power_brake_events", _ri(rng, 1, 6)); return {}


@scenario("psu_degraded", "error_type_contrast", "power", "PROC-023", None, POWER_Q)
def _(rng, s):
    s(0, "psu_degraded", 1); return {}


# ---------- device_class: identical symptom, the right procedure depends on hardware class ----------
DEV_Q = MEM_Q + ("{dev} reported {n} uncorrectable ECC error(s) today. What should we do?",)


@scenario("ecc_uncorrected_class_b", "device_class", "gpu_memory_ecc", "PROC-005", "class_b", DEV_Q)
def _(rng, s):
    n = _ri(rng, 1, 4); s(0, "ecc_uncorrected", n); return {"n": n}


@scenario("ecc_uncorrected_class_a", "device_class", "gpu_memory_ecc", "PROC-003", "class_a", DEV_Q)
def _(rng, s):
    n = _ri(rng, 1, 4); s(0, "ecc_uncorrected", n); s(0, "ecc_uncontained", 0); return {"n": n}


# ---------- temporal: the condition was true earlier in the week but not today ----------
@scenario("ecc_uncorrected_past", "temporal", "gpu_memory_ecc", "PROC-006", None,
          MEM_Q + ("{dev} had uncorrectable memory errors earlier this week. Is anything still needed?",))
def _(rng, s):
    s(-_ri(rng, 2, 5), "ecc_uncorrected", _ri(rng, 1, 3)); return {}


@scenario("pcie_replay_past_high", "temporal", "pcie", "PROC-014", None,
          PCIE_Q + ("{dev} had a burst of PCIe replays a few days ago. What should we do now?",))
def _(rng, s):
    s(-_ri(rng, 2, 5), "pcie_replay", _ri(rng, 150, 600)); s(0, "pcie_replay", _ri(rng, 3, 20)); return {}


@scenario("crc_past_high", "temporal", "interconnect", "PROC-018", None,
          LINK_Q + ("{dev} had a spike of interconnect errors a few days ago. What should we do now?",))
def _(rng, s):
    s(-_ri(rng, 2, 5), "link_crc_errors", _ri(rng, 200, 900)); s(0, "link_crc_errors", _ri(rng, 5, 40)); return {}


@scenario("temp_past_critical", "temporal", "thermal", "PROC-010", None,
          THERM_Q + ("{dev} overheated earlier this week. What should we do now?",))
def _(rng, s):
    s(-_ri(rng, 2, 5), "temp_max_c", _ri(rng, 92, 97)); s(0, "temp_max_c", _ri(rng, 83, 88)); return {}


# ---------- distractor: the wording points to one topic, the telemetry to a neighbouring one ----------
@scenario("host_dimm_uncorrected", "distractor", "host_memory", "PROC-026", None,
          ("{dev}'s node is reporting memory errors. What should we do?",
           "There are uncorrectable memory errors on the server hosting {dev}. Next steps?"))
def _(rng, s):
    s(0, "host_dimm_uncorrected", _ri(rng, 1, 3)); return {}


@scenario("host_dimm_corrected", "distractor", "host_memory", "PROC-025", None,
          ("{dev}'s node is reporting memory errors. What should we do?",
           "There are corrected memory errors on the server hosting {dev}. Do we need to act?"))
def _(rng, s):
    s(0, "host_dimm_corrected", _ri(rng, 5, 60)); return {}


@scenario("throttle_normal_temp", "distractor", "thermal", "PROC-012", None, THERM_Q)
def _(rng, s):
    s(0, "thermal_throttle_events", _ri(rng, 3, 30)); s(0, "temp_max_c", _ri(rng, 62, 76)); return {}


@scenario("pcie_width_degraded", "distractor", "pcie", "PROC-016", None,
          ("Host-to-GPU transfers on {dev} are slow. What should we do?",) + PCIE_Q)
def _(rng, s):
    s(0, "pcie_link_width", float(rng.choice([4, 8]))); return {}


CATEGORIES = ("numerical_threshold", "error_type_contrast", "device_class", "temporal", "distractor")
