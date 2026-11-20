---
id: PROC-025
title: 'Host DIMM corrected memory errors: monitor'
topic: host_memory
specificity: specific
device_classes: [class_a, class_b]
action_severity: low
preconditions:
- {metric: host_dimm_corrected, window: 24h, op: '>=', value: 1}
- {metric: host_dimm_uncorrected, window: 24h, op: ==, value: 0}
---

# Host DIMM corrected memory errors: monitor

Use this procedure when the host server (not the GPU) reports corrected memory errors on its DIMMs in the
last 24 hours and no uncorrected DIMM errors.

Steps:
1. Leave the node in service.
2. Record which DIMM slot reported the errors.
3. Replace the DIMM at the next maintenance window if the count keeps rising.
