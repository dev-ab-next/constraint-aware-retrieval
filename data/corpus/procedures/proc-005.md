---
id: PROC-005
title: 'Uncorrected GPU memory error (class B): drain and reboot to retire pages'
topic: gpu_memory_ecc
specificity: specific
device_classes: [class_b]
action_severity: high
preconditions:
- {metric: ecc_uncorrected, window: 24h, op: '>=', value: 1}
---

# Uncorrected GPU memory error (class B): drain and reboot to retire pages

Applies to class B GPUs only. Class B devices handle bad memory by retiring pages, and retirement takes
effect only after the device is reinitialized. Use this procedure when a class B GPU reports one or more
uncorrected ECC memory errors in the last 24 hours.

Steps:
1. Cordon the node and drain all workloads; class B devices cannot contain the error to a single job.
2. Reboot the node so the retired pages take effect.
3. Check the retired-page count. If it exceeds the replacement limit, open a hardware replacement request.
