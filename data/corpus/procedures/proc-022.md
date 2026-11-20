---
id: PROC-022
title: 'GPU power brake events: check power delivery'
topic: power
specificity: specific
device_classes: [class_a, class_b]
action_severity: medium
preconditions:
- {metric: power_brake_events, window: 24h, op: '>=', value: 1}
---

# GPU power brake events: check power delivery

Use this procedure when a GPU reports one or more power brake events in the last 24 hours. A power brake is
a hardware signal that forces the GPU to its lowest clocks to protect the power supply.

Steps:
1. Check the node's power supply status and the rack's power budget.
2. Check whether other GPUs in the node had brake events at the same time.
3. If only this GPU is affected, inspect its power cables.
