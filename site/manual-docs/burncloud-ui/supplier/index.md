---
title: "Supplier"
slug: /burncloud-ui/supplier/
---

# Supplier

Supplier 的 Mental Model：

```text
GPU → Health → Contribution → Earnings
```

Supplier 的任务是接入机器、保持健康、理解贡献并获得收入。模型部署、Runtime 参数、模型切换和流量分配由 BurnCloud 自动完成。

## 页面

- Overview
- Resources
- Deployments
- Earnings
- Settlements
- Reliability
- Settings

## 最高边界

Deployments **只读**。Supplier 可以请求 Graceful Offline，但不能手工选择模型、启动 Runtime、调整 Traffic 或绕过 Scheduler。
