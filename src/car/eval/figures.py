"""Render the two blog figures from results/*.csv.

Usage: python -m car.eval.figures
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from car import RESULTS_DIR
from car.eval.report import pct

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"  # categorical slots 1-3, fixed order

LABELS = {"C1": "C1\nDense", "C2": "C2\nHybrid", "C3": "C3\n+ filter", "C4": "C4\n+ rerank", "C5": "C5\n+ verify"}


def _style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(INK2)
    ax.tick_params(colors=INK2, length=0)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def main_figure():
    df = pd.read_csv(RESULTS_DIR / "main.csv").set_index("condition")
    conds = list(df.index)
    x = np.arange(len(conds))
    w = 0.36
    fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200, facecolor=SURFACE)
    _style(ax)
    series = [("top1_violation", "Top result contradicts telemetry", ORANGE, -w / 2 - 0.01),
              ("top1_correct", "Top result is the correct specific procedure", BLUE, w / 2 + 0.01)]
    for col, label, color, off in series:
        vals = df[col].values
        ax.bar(x + off, vals, w, color=color, label=label, edgecolor=SURFACE, linewidth=1)
        for xi, v in zip(x, vals):
            ax.text(xi + off, v + 0.02, pct(v), ha="center", va="bottom", fontsize=8, color=INK2)
    ax.set_xticks(x, [LABELS[c] for c in conds], color=INK, fontsize=9)
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    ax.set_title("Top-ranked procedure by retrieval setup (200 queries)", loc="left", color=INK, fontsize=11)
    ax.legend(frameon=False, loc="upper left", fontsize=8.5, labelcolor=INK)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "fig_main.png", facecolor=SURFACE)
    plt.close(fig)


def ablation_figure():
    df = pd.read_csv(RESULTS_DIR / "ablations.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), dpi=200, facecolor=SURFACE, sharey=True)
    panels = [("missing_telemetry", "Missing telemetry"), ("noisy_preconditions", "Imperfect preconditions")]
    lines = [("recall@3", "Recall@3 (correct procedure in top 3)", BLUE, "o"),
             ("unflagged_violation@3", "Unflagged violation in top 3", ORANGE, "s"),
             ("flagged@3", "At least one result flagged as unchecked", AQUA, "^")]
    for ax, (kind, title) in zip(axes, panels):
        _style(ax)
        d = df[df.ablation == kind].sort_values("level")
        for col, label, color, marker in lines:
            ax.errorbar(d.level, d[f"{col}_mean"], yerr=d[f"{col}_std"], color=color, marker=marker,
                        markersize=6, linewidth=2, capsize=3, label=label,
                        markeredgecolor=SURFACE, markeredgewidth=1.5)
        ax.set_title(title, loc="left", color=INK, fontsize=10)
        ax.set_xticks([0, 0.1, 0.25, 0.5], ["0%", "10%", "25%", "50%"], color=INK)
        ax.set_xlabel("probability each metric is missing" if kind == "missing_telemetry"
                      else "probability each condition is dropped or wrong", color=INK2, fontsize=8.5)
        ax.set_ylim(-0.03, 1.05)
        ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1.0))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=8.5, labelcolor=INK)
    fig.suptitle("C5 under degraded inputs (mean ± sd over 5 seeds)", x=0.01, ha="left", color=INK, fontsize=11)
    fig.tight_layout(rect=(0, 0.08, 1, 0.97))
    fig.savefig(RESULTS_DIR / "fig_ablations.png", facecolor=SURFACE)
    plt.close(fig)


if __name__ == "__main__":
    main_figure()
    ablation_figure()
    print("wrote", RESULTS_DIR / "fig_main.png", RESULTS_DIR / "fig_ablations.png")
