---
title: "NODE-402：资源准入、端口分配与 Process Spawn"
slug: /burncloud-node/implementation-plan/node-402/
---

# NODE-402：资源准入、端口分配与 Process Spawn

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**功能依赖：NODE-401、NODE-103**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-402 要让 BurnCloud 在后台自动为 ProcessSpec 做最后的资源准入、分配内部端口并启动模型进程。用户不提供端口、不执行命令，也不管理 PID。并发启动必须避免两个模型同时把同一份可用 GPU / RAM 资源“各算一次”后一起 OOM。

### 背景与动机（Why）

自动化 Node 不能只在 Resolver 阶段看一次 VRAM 就认为永远可用。Variant 选择和真正 spawn 之间资源可能已经变化，因此 Process Manager 需要在启动前做一次轻量的 actual admission，并以并发安全方式占用/确认资源。v0.1 不需要复杂 GPU Scheduler，但必须避免明显 race。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 自动分配内部端口 | 不让用户指定内部端口 |
| ProcessSpec → spawn | 不让用户执行 llama-server |
| spawn 前重新确认关键资源 | 不做复杂 GPU scheduler |
| 并发安全的最小 admission | 不做多机调度 |
| 持有 Child/PID truth | 不把 spawn 当 READY |

### 风险与安全网（Risk）

> v0.1 可以保守准入，但不能用过度调度换来复杂度；不确定资源时 fail closed，不能同时启动多个“理论上都能跑”的模型直到 OOM。

### 审批者关注点（Reviewer Focus）

1. 是否同意启动完全由 BurnCloud 自动完成？
2. 是否同意 spawn 前必须做一次 current-resource admission？
3. 是否同意 v0.1 只需要最小并发保护，不建设完整 GPU Scheduler？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
ProcessSpec
+ current ResourceSnapshot
       ↓
atomic/minimal admission
       ↓
internal port allocation
       ↓
Command::spawn
       ↓
STARTING + owned Child
```

### 2. Evidence

current InferenceService 由调用方提供 port/gpu_layers 并直接 spawn；current main 尚无自动端口 + concurrent resource admission contract。

### 3. Reuse Targets / Do Not Recreate

Reuse：Tokio process APIs、current hardware/resource view、existing process ownership patterns。  
Do Not Recreate：cluster scheduler、GPU allocator platform、Runtime adapter、Router registration。

### 4. Scope

#### Allowed

- internal port allocation；
- final pre-spawn resource check；
- minimal reservation/admission lock or equivalent race prevention；
- process spawn；
- Child/PID ownership；
- STARTING transition；
- spawn failure cleanup；
- targeted concurrency tests。

#### Avoid

- readiness/health decision（NODE-403）；
- restart/stop policy（NODE-404）；
- Local Channel registration；
- multi-host scheduling；
- sophisticated GPU packing/fragmentation scheduler；
- user-visible manual port/PID controls。

### 5. Behavior Contract

```text
spawn requires valid ProcessSpec
spawn requires current admission success
port is allocated internally
successful spawn => STARTING, never READY
failed spawn => no leaked reservation/port/Child state
concurrent admissions must not overcommit the same observed capacity by race
```

v0.1 可以采用保守策略；具体策略在 READY Audit / Task Contract 基于真实资源模型确定。

### 6. Failure / Forbidden Fallbacks

结构化失败至少支持：

```text
INSUFFICIENT_RUNTIME_RESOURCE
PORT_ALLOCATION_FAILED
PROCESS_SPAWN_FAILED
ADMISSION_CONFLICT
```

禁止：

```text
spawn success => READY
admission failure => spawn anyway
port conflict => ask user to choose port
resource race => rely on OOM as scheduler
spawn failure => silently start Provider runtime
```

### 7. Impact / Invariants

```text
persistence: no new business persistence required
external_calls: local process spawn
billing/auth/routing: none
process lifecycle: owns Child/PID from spawn onward
```

Candidate invariants：
- **Process Spawned != Model READY.**
- **Concurrent managed spawns must not knowingly overcommit the same resource facts by race.**

### 8. Dependencies

前置：NODE-401、NODE-103。  
后续：NODE-403、NODE-404、NODE-504。

### 9. Stop Conditions

STOP IF：实现需要复杂 GPU scheduler 才能成立、无法防止明显并发 overcommit、需要用户提供 port/PID、或必须修改 Router/Billing/Auth。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] ProcessSpec 可自动分配端口并 spawn。
- [ ] 用户无需提供 port/PID/command。
- [ ] spawn 前进行 current-resource admission。
- [ ] 并发 admission 不会明显重复占用同一可用容量。
- [ ] spawn 成功只进入 STARTING。
- [ ] spawn 失败释放临时资源/端口/状态。

### ✅ 边界保护

- [ ] 未建设复杂 GPU Scheduler。
- [ ] 未实现 readiness / Router registration。
- [ ] 未引入手工启动流程。

### ✅ 回归与验证

- [ ] tests 覆盖 port allocation、spawn failure、resource insufficient、concurrent admission conflict。
- [ ] `Process Spawned != Model READY` 始终成立。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确最小 admission policy。
- [ ] 只通过分支 + Pull Request 合并。
