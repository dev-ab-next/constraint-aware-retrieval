---
id: PROC-002
title: 'Corrected GPU memory errors at an elevated rate: run diagnostics'
topic: gpu_memory_ecc
specificity: specific
device_classes: [class_a, class_b]
action_severity: medium
preconditions:
- {metric: ecc_corrected, window: 24h, op: '>=', value: 100}
- {metric: ecc_uncorrected, window: 24h, op: ==, value: 0}
---

# Corrected GPU memory errors at an elevated rate: run diagnostics

Use this procedure when a GPU reports 100 or more corrected ECC memory errors in the last 24 hours and no
uncorrected errors in the same period.

An elevated corrected-error rate can be an early sign of degrading memory, even though every error so far
has been corrected and running workloads are unaffected.

Steps:
1. Keep current workloads running, but stop scheduling new long-running jobs on the GPU.
2. Run the extended memory diagnostic during the next maintenance window.
3. If the diagnostic fails, or uncorrected errors appear, follow the uncorrected-error procedure for the
   device class (PROC-003, PROC-004 or PROC-005).
4. Open a ticket to watch the trend for 7 days.
