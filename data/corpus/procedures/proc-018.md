---
id: PROC-018
title: 'GPU interconnect CRC errors at a low rate: monitor'
topic: interconnect
specificity: specific
device_classes: [class_a, class_b]
action_severity: low
preconditions:
- {metric: link_crc_errors, window: 24h, op: '>=', value: 1}
- {metric: link_crc_errors, window: 24h, op: <, value: 100}
- {metric: links_down, window: now, op: ==, value: 0}
---

# GPU interconnect CRC errors at a low rate: monitor

Use this procedure when a GPU's interconnect links report between 1 and 99 CRC errors in the last 24 hours
and all links are up.

The interconnect retries corrupted transfers, so a low CRC error rate does not affect results.

Steps:
1. Leave the GPU in service.
2. Record the count and check the trend after 24 hours.
3. If the count reaches 100 or more per day, follow PROC-019.
