---
id: PROC-006
title: 'Past uncorrected GPU memory errors with none in the last day: review history'
topic: gpu_memory_ecc
specificity: specific
device_classes: [class_a, class_b]
action_severity: low
preconditions:
- {metric: ecc_uncorrected, window: 7d, op: '>=', value: 1}
- {metric: ecc_uncorrected, window: 24h, op: ==, value: 0}
---

# Past uncorrected GPU memory errors with none in the last day: review history

Use this procedure when a GPU had at least one uncorrected ECC memory error in the last 7 days but none in
the last 24 hours. The original error should already have been handled; this procedure checks that the
follow-up actions were completed.

Steps:
1. Confirm the earlier incident was closed and that any required reset or reboot happened.
2. Confirm no row remap is still pending and no remap failure was recorded.
3. Keep the GPU in service and add it to the weekly watch list.
