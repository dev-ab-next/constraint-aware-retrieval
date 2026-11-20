---
id: PROC-011
title: 'GPU temperature at or above the critical limit: migrate workloads'
topic: thermal
specificity: specific
device_classes: [class_a, class_b]
action_severity: high
preconditions:
- {metric: temp_max_c, window: 24h, op: '>=', value: 90}
---

# GPU temperature at or above the critical limit: migrate workloads

Use this procedure when a GPU's peak temperature over the last 24 hours reached 90 °C or higher.

At this temperature the GPU throttles its clocks heavily and long exposure can shorten its life.

Steps:
1. Migrate long-running workloads off the GPU.
2. Cordon the node until the cooling issue is fixed.
3. Inspect fans, heat sinks and rack airflow, and escalate to facilities if the inlet temperature is high.
