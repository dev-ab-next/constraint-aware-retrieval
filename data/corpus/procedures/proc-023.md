---
id: PROC-023
title: 'Node power supply redundancy lost: schedule replacement'
topic: power
specificity: specific
device_classes: [class_a, class_b]
action_severity: medium
preconditions:
- {metric: psu_degraded, window: now, op: ==, value: 1}
---

# Node power supply redundancy lost: schedule replacement

Use this procedure when the node hosting the GPU reports that a power supply unit has failed or lost
redundancy.

The node keeps running on the remaining supplies, but another failure would take it down.

Steps:
1. Keep workloads running but avoid scheduling new long jobs on the node.
2. Schedule a power supply replacement.
3. Confirm redundancy is restored after the replacement.
