---
id: PROC-003
title: 'Uncorrected, contained GPU memory error (class A): restart the affected job'
topic: gpu_memory_ecc
specificity: specific
device_classes: [class_a]
action_severity: medium
preconditions:
- {metric: ecc_uncorrected, window: 24h, op: '>=', value: 1}
- {metric: ecc_uncontained, window: 24h, op: ==, value: 0}
---

# Uncorrected, contained GPU memory error (class A): restart the affected job

Applies to class A GPUs only. Use this procedure when the GPU reports at least one uncorrected ECC memory
error in the last 24 hours and every one of those errors was contained (the uncontained-error count is 0).

On class A devices, a contained error affects only the job that touched the bad memory. Other jobs on the
same GPU continue to run correctly.

Steps:
1. Restart the job that was terminated by the error. Other workloads can stay on the GPU.
2. Check whether a row remap is pending. If it is, follow PROC-007 to schedule a GPU reset.
3. Do not take the node out of service for a single contained error.
