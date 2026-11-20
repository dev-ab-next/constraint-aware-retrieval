# Figures

All figures are original and were made for this project.

| Image | Shows | Used in | Made by |
|---|---|---|---|
| `docs/img/check.png` | The precondition check: PASS, FAIL or UNKNOWN | Walkthrough | `source/diagrams.html` |
| `docs/img/pipeline.png` | The five setups, C1 to C5 | Walkthrough | `source/diagrams.html` |
| `docs/img/data_flow.png` | How the test data is built | Walkthrough | `source/diagrams.html` |
| `results/fig_main.png` | Main results for the five setups | README, results page | `python -m car.eval.figures` |
| `results/fig_ablations.png` | C5 with missing data and wrong conditions | Results page | `python -m car.eval.figures` |

The two results charts are rebuilt from the result files by `scripts/reproduce.sh`. The three diagrams are
drawn as SVG in `source/diagrams.html`. To re-render them after editing that file (requires Node.js and
Playwright with Chromium):

```bash
node docs/img/source/render.js docs/img/source/diagrams.html docs/img
```
