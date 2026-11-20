---
id: PROC-021
title: 'GPU interconnect issues: general triage'
topic: interconnect
specificity: general
device_classes: [class_a, class_b]
action_severity: low
preconditions: []
---

# GPU interconnect issues: general triage

General first steps for any report of GPU-to-GPU interconnect errors or slow multi-GPU communication.

Steps:
1. Collect per-link CRC error counts for the last 24 hours and the current link states.
2. Check whether other GPUs on the same node report errors.
3. Use the collected data to choose the matching interconnect procedure.
