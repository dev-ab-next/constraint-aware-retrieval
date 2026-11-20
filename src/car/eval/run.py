"""Run the main comparison (C1-C5) and the two robustness ablations for C5.

Usage: python -m car.eval.run
Writes results/*.csv, results/*.md and results/per_query.jsonl.
"""
from __future__ import annotations

import json
import math
import platform
import time

import numpy as np
import pandas as pd
import yaml

from car import DATA_DIR, REPO_ROOT, RESULTS_DIR
from car.corpus import Precondition, load_corpus
from car.eval.metrics import query_metrics
from car.retrieve.pipeline import CONDITIONS, Retriever
from car.telemetry import METRICS, describe_state, device_state


def load_jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f]


def noisy_preconditions(procs, p: float, rng) -> dict[str, list[Precondition]]:
    """Simulate imperfect precondition extraction: each clause is dropped or has its threshold changed."""
    out = {}
    for proc in procs:
        clauses = []
        for c in proc.preconditions:
            if rng.random() >= p:
                clauses.append(c)
            elif rng.random() < 0.5:
                continue  # dropped
            else:
                new = 1.0 if c.value == 0 else float(max(1, round(c.value * rng.uniform(0.5, 1.5))))
                if new == c.value:
                    new = c.value + 1
                clauses.append(Precondition(c.metric, c.window, c.op, new))
        out[proc.id] = clauses
    return out


def with_missing(state: dict, p: float, rng) -> dict:
    """Simulate missing telemetry: each metric is missing (all windows) with probability p."""
    out = dict(state)
    for m in METRICS:
        if rng.random() < p:
            for w in ("now", "24h", "7d"):
                out[(m, w)] = math.nan
    return out


def summarize(rows: list[dict], keys: list[str]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    metric_cols = [c for c in df.columns if c not in keys + ["qid", "category"]]
    return df.groupby(keys)[metric_cols].mean().reset_index()


def main() -> None:
    cfg = yaml.safe_load(open(REPO_ROOT / "configs" / "experiments.yaml"))
    k = cfg["k"]
    procs = load_corpus()
    queries = load_jsonl(DATA_DIR / "queries" / "queries.jsonl")
    qrels = {q["qid"]: q for q in load_jsonl(DATA_DIR / "queries" / "qrels.jsonl")}
    tel = pd.read_csv(DATA_DIR / "telemetry" / "fleet.csv.gz")

    t0 = time.perf_counter()
    ret = Retriever(procs, cfg["embed_model"], cfg["rerank_model"], cfg["embed_query_prefix"],
                    cfg["rrf_k"], cfg["rerank_depth"])
    print(f"models loaded in {time.perf_counter() - t0:.1f}s")

    states, texts, cached_c4 = {}, {}, {}
    for q in queries:
        states[q["qid"]] = device_state(tel, q["device_id"], q["day"])
        texts[q["qid"]] = q["text"] + "\n" + describe_state(q["device_id"], q["device_class"], states[q["qid"]])

    # ---------------- main comparison ----------------
    rows, per_query = [], []
    for cond in CONDITIONS:
        ret.search(cond, texts[queries[0]["qid"]], queries[0]["device_class"], states[queries[0]["qid"]], k)  # warm-up
        for q in queries:
            qid = q["qid"]
            t = time.perf_counter()
            res = ret.search(cond, texts[qid], q["device_class"], states[qid], k)
            ms = (time.perf_counter() - t) * 1000
            m = query_metrics([r.id for r in res], [r.flagged for r in res], qrels[qid], k)
            rows.append({"condition": cond, "qid": qid, "category": q["category"], "latency_ms": ms, **m})
            per_query.append({"condition": cond, "qid": qid, "returned": [r.id for r in res],
                              "flagged": [r.flagged for r in res]})
        print(f"{cond} done")

    RESULTS_DIR.mkdir(exist_ok=True)
    main_df = summarize(rows, ["condition"])
    lat = pd.DataFrame(rows).groupby("condition")["latency_ms"].quantile([0.5, 0.95]).unstack()
    main_df["latency_p50_ms"] = main_df.condition.map(lat[0.5])
    main_df["latency_p95_ms"] = main_df.condition.map(lat[0.95])
    main_df = main_df.drop(columns=["latency_ms"])
    main_df.to_csv(RESULTS_DIR / "main.csv", index=False)
    cat_df = summarize(rows, ["condition", "category"]).drop(columns=["latency_ms"])
    cat_df.to_csv(RESULTS_DIR / "by_category.csv", index=False)
    with open(RESULTS_DIR / "per_query.jsonl", "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in per_query)

    # cache C4 rankings (full reranked list) for the ablations
    for q in queries:
        cached_c4[q["qid"]] = ret.candidates(texts[q["qid"]], q["device_class"])

    # ---------------- ablations (C5 only) ----------------
    abl_rows = []
    ab = cfg["ablations"]
    for kind, levels in (("noisy_preconditions", ab["noisy_preconditions"]),
                         ("missing_telemetry", ab["missing_telemetry"])):
        for p in [0.0] + list(levels):
            for seed in ab["seeds"]:
                rng = np.random.default_rng(seed)
                pres = noisy_preconditions(procs, p, rng) if kind == "noisy_preconditions" else None
                for q in queries:
                    qid = q["qid"]
                    state = with_missing(states[qid], p, rng) if kind == "missing_telemetry" else states[qid]
                    res = ret.verify(cached_c4[qid], q["device_class"], state, k, pres)
                    m = query_metrics([r.id for r in res], [r.flagged for r in res], qrels[qid], k)
                    abl_rows.append({"ablation": kind, "level": p, "seed": seed, "qid": qid,
                                     "category": q["category"], **m})
    abl = pd.DataFrame(abl_rows)
    cols = [c for c in abl.columns if c not in ("ablation", "level", "seed", "qid", "category")]
    per_seed = abl.groupby(["ablation", "level", "seed"])[cols].mean()
    abl_summary = per_seed.groupby(["ablation", "level"]).agg(["mean", "std"])
    abl_summary.columns = [f"{a}_{b}" for a, b in abl_summary.columns]
    abl_summary.reset_index().to_csv(RESULTS_DIR / "ablations.csv", index=False)

    # ---------------- provenance ----------------
    prov = {"python": platform.python_version(), "config": cfg}
    try:
        import sentence_transformers, torch
        from huggingface_hub import model_info
        prov["sentence_transformers"] = sentence_transformers.__version__
        prov["torch"] = torch.__version__
        prov["model_revisions"] = {m: model_info(m).sha for m in (cfg["embed_model"], cfg["rerank_model"])}
    except Exception as e:  # offline runs still produce results
        prov["model_revisions_error"] = str(e)
    (RESULTS_DIR / "provenance.json").write_text(json.dumps(prov, indent=2))

    pd.set_option("display.width", 200)
    print(main_df.round(3).to_string(index=False))
    print(abl_summary.round(3).to_string())


if __name__ == "__main__":
    main()
