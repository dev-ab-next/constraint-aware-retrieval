---
id: PROC-009
title: 'GPU memory errors: general triage and data collection'
topic: gpu_memory_ecc
specificity: general
device_classes: [class_a, class_b]
action_severity: low
preconditions: []
---

# GPU memory errors: general triage and data collection

General first steps for any report of GPU memory or ECC errors, before choosing a specific procedure.

Steps:
1. Collect the device's corrected and uncorrected error counts for the last 24 hours and 7 days.
2. Collect the row remap status (class A) or retired-page count (class B).
3. Note which jobs were running on the GPU when the errors were reported.
4. Use the collected data to choose the matching procedure.
