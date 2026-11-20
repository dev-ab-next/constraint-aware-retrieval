"""Write results/README.md: every table from the CSV/JSON outputs, in one readable page.

Usage: python -m car.eval.report
"""
from __future__ import annotations

import json
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd

from car import DATA_DIR, RESULTS_DIR

NAMES = {"C1": "C1 Dense", "C2": "C2 Hybrid", "C3": "C3 + class filter",
         "C4": "C4 + rerank", "C5": "C5 + verification"}
CATS = {"numerical_threshold": "Numerical threshold", "error_type_contrast": "Error-type contrast",
        "device_class": "Device class", "temporal": "Temporal", "distractor": "Distractor"}


def pct(x: float) -> str:
    """Whole percent, rounding halves up (26.5% -> 27%), so every table rounds the same way."""
    return f"{Decimal(repr(float(x) * 100)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)}%"


def table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(lines)


def main_table(df: pd.DataFrame) -> str:
    rows = [[NAMES[r.condition], pct(r.top1_violation), pct(r.top1_correct), pct(r["recall@3"]),
             pct(r["violation_rate@3"]), f"{r['ndcg@3']:.2f}", f"{r.latency_p50_ms:.0f} ms"]
            for _, r in df.iterrows()]
    return table(["Setup", "Top-1 violation ↓", "Top-1 correct ↑", "Recall@3 ↑",
                  "Violations in top 3 ↓", "nDCG@3 ↑", "Latency p50"], rows)


def category_table(df: pd.DataFrame, metric: str) -> str:
    piv = df.pivot(index="category", columns="condition", values=metric)
    rows = [[CATS[c]] + [pct(piv.loc[c, k]) for k in NAMES] for c in CATS]
    return table(["Category"] + list(NAMES), rows)


def ablation_table(df: pd.DataFrame, kind: str) -> str:
    d = df[df.ablation == kind].sort_values("level")
    rows = [[pct(r.level), f"{pct(r['recall@3_mean'])} ± {pct(r['recall@3_std'])}",
             f"{pct(r['unflagged_violation@3_mean'])} ± {pct(r['unflagged_violation@3_std'])}",
             f"{pct(r['flagged@3_mean'])} ± {pct(r['flagged@3_std'])}"] for _, r in d.iterrows()]
    first = "Metric missing" if kind == "missing_telemetry" else "Clause dropped or wrong"
    return table([first, "Recall@3", "Unflagged violation in top 3", "Flagged result in top 3"], rows)


def probe_tables(probe: dict) -> str:
    models = list(probe)
    short = [m.split("/")[-1] for m in models]
    pairs = [p["pair"] for p in probe[models[0]]["pairs"]]
    rows = [[p] + [f"{probe[m]['pairs'][i]['cosine']:.3f}" for m in models] for i, p in enumerate(pairs)]
    out = table(["Sentence pair (cosine similarity)"] + short, rows)
    tests = [t["test"] for t in probe[models[0]]["threshold"]]
    rows = [[t] + [f"{probe[m]['threshold'][i]['auc']:.2f}" for m in models] for i, t in enumerate(tests)]
    out += "\n\n" + table(["Threshold test (AUC, 0.5 = chance)"] + short, rows)
    return out


def per_question_csv() -> None:
    """One row per question: what was asked, what was true, and what each setup put first."""
    from car.corpus import load_corpus
    from car.telemetry import device_state

    titles = {p.id: p.title for p in load_corpus()}
    queries = [json.loads(line) for line in open(DATA_DIR / "queries" / "queries.jsonl")]
    qrels = {r["qid"]: r for r in map(json.loads, open(DATA_DIR / "queries" / "qrels.jsonl"))}
    runs = {(r["condition"], r["qid"]): r for r in map(json.loads, open(RESULTS_DIR / "per_query.jsonl"))}
    tel = pd.read_csv(DATA_DIR / "telemetry" / "fleet.csv.gz")
    rows = []
    for q in queries:
        qr = qrels[q["qid"]]
        st = device_state(tel, q["device_id"], q["day"])
        today = {m: v for (m, w), v in st.items() if w == "24h" and v == v and v != 0
                 and m not in ("temp_max_c", "pcie_link_width")}
        today["temp_max_c"] = st[("temp_max_c", "24h")]
        if st[("pcie_link_width", "24h")] != 16:
            today["pcie_link_width"] = st[("pcie_link_width", "24h")]
        row = {"qid": q["qid"], "category": q["category"], "question": q["text"],
               "device_class": q["device_class"],
               "telemetry_today": "; ".join(f"{m}={v:g}" for m, v in today.items()),
               "right_procedures": "; ".join(qr["specific_applicable"])}
        for c in NAMES:
            ret = runs[(c, q["qid"])]["returned"]
            first = ret[0] if ret else ""
            row[f"{c}_first"] = f"{first} {titles.get(first, '')}".strip()
            row[f"{c}_first_fits"] = "yes" if first and qr["verdicts"][first] == "pass" else "no"
            right = set(qr["specific_applicable"])
            row[f"{c}_right_found_in_top3"] = f"{len(right & set(ret))} of {len(right)}"
        rows.append(row)
    pd.DataFrame(rows).to_csv(RESULTS_DIR / "per_question.csv", index=False)
    print("wrote", RESULTS_DIR / "per_question.csv")


def main() -> None:
    main_df = pd.read_csv(RESULTS_DIR / "main.csv")
    cat = pd.read_csv(RESULTS_DIR / "by_category.csv")
    abl = pd.read_csv(RESULTS_DIR / "ablations.csv")
    probe = json.loads((RESULTS_DIR / "probe.json").read_text())
    prov = json.loads((RESULTS_DIR / "provenance.json").read_text())

    md = f"""# Results

Generated by `python -m car.eval.report` from the files in this folder. 200 queries, top 3 results per setup.
Latency depends on the machine (4-core CPU here); all other numbers reproduce exactly from the fixed seed.

**Top-1 violation:** the first result's preconditions are false for the device.
**Top-1 correct:** the first result is the specific procedure that applies.
**Recall@3:** share of applicable specific procedures found in the top 3.

## Main comparison

![main](fig_main.png)

{main_table(main_df)}

C5's zero violations follow by construction when preconditions are correct, because the labels use the
same preconditions. The ablations below show what happens when they are wrong.

## Top-1 violation by category

{category_table(cat, "top1_violation")}

## Top-1 correct by category

{category_table(cat, "top1_correct")}

## Recall@3 by category

{category_table(cat, "recall@3")}

## Robustness of C5 (mean ± sd over 5 seeds)

![ablations](fig_ablations.png)

**Missing telemetry:** each metric removed for the queried device with the given probability.

{ablation_table(abl, "missing_telemetry")}

**Imperfect preconditions:** each precondition clause dropped or given a wrong threshold with the given
probability, simulating authoring or extraction errors.

{ablation_table(abl, "noisy_preconditions")}

## Embedding probe

{probe_tables(probe)}

## Run details

- Embedding model: `{prov['config']['embed_model']}` (revision `{prov.get('model_revisions', {}).get(prov['config']['embed_model'], 'n/a')[:12]}`)
- Reranker: `{prov['config']['rerank_model']}` (revision `{prov.get('model_revisions', {}).get(prov['config']['rerank_model'], 'n/a')[:12]}`)
- Python {prov['python']}, torch {prov.get('torch', 'n/a')}, sentence-transformers {prov.get('sentence_transformers', 'n/a')}, CPU only
- Every question with what each setup put first: [`per_question.csv`](per_question.csv)
- Raw per-query outputs: `per_query.jsonl`
"""
    (RESULTS_DIR / "README.md").write_text(md)
    print("wrote", RESULTS_DIR / "README.md")
    per_question_csv()


if __name__ == "__main__":
    main()
