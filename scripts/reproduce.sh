#!/usr/bin/env bash
# Regenerate the benchmark and every result in results/. CPU-only; 10-15 minutes on 4 cores.
set -euo pipefail
cd "$(dirname "$0")/.."

python -m pytest -q
python -m car.generate.queries                 # fleet telemetry, 200 queries, labels (fixed seed)
python -m car.probe.numerical_sensitivity      # embedding probe    -> results/probe.json
python -m car.eval.run                         # C1-C5 + ablations  -> results/*.csv
python -m car.eval.figures                     # figures            -> results/fig_*.png
python -m car.eval.report                      # tables             -> results/README.md
