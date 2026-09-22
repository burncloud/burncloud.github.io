---
title: "HealthProbe Contract"
slug: /burncloud-node/contracts/health-probe/
---

# `HealthProbe` Contract

```text
Owner: crates/platform/node
Status: Accepted / Framework Only
Source: crates/platform/node/src/preparation.rs
Fake: FakeHealthProbe
```

## 唯一职责

检查 `ReadinessTarget` 当前是否健康，并返回布尔健康事实或检查错误。

```rust
async fn is_healthy(&self, target: ReadinessTarget) -> Result<bool, HealthError>;
```

## Readiness 与 Health 的区别

```text
ReadinessProbe
└─ 回答：服务是否已经可以接收请求？

HealthProbe
└─ 回答：服务当前是否仍然健康？
```

二者可以使用同一个 `ReadinessTarget`，但不能因此合并职责。

## 具体示例

输入：

```text
ReadinessTarget
└─ endpoint: "http://127.0.0.1:39122/health"
```

健康输出：

```text
Ok(true)
```

不健康输出：

```text
Ok(false)
```

检查失败：

```text
HealthError::CheckFailed(
    "health endpoint unreachable"
)
```

`Ok(false)` 是有效健康事实；`Err` 表示无法完成检查，两者都不能由 Probe 自己转换成重启或路由操作。

## 不负责什么

```text
HealthProbe 不负责
├─ 启动、停止或重启进程
├─ 修改 ProcessPlan
├─ 自己摘除 Route
├─ 决定恢复策略
├─ 生成健康检查地址
└─ 发布 Routable
```

Probe 只提供证据；Orchestrator 和 Route Attachment 根据证据执行状态迁移和 fail-closed 顺序。

## BDD 边界

```gherkin
Scenario: A routable runtime becomes unhealthy
  When HealthProbe reports unhealthy
  Then orchestration marks the workload unhealthy
  And Traffic is quarantined before exact detachment
  And HealthProbe does not mutate routing itself
```

## 停止条件

如果健康检查实现开始直接重启进程、操作 Router 或决定调度优先级，立即停止并交回对应 Owner。
