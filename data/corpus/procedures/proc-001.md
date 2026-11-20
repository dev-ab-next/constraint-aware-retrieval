---
id: PROC-001
title: 'Corrected GPU memory errors at a low rate: monitor'
topic: gpu_memory_ecc
specificity: specific
device_classes: [class_a, class_b]
action_severity: low
preconditions:
- {metric: ecc_corrected, window: 24h, op: '>=', value: 1}
- {metric: ecc_corrected, window: 24h, op: <, value: 100}
- {metric: ecc_uncorrected, window: 7d, op: ==, value: 0}
---

# Corrected GPU memory errors at a low rate: monitor

Use this procedure when a GPU reports corrected (single-bit) ECC memory errors at a low rate: at least one
but fewer than 100 corrected errors in the last 24 hours, and no uncorrected errors in the last 7 days.

Corrected errors are fixed by the memory's error-correcting code and do not affect running workloads. A low
rate is common across a large fleet and does not by itself indicate a failing device.

Steps:
1. Leave the GPU in service. Do not drain workloads.
2. Record the corrected-error count in the device history so the trend can be tracked.
3. Re-check the count after 24 hours. If it rises to 100 or more per day, switch to PROC-002.
