---
id: PROC-015
title: 'PCIe replay errors at a high rate: reseat and test'
topic: pcie
specificity: specific
device_classes: [class_a, class_b]
action_severity: medium
preconditions:
- {metric: pcie_replay, window: 24h, op: '>=', value: 50}
---

# PCIe replay errors at a high rate: reseat and test

Use this procedure when a GPU reports 50 or more PCIe replay events in the last 24 hours.

A high replay rate reduces bandwidth and can point to a loose card, a bad riser or a failing slot.

Steps:
1. Drain the node.
2. Reseat the GPU and inspect the riser and slot.
3. Run the PCIe link test before returning the node to service.
