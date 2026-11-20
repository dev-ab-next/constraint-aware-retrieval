---
id: PROC-012
title: 'Thermal throttling reported at normal temperature: check sensors and firmware'
topic: thermal
specificity: specific
device_classes: [class_a, class_b]
action_severity: medium
preconditions:
- {metric: thermal_throttle_events, window: 24h, op: '>=', value: 1}
- {metric: temp_max_c, window: 24h, op: <, value: 83}
---

# Thermal throttling reported at normal temperature: check sensors and firmware

Use this procedure when a GPU reports thermal throttling events in the last 24 hours even though its peak
temperature stayed below 83 °C.

Throttling at a normal temperature usually points to a faulty sensor, a misconfigured limit or a firmware
problem rather than a real cooling issue.

Steps:
1. Compare the reported temperature with a second sensor or a neighboring GPU.
2. Check that the configured thermal limits match the fleet standard.
3. Check the firmware version and update it if it is behind the fleet baseline.
