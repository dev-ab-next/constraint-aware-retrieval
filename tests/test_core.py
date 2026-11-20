import math

import numpy as np
import pytest

from car.corpus import Precondition, load_corpus
from car.eval.metrics import query_metrics
from car.generate.fleet import generate_fleet
from car.generate.queries import build
from car.retrieve.pipeline import rrf
from car.telemetry import device_state
from car.verify.check import Verdict, check_precondition, check_procedure

CORPUS = {p.id: p for p in load_corpus()}


def state(**kv):
    """Build a state where every key is metric__window."""
    return {tuple(k.split("__")): float(v) for k, v in kv.items()}


def test_corpus_loads_and_ids_unique():
    assert len(CORPUS) == 26
    assert all(p.text for p in CORPUS.values())


@pytest.mark.parametrize("op,value,expected", [
    (">=", 3, Verdict.PASS), (">=", 4, Verdict.FAIL), ("<", 4, Verdict.PASS),
    ("==", 3, Verdict.PASS), ("==", 0, Verdict.FAIL),
])
def test_check_precondition_ops(op, value, expected):
    s = state(ecc_uncorrected__24h=3)
    assert check_precondition(Precondition("ecc_uncorrected", "24h", op, value), s) is expected


def test_missing_value_is_unknown_not_fail():
    s = state(ecc_uncorrected__24h=math.nan)
    assert check_precondition(Precondition("ecc_uncorrected", "24h", ">=", 1), s) is Verdict.UNKNOWN


def test_fail_beats_unknown():
    # PROC-003: uncorrected >= 1 and uncontained == 0
    s = state(ecc_uncorrected__24h=0, ecc_uncontained__24h=math.nan)
    assert check_procedure(CORPUS["PROC-003"], "class_a", s) is Verdict.FAIL


def test_device_class_mismatch_fails():
    s = state(ecc_uncorrected__24h=2, ecc_uncontained__24h=0)
    assert check_procedure(CORPUS["PROC-003"], "class_a", s) is Verdict.PASS
    assert check_procedure(CORPUS["PROC-003"], "class_b", s) is Verdict.FAIL


def test_contained_vs_uncontained_are_exclusive():
    s = state(ecc_uncorrected__24h=2, ecc_uncontained__24h=1)
    assert check_procedure(CORPUS["PROC-003"], "class_a", s) is Verdict.FAIL
    assert check_procedure(CORPUS["PROC-004"], "class_a", s) is Verdict.PASS


def test_seven_day_window_sums_counts():
    rng = np.random.default_rng(0)
    tel = generate_fleet(2, 10, rng)
    tel.loc[(tel.device_id == "gpu-0000") & (tel.day == 5), "ecc_uncorrected"] = 2
    st = device_state(tel, "gpu-0000", 9)
    assert st[("ecc_uncorrected", "7d")] == 2
    assert st[("ecc_uncorrected", "24h")] == 0
    # day 5 falls outside the 7-day window ending on day 12 (days 6..12)
    assert device_state(tel, "gpu-0000", 9)[("ecc_uncorrected", "7d")] == 2
    tel2 = generate_fleet(2, 13, np.random.default_rng(0))
    tel2.loc[(tel2.device_id == "gpu-0000") & (tel2.day == 5), "ecc_uncorrected"] = 2
    assert device_state(tel2, "gpu-0000", 12)[("ecc_uncorrected", "7d")] == 0


def test_rrf_prefers_consistently_high_ranks():
    # "b" is 2nd and 1st; "a" is 1st and 3rd -> b wins; ties broken by id
    assert rrf([["a", "b", "c"], ["b", "c", "a"]])[0] == "b"
    assert rrf([["a", "b"], ["b", "a"]]) == ["a", "b"]


def test_metrics_violation_and_recall():
    qrel = {"specific_applicable": ["P1"], "general_applicable": ["G"],
            "verdicts": {"P1": "pass", "G": "pass", "X": "fail"}}
    m = query_metrics(["X", "P1", "G"], [False, False, False], qrel, 3)
    assert m["top1_violation"] == 1.0 and m["top1_correct"] == 0.0
    assert m["recall@3"] == 1.0
    assert m["violation_rate@3"] == pytest.approx(1 / 3)


def test_benchmark_build_is_deterministic_and_targets_apply():
    cfg = {"seed": 7, "n_devices": 300, "n_days": 30, "queries_per_category": 8}
    _, q1, r1 = build(cfg)
    _, q2, r2 = build(cfg)
    assert q1 == q2 and r1 == r2
    assert all(r["target"] in r["specific_applicable"] for r in r1)
