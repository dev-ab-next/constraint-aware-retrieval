---
id: PROC-017
title: 'PCIe issues: general triage'
topic: pcie
specificity: general
device_classes: [class_a, class_b]
action_severity: low
preconditions: []
---

# PCIe issues: general triage

General first steps for any report of PCIe errors or bandwidth problems on a GPU.

Steps:
1. Collect the replay count for the last 24 hours and the current link width and speed.
2. Check the host's kernel log for PCIe error messages.
3. Use the collected data to choose the matching PCIe procedure.
