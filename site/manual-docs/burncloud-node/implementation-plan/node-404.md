---
title: "NODE-404：Stop / Crash / Restart / Logs"
slug: /burncloud-node/implementation-plan/node-404/
---

# NODE-404：Stop / Crash / Restart / Logs

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**功能依赖：NODE-403**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-404 要补齐模型进程的完整生命周期：主动停止、异常 crash、有限重启和 stdout/stderr 日志。这样 Node 关闭时不会残留模型进程，进程 crash 后也不会继续保持 READY。完成后，Process Manager 才真正对“模型进程从生到死”负责。

### 背景与动机（Why）

current `InferenceService` 已能 `kill()` Child 并设置 `Stopped`，stdout/stderr 也被设置为 piped；但当前原型没有完整 crash monitor、bounded restart policy 和日志生命周期。更关键的是，如果异常退出没有及时驱动状态变化，Router 未来可能继续把已经不存在的 Runtime 当成可用目标。

NODE-404 因此只负责**真实进程生命周期**，不做 Router 摘除本身；NODE-502 会消费这里的状态事实。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 主动 stop / Node shutdown 清理 | 不做多机恢复 |
| 监控 unexpected crash | 不做 GPU scheduler |
| 有边界的 restart policy | 不无限重启风暴 |
| 捕获 stdout / stderr 日志 | 不修改 Router 选择算法 |
| crash 后立即失去可用状态 | 不把日志系统变成大型 observability 项目 |

### 风险与安全网（Risk）

> 这是**进程资源治理**：最坏结果是 Runtime 停止并明确失败；不允许通过无限重启、吞掉 crash 或伪造 READY 来掩盖故障。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Process Manager 对 stop/crash/restart/logs 负完整责任？
2. 是否同意 restart 必须 bounded，不能形成重启风暴？
3. 是否确认 Router 联动仍留在 NODE-502，NODE-404 只提供真实状态？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
READY / STARTING process
   ├─ explicit stop → STOPPING → STOPPED
   ├─ unexpected exit → FAILED/UNHEALTHY
   │                     ↓ bounded policy
   │                  optional restart
   └─ stdout/stderr → owned runtime logs
```

### 2. Evidence

- current `InferenceService::stop_instance()` 能从 HashMap 取出 Child、`kill().await` 并设置 `Stopped`。
- current spawn 已将 stdout/stderr 设为 `Stdio::piped()`，但当前实现没有在该模块中形成完整日志消费合同。
- current statuses 主要在内存 HashMap 中，尚未形成 unexpected crash / bounded restart 的独立 lifecycle contract。

### 3. Entry / Starting Point

重新检查：

```text
NODE-402 Process Manager ownership
NODE-403 health state machine
crates/service/crates/inference/src/lib.rs :: stop_instance / process map
current logging infrastructure
Node shutdown plumbing from NODE-001
```

### 4. Reuse Targets / Do Not Recreate

Reuse：owned Child handles、Tokio process APIs、现有 tracing/logging 基础设施。  
Do Not Recreate：system-wide scheduler、new observability platform、Router health tracker。

### 5. Scope

#### Allowed

- graceful/forced stop policy；
- child exit observation；
- unexpected crash transition；
- bounded restart count/backoff policy；
- stdout/stderr drain/capture；
- Node shutdown child cleanup；
- lifecycle tests。

#### Avoid

- Local Channel availability mutation（NODE-502）；
- complex supervisor cluster；
- GPU/multi-model scheduler；
- multi-host failover；
- billing/auth/routing changes。

### 6. Behavior Contract

必须满足：

```text
explicit stop => process is not restarted unless contract explicitly says so
unexpected exit => READY cannot remain true
restart policy => finite attempts + bounded delay/window
restart exhaustion => terminal diagnosable failure
Node shutdown => owned children are cleaned up
logs => stdout/stderr are drained so pipes do not block child execution
```

Process Manager owns child lifecycle truth；Router 只消费该 truth。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
crash => keep READY
restart forever
stop failure => ignore and mark STOPPED
child output pipe => never drained
Node shutdown => orphan model processes
restart failure => silently spawn a different runtime
```

### 8. Impact / Invariants

```text
persistence: optional minimal restart metadata only if current design requires
external_calls: local process control only
billing/auth/routing: no direct mutation
process lifecycle: full child lifecycle ownership
logging: runtime stdout/stderr integration
```

Candidate invariant：**真实进程状态必须驱动 Runtime 可用状态。**

### 9. Dependencies

前置：`NODE-403`。  
后续：`NODE-502`。

### 10. Stop Conditions

STOP IF：需要无限 restart、需要 Router mutation 才能表达 crash、无法保证 child cleanup、日志方案要求重建全局 logging、或 scope 扩展到 GPU/multi-host scheduler。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] explicit stop 能结束 owned child 并进入 STOPPED。
- [ ] unexpected crash 能被观察并离开 READY。
- [ ] restart policy 有明确次数/窗口/退避边界。
- [ ] restart exhaustion 有终态和诊断。
- [ ] stdout/stderr 被安全消费/记录。
- [ ] Node shutdown 不残留 owned model processes。

### ✅ 边界保护

- [ ] 未实现 Router availability mutation。
- [ ] 未实现无限重启。
- [ ] 未引入 GPU scheduler / multi-host recovery。
- [ ] 未重建全局 observability/logging 平台。

### ✅ 回归与验证

- [ ] tests 覆盖 explicit stop、crash、restart success、restart limit、shutdown cleanup。
- [ ] crash 后 READY 不会残留。
- [ ] pipe capture 不导致子进程阻塞。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确 restart policy 与 shutdown ownership。
- [ ] 只通过分支 + Pull Request 合并。
