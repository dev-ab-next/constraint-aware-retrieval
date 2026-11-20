---
id: PROC-024
title: 'GPU power issues: general triage'
topic: power
specificity: general
device_classes: [class_a, class_b]
action_severity: low
preconditions: []
---

# GPU power issues: general triage

General first steps for any report of GPU power problems, unexpected clock drops or power-related resets.

Steps:
1. Collect power draw, power brake event counts and power supply status.
2. Check the rack's power budget.
3. Use the collected data to choose the matching power procedure.
