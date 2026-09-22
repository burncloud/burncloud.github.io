---
title: "ProcessManager Contract"
slug: /burncloud-node/contracts/process-manager/
---

# `ProcessManager` Contract

```text
Owner: crates/platform/node
Status: Accepted / Framework Only
Source: crates/platform/node/src/contracts.rs
Fake: FakeProcessManager
```

## 唯一职责

根据调用者提供的 `ProcessSpec` 启动本地进程，并通过 `ProcessHandle` 管理该进程的停止。

```rust
async fn start(&self, spec: ProcessSpec) -> Result<ProcessHandle, ProcessError>;
async fn stop(&self, handle: ProcessHandle) -> Result<(), ProcessError>;
```

## 输入与输出

```text
ProcessSpec { program, args }
        ↓ start
ProcessHandle { pid }
        ↓ stop
Ok / ProcessError
```

## 具体示例

输入：

```text
ProcessSpec
├─ program: "/fake/runtime/llama.cpp/server"
└─ args
   └─ "/fake/artifacts/qwen-4b_fake.gguf"
```

成功输出：

```text
ProcessHandle
└─ pid: 42
```

启动失败：

```text
ProcessError::StartFailed(
    "process could not be started"
)
```

停止失败：

```text
ProcessError::StopFailed(
    "process could not be stopped"
)
```

`pid: 42` 是 Fake Receipt；取得 PID 只证明启动步骤成功，不证明服务已经 Ready。

## 不负责什么

```text
ProcessManager 不负责
├─ 理解模型或 Provider
├─ 选择 Runtime
├─ 拼装 Runtime 专用参数
├─ 下载任何文件
├─ 判断 READY / Healthy
├─ 注册路由
└─ 决定失败后的业务策略
```

它执行 `ProcessSpec`，但不解释 `ProcessSpec` 的业务含义。

## BDD 边界

```gherkin
Scenario: Start succeeds
  Given a complete ProcessSpec
  When ProcessManager starts it
  Then it returns a ProcessHandle
  And that receipt does not imply Ready, Healthy, or Routable
```

## 停止条件

如果 ProcessManager 需要根据 Runtime 名称、模型格式、客户或路由规则改变参数，说明 `RuntimeAdapter` 或上层策略存在缺口，应立即停止。
