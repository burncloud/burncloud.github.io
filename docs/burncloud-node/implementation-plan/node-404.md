---
title: "NODE-404：自动 Stop / Crash / Restart / Logs"
slug: /burncloud-node/implementation-plan/node-404/
---

# NODE-404：自动 Stop / Crash / Restart / Logs

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**功能依赖：NODE-403**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-404 要让模型进程从启动后到退出都由 BurnCloud 自动托管：Node shutdown 自动清理，异常 crash 自动离开 READY，允许有边界的重启，并持续消费 stdout/stderr。用户不需要“停止模型”或管理 PID。v0.1 不要求复杂的空闲驱逐策略，但绝不能留下孤儿进程或无限重启风暴。

### 背景与动机（Why）

在 demand-driven 模式下，用户不会进入管理页手工 stop。谁启动进程，谁就必须负责在 Node 退出、Runtime crash 或健康失效时正确收尾。current InferenceService 已有 Child handle 和 stop prototype，但还缺完整 supervisor semantics。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Node shutdown 自动清理 | 不要求用户手工 stop |
| unexpected crash detection | 不做多机恢复 |
| bounded restart | 不无限重启 |
| stdout/stderr drain + diagnostics | 不建大型 observability 平台 |
| crash 后立即失去 READY truth | 不直接修改 Router availability |

### 风险与安全网（Risk）

> 自动托管的底线是“真实状态优先”：进程死了就必须承认死了，不能为了看起来稳定而保留 READY 或反复无限拉起。

### 审批者关注点（Reviewer Focus）

1. 是否同意用户不承担 stop/cleanup 责任？
2. 是否同意 restart 必须 bounded？
3. 是否确认 Router 摘除仍由 NODE-502 消费状态完成？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
STARTING / READY process
   ├─ Node shutdown → STOPPING → STOPPED
   ├─ explicit internal replacement/stop policy → STOPPED
   ├─ unexpected exit → FAILED/UNHEALTHY
   │                     ↓ bounded policy
   │                  optional restart
   └─ stdout/stderr → runtime diagnostics
```

### 2. Evidence

current InferenceService 可 `kill().await` Child，stdout/stderr 已 piped，但没有完整 crash monitor、bounded restart 和 automatic shutdown ownership contract。

### 3. Reuse Targets / Do Not Recreate

Reuse：owned Child handles、Tokio process APIs、existing tracing/logging、NODE-001 shutdown plumbing。  
Do Not Recreate：cluster supervisor、new observability platform、Router health tracker。

### 4. Scope

#### Allowed

- shutdown cleanup；
- internal stop/replacement policy；
- child exit observation；
- crash transition；
- bounded restart count/backoff；
- stdout/stderr drain/capture；
- lifecycle diagnostics；
- tests。

#### Avoid

- user-required manual stop workflow；
- Local Channel mutation（NODE-502）；
- GPU scheduler；
- multi-host recovery；
- billing/auth/routing changes；
- idle eviction unless separately approved by v0.1 policy。

### 5. Behavior Contract

```text
Node shutdown => all owned children cleaned up
unexpected exit => READY cannot remain true
restart => finite attempts + bounded delay/window
restart exhaustion => terminal diagnosable failure
logs => pipes continuously drained
manual user action is not required for normal lifecycle
```

v0.1 可以保持 READY 模型常驻直到 Node shutdown / crash / replacement / explicit internal resource policy；不要求本 Issue 设计复杂 idle unload。

### 6. Failure / Forbidden Fallbacks

禁止：

```text
crash => keep READY
restart forever
stop failure => mark STOPPED anyway
stdout/stderr pipe => never drained
Node shutdown => orphan child
restart failure => silently launch a different runtime
normal operation => require user to kill PID manually
```

### 7. Impact / Invariants

```text
persistence: minimal lifecycle metadata only if justified
external_calls: local process control
billing/auth/routing: no direct mutation
process lifecycle: full ownership after spawn
```

Candidate invariant：**BurnCloud owns cleanup for every managed process it starts.**

### 8. Dependencies

前置：NODE-403。  
后续：NODE-502、NODE-504。

### 9. Stop Conditions

STOP IF：需要无限 restart、需要 Router mutation 才能表达 crash、无法保证 child cleanup、日志方案要求重建全局 logging、或正常生命周期仍依赖用户手工管理 PID。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] Node shutdown 自动结束 owned children。
- [ ] unexpected crash 被观察并离开 READY。
- [ ] restart policy 有明确次数/窗口/退避边界。
- [ ] restart exhaustion 有终态诊断。
- [ ] stdout/stderr 被安全消费。
- [ ] 用户无需手工 stop / kill PID。

### ✅ 边界保护

- [ ] 未实现 Router availability mutation。
- [ ] 未实现无限重启。
- [ ] 未引入 GPU scheduler / multi-host recovery。
- [ ] 未强行加入复杂 idle eviction。

### ✅ 回归与验证

- [ ] tests 覆盖 shutdown、crash、restart success、restart limit、cleanup。
- [ ] crash 后 READY 不残留。
- [ ] pipe capture 不阻塞 child。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确 restart/shutdown ownership。
- [ ] 只通过分支 + Pull Request 合并。


---

## 第四层：人类验收（Human Acceptance）

> 本节由 [Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/) 生成。机器测试、CI 或 AI Review 不能替代这里的人工验收。

### NODE-404 — Stop / Crash / Restart / Logs

**验收者：** Runtime 工程师 + 运维负责人。

**人工步骤：**
1. 正常停止一个 managed Runtime，确认进程退出。
2. 强制杀掉一个 managed Runtime，观察 crash 检测和 restart policy。
3. 连续制造 crash 达到重启上限。
4. 查看 runtime logs 是否足够定位 exit code/失败原因。

**人类通过标准：** BurnCloud 对自己启动的模型进程负责清理；crash 可检测；restart 有上限；日志可诊断。

**人工判定失败：** Node 退出后 orphan process、无限 crash loop、失败被吞掉、或日志找不到具体 runtime/process 身份。

**建议证据：** process list 前后对比 + restart_count + 日志片段。
