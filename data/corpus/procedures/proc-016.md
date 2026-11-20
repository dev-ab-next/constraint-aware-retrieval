---
id: PROC-016
title: 'PCIe link running below full width: inspect the slot'
topic: pcie
specificity: specific
device_classes: [class_a, class_b]
action_severity: medium
preconditions:
- {metric: pcie_link_width, window: now, op: <, value: 16}
---

# PCIe link running below full width: inspect the slot

Use this procedure when a GPU's PCIe link is currently trained below its full width of 16 lanes.

A narrow link lowers host-to-device bandwidth even when no errors are reported.

Steps:
1. Confirm the reduced width after a warm reboot.
2. If it persists, drain the node, reseat the GPU and inspect the slot.
3. If the width is still reduced, open a hardware ticket for the slot or riser.
