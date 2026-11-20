---
id: PROC-010
title: 'GPU temperature in the warning band: check cooling'
topic: thermal
specificity: specific
device_classes: [class_a, class_b]
action_severity: low
preconditions:
- {metric: temp_max_c, window: 24h, op: '>=', value: 83}
- {metric: temp_max_c, window: 24h, op: <, value: 90}
---

# GPU temperature in the warning band: check cooling

Use this procedure when a GPU's peak temperature over the last 24 hours was at least 83 °C but below 90 °C.

Temperatures in this band are above the fleet's normal operating range but below the critical limit.

Steps:
1. Keep workloads running.
2. Check fan speeds, inlet temperature and airflow for the rack.
3. Compare with neighboring GPUs to see whether the issue is local or rack-wide.
