---
id: PROC-026
title: 'Host DIMM uncorrected memory errors: drain and replace'
topic: host_memory
specificity: specific
device_classes: [class_a, class_b]
action_severity: high
preconditions:
- {metric: host_dimm_uncorrected, window: 24h, op: '>=', value: 1}
---

# Host DIMM uncorrected memory errors: drain and replace

Use this procedure when the host server (not the GPU) reports one or more uncorrected memory errors on its
DIMMs in the last 24 hours.

Uncorrected host memory errors can crash the operating system or corrupt data in host memory.

Steps:
1. Cordon the node and drain all workloads.
2. Identify the failing DIMM slot from the system event log.
3. Replace the DIMM and run a host memory test before returning the node to service.
