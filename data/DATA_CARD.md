# Data card

## What this is

A synthetic benchmark for retrieving runbook procedures for GPU hardware diagnosis, where the right
procedure depends on device telemetry. **Everything is fictional**: the fleet, the hardware classes, the
procedures and the thresholds. The procedures are modeled on the *kinds* of distinctions public GPU
operations documentation makes (for example contained vs uncontained memory errors, or row remapping vs
page retirement), but they are original text, they are not vendor guidance, and they must not be used to
operate real hardware.

## Contents

| Path | What |
|---|---|
| `corpus/procedures/*.md` | 26 procedures, 6 topics. YAML front matter holds `device_classes` and `preconditions`. |
| `telemetry/fleet.csv.gz` | 300 devices × 30 days, one row per device-day (generated). |
| `queries/queries.jsonl` | 200 questions: device, day, text, category, scenario, topic. |
| `queries/qrels.jsonl` | Labels: `specific_applicable`, `general_applicable`, and a pass/fail verdict for every procedure. |

## How the data is generated

`python -m car.generate.queries` with `configs/fleet.yaml` (seed 20261119):

1. Healthy background telemetry for every device, with occasional small corrected-error and replay counts.
2. For each query, a scenario (`src/car/generate/scenarios.py`) injects a fault into one unused device's
   telemetry and picks a question template. 40 queries per category, cycling through that category's
   scenarios.
3. Labels are computed from the device's **true** state after injection:
   - *specific_applicable*: procedures on the query's topic, not general triage, whose preconditions all pass
   - *general_applicable*: the general-triage procedure for the topic
   - a verdict (pass/fail) for every procedure, used to count violations
   A scenario's intended target procedure is only used as a sanity check: generation fails if the
   target does not apply after injection.

## Known limitations

- **Labels share preconditions with the verifier.** In the clean setting, C5's zero-violation result
  follows by construction. The ablations (noisy preconditions, missing telemetry) exist to measure what
  happens when that assumption breaks.
- **Small and templated.** 26 procedures, 200 questions, a limited set of templates, and a single
  set of labeling rules with no independent review.
- **Relevance is by topic.** A procedure from another topic is never counted as relevant, even when an
  operator might find it useful.
- **Simplified telemetry.** Daily granularity; windows are "now", "24h" (the query day) and "7d"
  (7 days ending on the query day). A window with any missing day is treated as missing.
