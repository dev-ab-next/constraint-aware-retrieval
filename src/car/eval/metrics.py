"""Per-query metrics. 'Violation' always means: the procedure's preconditions are FALSE for the device's
TRUE state (ground truth), regardless of what the retriever could observe."""
from __future__ import annotations

import math


def query_metrics(returned: list[str], flagged: list[bool], qrel: dict, k: int) -> dict:
    top = returned[:k]
    flags = flagged[:k]
    verdicts = qrel["verdicts"]
    specific = set(qrel["specific_applicable"])
    general = set(qrel["general_applicable"])
    violations = [verdicts[d] == "fail" for d in top]

    gains = [2 if d in specific else 1 if d in general else 0 for d in top]
    dcg = sum(g / math.log2(i + 2) for i, g in enumerate(gains))
    ideal = sorted([2] * len(specific) + [1] * len(general), reverse=True)[:k]
    idcg = sum(g / math.log2(i + 2) for i, g in enumerate(ideal))

    return {
        "top1_correct": float(bool(top) and top[0] in specific),
        "top1_violation": float(bool(top) and violations[0]),
        f"recall@{k}": len(specific & set(top)) / len(specific) if specific else math.nan,
        f"violation_rate@{k}": sum(violations) / len(top) if top else 0.0,
        f"any_violation@{k}": float(any(violations)),
        f"unflagged_violation@{k}": float(any(v and not f for v, f in zip(violations, flags))),
        f"flagged@{k}": float(any(flags)),
        f"ndcg@{k}": dcg / idcg if idcg else math.nan,
        "returned": len(top),
    }
