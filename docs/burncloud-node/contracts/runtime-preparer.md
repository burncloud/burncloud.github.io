---
title: "RuntimePreparer Contract"
slug: /burncloud-node/contracts/runtime-preparer/
---

# `RuntimePreparer` Contract

```text
Owner: crates/platform/node
Status: Accepted / Framework Only
Source: crates/platform/node/src/preparation.rs
Fake: FakeRuntimePreparer
```

## 唯一职责

根据 `RuntimeRequest` 准备或定位本机可使用的 Runtime，并返回可执行入口 Receipt。

```rust
async fn prepare(
    &self,
    request: RuntimeRequest,
) -> Result<PreparedRuntime, RuntimePrepareError>;
```

## 输入与输出

```text
RuntimeRequest
├─ runtime
└─ version
        ↓
RuntimePreparer
        ├─ PreparedRuntime { executable }
        └─ RuntimePrepareError
```

## 具体示例

输入：

```text
RuntimeRequest
├─ runtime: "llama.cpp"
└─ version: Some("fake-v0")
```

成功输出：

```text
PreparedRuntime
└─ executable: "/fake/runtime/llama.cpp/server"
```

失败输出：

```text
RuntimePrepareError::PrepareFailed(
    "requested runtime version is unavailable"
)
```

示例中的 Runtime 名称、版本和路径不构成生产默认值；成功输出也不代表进程已经启动。

## 不负责什么

```text
RuntimePreparer 不负责
├─ 选择模型 Artifact
├─ 生成模型启动参数
├─ 分配服务端口
├─ 生成 readiness endpoint
├─ 启动或停止进程
├─ 检查健康
└─ 选择 Windows / Linux 组合策略
```

安装、查找、版本校验可以属于生产实现，但 `PreparedRuntime` 只证明可执行入口已经准备好，不证明进程已运行。

## BDD 边界

```gherkin
Scenario: Runtime preparation succeeds
  When RuntimePreparer prepares a runtime request
  Then it returns the executable receipt
  And it does not construct the model launch command
  And it does not start a process
```

## 停止条件

如果实现开始理解模型路径、服务端口、健康地址或路由规则，立即停止；这些分别属于 `RuntimeAdapter`、Probe 和 Route Attachment。
