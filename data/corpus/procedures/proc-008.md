---
id: PROC-008
title: 'Row remap failure (class A): remove from service'
topic: gpu_memory_ecc
specificity: specific
device_classes: [class_a]
action_severity: high
preconditions:
- {metric: remap_failure, window: now, op: ==, value: 1}
---

# Row remap failure (class A): remove from service

Applies to class A GPUs only. Use this procedure when the device reports that a row remap failed, for
example because no spare rows are left in the affected memory bank.

A failed remap means the degraded memory cannot be retired and errors are likely to recur.

Steps:
1. Cordon the node and drain all workloads.
2. Remove the GPU from service.
3. Open a hardware replacement request and attach the remap status output.
