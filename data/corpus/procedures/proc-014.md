---
id: PROC-014
title: 'PCIe replay errors at a low rate: monitor'
topic: pcie
specificity: specific
device_classes: [class_a, class_b]
action_severity: low
preconditions:
- {metric: pcie_replay, window: 24h, op: '>=', value: 1}
- {metric: pcie_replay, window: 24h, op: <, value: 50}
---

# PCIe replay errors at a low rate: monitor

Use this procedure when a GPU reports between 1 and 49 PCIe replay events in the last 24 hours.

A replay means a packet on the PCIe link had to be resent. A small number of replays is normal and the link
recovers on its own.

Steps:
1. Leave the GPU in service.
2. Record the count and re-check it after 24 hours.
3. If the count reaches 50 or more per day, follow PROC-015.
