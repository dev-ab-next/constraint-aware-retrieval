---
id: PROC-020
title: 'GPU interconnect link down: drain and repair'
topic: interconnect
specificity: specific
device_classes: [class_a, class_b]
action_severity: high
preconditions:
- {metric: links_down, window: now, op: '>=', value: 1}
---

# GPU interconnect link down: drain and repair

Use this procedure when one or more of a GPU's interconnect links are currently down.

With a link down, multi-GPU jobs either fail or fall back to a much slower path.

Steps:
1. Cordon the node and drain all multi-GPU workloads.
2. Try to bring the link back with a GPU reset.
3. If the link stays down, open a hardware ticket for the link hardware.
