---
title: "NODE-402：内部端口分配与 Process Spawn"
slug: /burncloud-node/implementation-plan/node-402/
---

# NODE-402：内部端口分配与 Process Spawn

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**功能依赖：NODE-401**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-402 要让 Process Manager 接收 `ProcessSpec`，自动分配本地内部端口并真正启动模型进程。用户不需要再手工指定 port、PID 或直接执行 `llama-server` 命令。完成后，Node 会明确拥有 Child/PID 生命周期，但“进程已经启动”仍然绝不能等于“模型已经 READY”。

### 背景与动机（Why）

当前 `InferenceConfig` 要求调用方提供 `port`，`InferenceService` 直接 `Command::spawn()` 并把 `Child` 存在 HashMap 里。这能工作，但把内部端口、命令拼装和进程 ownership 全部暴露在同一个服务里。

NODE-402 只把**进程真正启动起来并持有它**。Readiness 和持续 health 留给 NODE-403，crash/restart/logs 留给 NODE-404，Router registration 留给 NODE-501。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 自动分配内部 loopback 端口 | 不让用户手工管理 PID |
| 接收 ProcessSpec 并 spawn | 不把 spawn success 当 READY |
| 持有 Child / PID / handle | 不注册 Router / Channel |
| 明确处理端口冲突与 spawn failure | 不实现持续 health / restart |
| 提供 stop 所需基础 ownership | 不改 Provider routing |

### 风险与安全网（Risk）

> 这是**受控子进程创建**：最坏结果应该是 spawn 明确失败并清理资源；绝不能出现“进程没准备好但已经对 Router 可见”的情况。

### 审批者关注点（Reviewer Focus）

1. 是否同意内部端口由 Node 管理，不暴露给用户配置主流程？
2. 是否同意 Process Manager 是 Child/PID 的唯一 owner？
3. 是否确认 `Spawned != READY`，本 Issue 不允许注册 Local Channel？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
ProcessSpec
    ↓
allocate internal loopback port
    ↓
materialize command
    ↓
spawn child process
    ↓
STARTING / spawned handle
    ↓
NODE-403 readiness
```

### 2. Evidence

- current `InferenceService` 使用 `tokio::process::Command` 启动 llama-server，并在 `HashMap<String, Child>` 中持有进程。
- current `InferenceConfig` 由调用方传入 `port`，说明当前原型尚未形成内部 port ownership contract。
- `InferenceService` 当前只有在 health check 通过后才标记 `Running`，这证明“spawn 与可用”已经有初步区分，NODE-402 必须保持并强化该边界。

### 3. Entry / Starting Point

重新检查：

```text
NODE-401 ProcessSpec
crates/service/crates/inference/src/lib.rs :: start_instance
current process ownership / shutdown helpers
available port allocation utilities in main
```

### 4. Reuse Targets / Do Not Recreate

Reuse：Tokio process primitives、现有 inference process knowledge、workspace error/lint conventions。  
Do Not Recreate：Runtime argument logic、readiness checker、Router registration。

### 5. Scope

#### Allowed

- internal loopback port allocation；
- ProcessSpec materialization with allocated port；
- `Command::spawn()`；
- Child/PID/handle ownership；
- STARTING/spawned state；
- spawn failure cleanup；
- basic explicit stop primitive needed for ownership；
- targeted process fixture tests。

#### Avoid

- READY transition（NODE-403）；
- ongoing crash/restart/log lifecycle（NODE-404）；
- Local Channel registration；
- model download / Resolver；
- public network exposure of runtime port；
- GPU scheduler。

### 6. Behavior Contract

Inputs：validated `ProcessSpec`。  
Output：owned spawned process handle + allocated internal endpoint information + STARTING state。

必须满足：

```text
port is loopback/internal unless explicitly authorized otherwise
port allocation collision => retry/fail by explicit bounded policy
spawn success => STARTING, never READY
spawn failure => no leaked authoritative process state
one process owner => Process Manager
```

### 7. Failure / Forbidden Fallbacks

禁止：

```text
port conflict => use public 0.0.0.0 random exposure
spawn failure => mark READY anyway
spawn failure => switch runtime/provider silently
missing process handle => reconstruct ownership by PID guessing
spawn => immediately register Local Channel
use unwrap/expect in prohibited paths to force progress
```

### 8. Impact / Invariants

```text
persistence: process state only if later contract explicitly requires; no schema assumed
external_calls: local process spawn
billing/auth/routing: none
network: internal loopback runtime endpoint
process lifecycle: yes — spawn/ownership foundation
```

必须保持：
- `INV-WORKSPACE-002` — `unwrap_used = deny`；
- Candidate：`Process Spawned != Model READY`。

### 9. Dependencies

前置：`NODE-401`。  
后续：`NODE-403`、`NODE-404`。

### 10. Stop Conditions

STOP IF：需要把 runtime port 暴露公网、需要 spawn 后直接改 Router、无法确定 Child/PID ownership、必须依赖 PID 猜测恢复、或 scope 扩展到 readiness/restart/scheduling。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] Process Manager 能从 ProcessSpec 启动模型进程。
- [ ] 内部端口由 Node 自动分配并避免明显冲突。
- [ ] Child/PID/handle ownership 唯一且可查询。
- [ ] spawn 后状态仍是 STARTING / 非 READY。
- [ ] spawn failure 不残留伪造运行状态。

### ✅ 边界保护

- [ ] 未注册 Local Channel。
- [ ] 未实现 readiness/ongoing health/restart 策略。
- [ ] 未把 internal runtime port 作为新的公开 API。
- [ ] 未加入 GPU scheduler / 多机逻辑。

### ✅ 回归与验证

- [ ] tests 覆盖正常 spawn、binary 不存在、端口冲突/不可用、stop 基础路径。
- [ ] 有断言证明 spawn success 不等于 READY。
- [ ] `INV-WORKSPACE-002` 保持成立。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 锁定真实 port allocation 和 Child ownership 实现路径。
- [ ] 只通过分支 + Pull Request 合并。
