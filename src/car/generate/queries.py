"""Build the benchmark: fleet telemetry, queries and ground-truth labels.

Usage: python -m car.generate.queries --config configs/fleet.yaml
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict

import numpy as np
import pandas as pd
import yaml

from car import DATA_DIR, REPO_ROOT
from car.corpus import load_corpus
from car.generate.fleet import generate_fleet
from car.generate.scenarios import CATEGORIES, SCENARIOS
from car.telemetry import device_state
from car.verify.check import check_procedure


def label_query(procs, device_class, state, topic):
    """Ground truth for one query, computed from the device's TRUE state."""
    verdicts = {p.id: check_procedure(p, device_class, state).value for p in procs}
    specific = [p.id for p in procs if p.topic == topic and p.specificity == "specific" and verdicts[p.id] == "pass"]
    general = [p.id for p in procs if p.topic == topic and p.specificity == "general" and verdicts[p.id] == "pass"]
    return {"specific_applicable": specific, "general_applicable": general, "verdicts": verdicts}


def build(cfg: dict) -> tuple[pd.DataFrame, list[dict], list[dict]]:
    rng = np.random.default_rng(cfg["seed"])
    procs = load_corpus()
    tel = generate_fleet(cfg["n_devices"], cfg["n_days"], rng)
    tel = tel.set_index(["device_id", "day"]).sort_index()
    classes = tel.groupby(level=0)["device_class"].first().to_dict()

    by_cat = defaultdict(list)
    for s in SCENARIOS:
        by_cat[s.category].append(s)

    free = {c: [d for d, k in classes.items() if k == c] for c in ("class_a", "class_b")}
    for c in free:
        rng.shuffle(free[c])

    queries, qrels = [], []
    per_cat = cfg["queries_per_category"]
    for cat in CATEGORIES:
        scens = by_cat[cat]
        for i in range(per_cat):
            sc = scens[i % len(scens)]
            want = sc.device_class or ("class_a" if len(free["class_a"]) >= len(free["class_b"]) else "class_b")
            dev = free[want].pop()  # every query uses a different device
            day = int(rng.integers(10, cfg["n_days"]))

            def setter(offset, metric, value, dev=dev, day=day):
                tel.loc[(dev, day + offset), metric] = value

            params = sc.inject(rng, setter)
            template = sc.questions[int(rng.integers(len(sc.questions)))]
            if "{n}" in template and "n" not in params:
                template = sc.questions[0]
            text = template.format(dev=dev, **params)
            qid = f"Q{len(queries) + 1:03d}"

            state = device_state(tel.reset_index(), dev, day)
            gt = label_query(procs, classes[dev], state, sc.topic)
            if sc.target not in gt["specific_applicable"]:
                raise AssertionError(f"{qid} {sc.name}: target {sc.target} does not apply after injection")
            queries.append({"qid": qid, "device_id": dev, "device_class": classes[dev], "day": day,
                            "text": text, "category": cat, "scenario": sc.name, "topic": sc.topic})
            qrels.append({"qid": qid, "target": sc.target, **gt})
    return tel.reset_index(), queries, qrels


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(REPO_ROOT / "configs" / "fleet.yaml"))
    args = ap.parse_args()
    cfg = yaml.safe_load(open(args.config))
    tel, queries, qrels = build(cfg)
    (DATA_DIR / "telemetry").mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "queries").mkdir(parents=True, exist_ok=True)
    tel.to_csv(DATA_DIR / "telemetry" / "fleet.csv.gz", index=False)
    with open(DATA_DIR / "queries" / "queries.jsonl", "w") as f:
        f.writelines(json.dumps(q) + "\n" for q in queries)
    with open(DATA_DIR / "queries" / "qrels.jsonl", "w") as f:
        f.writelines(json.dumps(q) + "\n" for q in qrels)
    n_spec = np.mean([len(q["specific_applicable"]) for q in qrels])
    print(f"{len(tel)} telemetry rows, {len(queries)} queries, "
          f"mean specific-applicable procedures per query: {n_spec:.2f}")


if __name__ == "__main__":
    main()
