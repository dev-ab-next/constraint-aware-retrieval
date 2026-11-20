---
id: PROC-007
title: 'Row remap pending (class A): schedule a GPU reset'
topic: gpu_memory_ecc
specificity: specific
device_classes: [class_a]
action_severity: medium
preconditions:
- {metric: remap_pending, window: now, op: ==, value: 1}
- {metric: remap_failure, window: now, op: ==, value: 0}
---

# Row remap pending (class A): schedule a GPU reset

Applies to class A GPUs only. Class A devices replace degraded memory rows with spare rows, and the
replacement takes effect at the next GPU reset. Use this procedure when a remap is pending and no remap
failure has been recorded.

Running workloads are not affected while the remap is pending.

Steps:
1. Keep the GPU in service.
2. Schedule a GPU reset in the next maintenance window.
3. After the reset, confirm the pending flag is cleared.
