---
title: "ModelResolver Contract"
slug: /burncloud-node/contracts/model-resolver/
---

# `ModelResolver` Contract

```text
Owner: crates/supply/service-models
Status: Accepted / Framework Only
Source: crates/supply/service-models/src/resolver.rs
Fake: FakeModelResolver
```

## 唯一职责

根据逻辑模型名和机器可用的加速器内存，返回适合本机准备的模型事实，或者明确说明本机不支持。

```rust
async fn resolve(
    &self,
    request: ModelResolutionRequest,
) -> Result<ModelResolutionOutcome, ModelResolutionError>;
```

## 输入与输出

```text
ModelResolutionRequest
├─ model
└─ accelerator_memory_bytes
        ↓
ModelResolver
        ├─ Local(ResolvedModel)
        ├─ Unsupported(LocalModelUnsupported)
        └─ Err(ModelResolutionError)
```

`ResolvedModel` 拥有模型准备所需的 Supply 事实：模型名、Artifact 来源与摘要、Runtime 名称与版本。`Unsupported` 是正常业务结果，不是路由失败，也不是基础设施异常。

## 不负责什么

```text
ModelResolver 不负责
├─ 下载或校验 Artifact
├─ 安装 Runtime
├─ 生成进程参数
├─ 启动进程
├─ 判断 READY / Healthy
├─ 注册 Local Channel
└─ 决定请求最终路由到哪里
```

## 调用规则

只有 Orchestrator 在取得 `HardwareProfile` 后调用。成功返回 `ResolvedModel` 才能进入 Artifact 准备；返回 `Unsupported` 必须停止本地准备并保留现有远程路由行为。

## BDD 边界

```gherkin
Scenario: This machine has no compatible local variant
  Given a model demand and a hardware profile
  When ModelResolver returns Unsupported
  Then no artifact is prepared
  And no runtime is prepared
  And no local process is started
  And existing routing is not changed
```

## 停止条件

如果解析需要 Provider 售卖策略、客户余额、最终 Route 优先级或真实下载状态，立即停止：这些事实不属于 `ModelResolver`。

