---
title: "ReadinessProbe Contract"
slug: /burncloud-node/contracts/readiness-probe/
---

# `ReadinessProbe` Contract

```text
Owner: crates/platform/node
Status: Accepted / Framework Only
Source: crates/platform/node/src/preparation.rs
Fake: FakeReadinessProbe
```

## 唯一职责

等待 `ReadinessTarget` 达到“现在可以接受请求”的状态。

```rust
async fn wait_ready(&self, target: ReadinessTarget) -> Result<(), ReadinessError>;
```

## 调用顺序

```text
ProcessManager.start 成功
        ↓
ProcessStarted evidence
        ↓
ReadinessProbe.wait_ready(plan.readiness)
        ├─ Ok → 继续 HealthProbe
        └─ Err → Failed → 不得注册 Route
```

## 不负责什么

```text
ReadinessProbe 不负责
├─ 启动或重启进程
├─ 生成 readiness 地址
├─ 判断长期健康
├─ 修改 Node 生命周期
├─ 注册或摘除 Route
└─ 决定重试策略
```

`ReadinessTarget` 必须来自 `ProcessPlan`；Probe 不能自行猜测端口或路径。

## BDD 边界

```gherkin
Scenario: Runtime never becomes ready
  Given a process was started
  When ReadinessProbe returns an error
  Then the workload becomes Failed
  And no Local Channel is attached
```

## 停止条件

如果 Probe 需要理解模型、Runtime 安装、路由或计费，立即停止。若目标缺少必要信息，创建 `CONTRACT_GAP`，不要在 Probe 内猜测。

