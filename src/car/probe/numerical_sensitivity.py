"""Probe: do general-purpose text embeddings separate telemetry values that call for different actions?

Three small tests per model:
  1. pairwise similarity of sentences that differ only in a number, next to a paraphrase pair and
     an unrelated pair for scale
  2. threshold test: similarity between a threshold query ("more than 100 ...") and sentences with
     values 0..300; AUC measures how well similarity separates values above vs. below the threshold
     (0.5 = no better than chance, 1.0 = perfect)
  3. zero test: does the query "zero uncorrectable errors" rank the 0-error sentence first?

Usage: python -m car.probe.numerical_sensitivity
"""
from __future__ import annotations

import json

import numpy as np
from sentence_transformers import SentenceTransformer

from car import RESULTS_DIR

MODELS = {
    "BAAI/bge-small-en-v1.5": "Represent this sentence for searching relevant passages: ",
    "sentence-transformers/all-MiniLM-L6-v2": "",
}

PAIRS = [
    ("number only: 0 vs 3 uncorrectable",
     "The GPU reported 0 uncorrectable ECC errors in the last 24 hours.",
     "The GPU reported 3 uncorrectable ECC errors in the last 24 hours."),
    ("number only: 3 vs 250 uncorrectable",
     "The GPU reported 3 uncorrectable ECC errors in the last 24 hours.",
     "The GPU reported 250 uncorrectable ECC errors in the last 24 hours."),
    ("number only: 84 °C vs 91 °C",
     "The GPU peak temperature was 84 °C in the last 24 hours.",
     "The GPU peak temperature was 91 °C in the last 24 hours."),
    ("one word: corrected vs uncorrected",
     "The GPU reported 3 corrected ECC errors in the last 24 hours.",
     "The GPU reported 3 uncorrected ECC errors in the last 24 hours."),
    ("paraphrase, same facts (reference)",
     "The GPU reported 3 uncorrectable ECC errors in the last 24 hours.",
     "In the past day, the GPU logged three ECC errors that could not be corrected."),
    ("different topic (reference)",
     "The GPU reported 3 uncorrectable ECC errors in the last 24 hours.",
     "The PCIe link on the GPU is running at 8 lanes instead of 16."),
]

THRESHOLD_TESTS = [
    ("corrected ECC errors > 100",
     "The GPU logged more than 100 corrected ECC errors in the last 24 hours.",
     "The GPU logged {v} corrected ECC errors in the last 24 hours.", list(range(0, 301, 5)), 100),
    ("peak temperature >= 90 °C",
     "The GPU temperature reached 90 °C or higher.",
     "The GPU peak temperature was {v} °C.", list(range(60, 101)), 89.5),
]


def auc(scores_pos: np.ndarray, scores_neg: np.ndarray) -> float:
    """Probability that a random above-threshold value scores higher than a random below-threshold one."""
    gt = (scores_pos[:, None] > scores_neg[None, :]).mean()
    eq = (scores_pos[:, None] == scores_neg[None, :]).mean()
    return float(gt + 0.5 * eq)


def run() -> dict:
    out = {}
    for name, qprefix in MODELS.items():
        model = SentenceTransformer(name, device="cpu")
        enc = lambda xs: model.encode(xs, normalize_embeddings=True)
        res = {"pairs": [], "threshold": [], "zero_test": {}}
        for label, a, b in PAIRS:
            ea, eb = enc([a, b])
            res["pairs"].append({"pair": label, "cosine": round(float(ea @ eb), 4)})
        for label, query, tmpl, values, thr in THRESHOLD_TESTS:
            q = enc([qprefix + query])[0]
            sims = enc([tmpl.format(v=v) for v in values]) @ q
            vals = np.array(values)
            res["threshold"].append({
                "test": label, "auc": round(auc(sims[vals > thr], sims[vals <= thr]), 3),
                "spearman_sim_vs_value": round(float(np.corrcoef(np.argsort(np.argsort(sims)),
                                                                 np.argsort(np.argsort(vals)))[0, 1]), 3),
                "most_similar_value": int(vals[int(np.argmax(sims))]),
            })
        q = enc([qprefix + "A GPU with zero uncorrectable ECC errors in the last 24 hours."])[0]
        cands = [0, 1, 3, 250]
        sims = enc([f"The GPU reported {n} uncorrectable ECC errors in the last 24 hours." for n in cands]) @ q
        ranking = [cands[i] for i in np.argsort(-sims)]
        res["zero_test"] = {"ranking_of_counts": ranking, "zero_ranked_first": ranking[0] == 0,
                            "similarities": {str(c): round(float(s), 4) for c, s in zip(cands, sims)}}
        out[name] = res
    return out


def main() -> None:
    out = run()
    RESULTS_DIR.mkdir(exist_ok=True)
    (RESULTS_DIR / "probe.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
