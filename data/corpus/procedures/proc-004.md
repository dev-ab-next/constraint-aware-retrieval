---
id: PROC-004
title: 'Uncorrected, uncontained GPU memory error (class A): drain and reset'
topic: gpu_memory_ecc
specificity: specific
device_classes: [class_a]
action_severity: high
preconditions:
- {metric: ecc_uncontained, window: 24h, op: '>=', value: 1}
---

# Uncorrected, uncontained GPU memory error (class A): drain and reset

Applies to class A GPUs only. Use this procedure when the GPU reports one or more uncontained uncorrected
ECC memory errors in the last 24 hours.

An uncontained error means the device could not isolate the corrupted memory to a single job, so any
workload on the GPU may be affected.

Steps:
1. Cordon the node so no new work is scheduled.
2. Drain or stop all workloads on the GPU.
3. Reset the GPU and confirm that any pending row remap has been applied.
4. Run the extended memory diagnostic before returning the node to service.
