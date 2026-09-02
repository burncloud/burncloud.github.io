---
title: "类别六：Local Channel Integration 与 Demand Reconciliation"
slug: /burncloud-node/implementation-plan/local-channel/
---

# 类别六：Local Channel Integration 与 Demand Reconciliation

这一层把“真实本地 Runtime”接回 existing BurnCloud Router，并把用户 `/v1` 中出现的 model demand 自动收敛成本地 READY 能力。

```text
/v1 model demand
      ↓
NODE-504 Reconciler
      ↓
Resolve / Prepare / Runtime / READY
      ↓
NODE-501 Local Channel / Ability
      ↓
NODE-502 health linkage
      ↓
Existing ModelRouter
```

与此同时，**当前请求仍由 existing ModelRouter 决定走 Local 还是 Provider**。Reconciler 不成为第二个 Router。

核心产品行为：

- Local READY：Router 可优先 Local；
- Local absent + Provider available：当前请求先走 Provider，后台自动准备 Local；
- Provider unavailable + local preparing：返回 `MODEL_PREPARING`；
- local impossible：返回真实 Hardware / Disk / Runtime diagnosis；
- 相同模型并发请求只产生一个 local preparation pipeline；
- Runtime stop/crash/unhealthy 后 Local Channel 自动失效。

本类别包括：

- **NODE-501**：READY Runtime 自动注册 Local Channel / Ability；
- **NODE-502**：健康联动、摘除与恢复；
- **NODE-504**：Model Demand Reconciliation；
- **NODE-503**：最终 demand-driven E2E 验收。
