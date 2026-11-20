---
id: PROC-013
title: 'GPU thermal issues: general triage'
topic: thermal
specificity: general
device_classes: [class_a, class_b]
action_severity: low
preconditions: []
---

# GPU thermal issues: general triage

General first steps for any report of high GPU temperature or thermal throttling.

Steps:
1. Collect peak and average temperature for the last 24 hours.
2. Collect throttling event counts and fan speeds.
3. Use the collected data to choose the matching thermal procedure.
