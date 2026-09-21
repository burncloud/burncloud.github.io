---
title: "HardwareProbe Contract"
slug: /burncloud-node/contracts/hardware-probe/
---

# `HardwareProbe` Contract

```text
Owner: crates/platform/node
Status: Accepted / Framework Only
Source: crates/platform/node/src/contracts.rs
Fake: FakeHardwareProbe
```

## 唯一职责

检查本机并返回稳定、与 BurnCloud 业务无关的机器事实。

```rust
async fn inspect(&self) -> Result<HardwareProfile, HardwareProbeError>;
```

`HardwareProfile` 当前包含 CPU 线程、内存、可用磁盘以及加速器的类型、名称和显存。

## 输入与输出

```text
HardwareProbe.inspect()
        ├─ Ok(HardwareProfile)
        └─ Err(HardwareProbeError)
```

## 不负责什么

```text
HardwareProbe 不负责
├─ 选择模型 Variant
├─ 判断某模型是否可售
├─ 预留或调度 GPU
├─ 下载驱动或 Runtime
├─ 启动模型进程
└─ 决定路由和计费
```

## 调用规则

Orchestrator 可以把 `HardwareProfile` 中的稳定事实交给 Supply 的 `ModelResolver`。`HardwareProbe` 自己不得依赖 Model、Provider、Route、Billing 或 Tenant 语义。

## BDD 边界

```gherkin
Scenario: Hardware inspection succeeds
  When HardwareProbe inspects the machine
  Then it returns only machine-level facts
  And it does not select a model
  And it does not mutate runtime or routing state
```

## 停止条件

如果实现需要知道模型价格、客户身份、Provider 或 Route，说明职责已经越界，应停止并上升架构审查。

