---
title: "RuntimeAdapter Contract"
slug: /burncloud-node/contracts/runtime-adapter/
---

# `RuntimeAdapter` Contract

```text
Owner: crates/platform/node
Status: Accepted / Framework Only
Source: crates/platform/node/src/preparation.rs
Fake: FakeRuntimeAdapter
Production implementation: Not started
```

## 唯一职责

把已经准备好的 Runtime 和 Artifact 转换成完整、可执行但尚未执行的 `ProcessPlan`。

```rust
async fn plan(
    &self,
    runtime: &PreparedRuntime,
    artifact: &PreparedArtifact,
) -> Result<ProcessPlan, RuntimeAdapterError>;
```

## 输入与输出

```text
PreparedRuntime + PreparedArtifact
        ↓
RuntimeAdapter.plan(...)
        ├─ ProcessPlan
        │   ├─ ProcessSpec
        │   ├─ ReadinessTarget
        │   └─ local_endpoint
        └─ RuntimeAdapterError
```

## 为什么需要它

`RuntimePreparer` 只证明 Runtime 可用；`ProcessManager` 只执行 `ProcessSpec`。具体 Runtime 的启动格式必须被隔离在二者之间，不能泄漏进 Orchestrator。

## 不负责什么

```text
RuntimeAdapter 不负责
├─ 下载或安装 Runtime
├─ 下载或验证 Artifact
├─ 启动、停止或重启进程
├─ 发起 readiness / health 请求
├─ 注册或选择 Route
├─ 选择 Windows / Linux
└─ 在多个 Runtime 之间做业务策略选择
```

## 调用顺序

```text
PreparedRuntime 与 PreparedArtifact 都存在
        ↓
调用 RuntimeAdapter.plan(...)
        ↓
成功生成 ProcessPlan？
        │
        ├─ 否 → Failed → ProcessManager 不得调用
        └─ 是 → 先保存 Plan Receipt
                 ↓
              ProcessManager.start(plan.process)
```

## BDD 边界

```gherkin
Scenario: Framework uses the injected adapter
  Given PreparedRuntime and a verified PreparedArtifact
  When RuntimeAdapter creates a ProcessPlan
  Then the orchestrator stores that exact plan
  And ProcessManager receives only plan.process
  And probes consume plan.readiness
  And route attachment consumes plan.local_endpoint
```

## 修改规则

```text
需要编写真实 Runtime Adapter
        ↓
必须单独创建生产实现 Issue
        ↓
一个 Issue 只实现一种启动格式
        ↓
不得修改 Accepted Contract
```

如果现有 `ProcessPlan` 无法表达已证明的生产需求，停止实现并创建 `CONTRACT_GAP`；不能顺手扩大接口。

