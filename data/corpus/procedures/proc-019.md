---
id: PROC-019
title: 'GPU interconnect CRC errors at a high rate: run fabric diagnostics'
topic: interconnect
specificity: specific
device_classes: [class_a, class_b]
action_severity: medium
preconditions:
- {metric: link_crc_errors, window: 24h, op: '>=', value: 100}
- {metric: links_down, window: now, op: ==, value: 0}
---

# GPU interconnect CRC errors at a high rate: run fabric diagnostics

Use this procedure when a GPU's interconnect links report 100 or more CRC errors in the last 24 hours while
all links are still up.

A high CRC error rate causes retries that slow multi-GPU jobs and can precede a link failure.

Steps:
1. Drain multi-GPU workloads from the node.
2. Run the interconnect fabric diagnostic.
3. Reseat or replace the affected link cable or bridge if the diagnostic points to it.
