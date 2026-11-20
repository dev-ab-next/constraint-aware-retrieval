"""Constraint verification: check a procedure's preconditions against a device state.

Three-valued result:
  PASS    every precondition holds
  FAIL    at least one precondition is false (the procedure does not apply)
  UNKNOWN nothing is false, but at least one value needed to decide is missing
"""
from __future__ import annotations

import math
import operator
from enum import Enum

from car.corpus import Precondition, Procedure

OPS = {">=": operator.ge, ">": operator.gt, "<=": operator.le, "<": operator.lt, "==": operator.eq}


class Verdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


def check_precondition(pre: Precondition, state: dict[tuple[str, str], float]) -> Verdict:
    if pre.op not in OPS:
        raise ValueError(f"unsupported operator {pre.op!r}")
    value = state.get((pre.metric, pre.window), math.nan)
    if value is None or math.isnan(value):
        return Verdict.UNKNOWN
    return Verdict.PASS if OPS[pre.op](value, pre.value) else Verdict.FAIL


def check_procedure(proc: Procedure, device_class: str, state: dict[tuple[str, str], float],
                    preconditions: list[Precondition] | None = None) -> Verdict:
    """Verify a procedure for one device. `preconditions` overrides the procedure's own (used in ablations)."""
    if device_class not in proc.device_classes:
        return Verdict.FAIL
    pres = proc.preconditions if preconditions is None else preconditions
    verdicts = [check_precondition(p, state) for p in pres]
    if Verdict.FAIL in verdicts:
        return Verdict.FAIL
    if Verdict.UNKNOWN in verdicts:
        return Verdict.UNKNOWN
    return Verdict.PASS
