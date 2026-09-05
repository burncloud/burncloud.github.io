---
title: "NODE-403：Readiness / Health 状态机"
slug: /burncloud-node/implementation-plan/node-403/
---

# NODE-403：Readiness / Health 状态机

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**功能依赖：NODE-402**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-403 要建立模型进程从 `STARTING` 到 `READY / FAILED / UNHEALTHY` 的明确状态机。只有 readiness 真正通过的 Runtime 才能被后续 Local Channel 暴露给 Router；“进程已经 spawn”绝不能被当成“模型已经能接请求”。完成后，Node 会有可靠的可用性事实，而不是靠进程是否存在来猜。

### 背景与动机（Why）

current `InferenceService` 已经会轮询 llama-server 的 `/v1/models`，健康检查成功后才把状态从 `Starting` 改为 `Running`。这证明现有原型已经认识到 readiness 的必要性，但它仍缺少更完整的状态合同，例如启动超时、进程提前退出、运行后 health 变坏以及这些状态如何被上层消费。

NODE-403 的职责是把这件事变成**明确、可测试的状态机**。它不负责重启进程，也不直接修改 Router 数据模型；Router 联动属于 NODE-502。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 定义 STARTING / READY / FAILED / UNHEALTHY | 不把 spawn success 当 READY |
| 实现 readiness polling / timeout | 不负责 bounded restart |
| 实现持续 health 判断所需最小机制 | 不直接注册/摘除 Router |
| 处理启动时进程提前退出 | 不修改 Billing / Auth |
| 给上层提供唯一 Runtime health truth | 不混入 Artifact validation |

### 风险与安全网（Risk）

> 这是**可用性安全门**：任何不确定状态都不能被提升成 READY；最坏结果是本地模型暂时不可路由，而不是把未准备好的进程交给真实流量。

### 审批者关注点（Reviewer Focus）

1. 是否确认 `Spawned != READY` 是硬约束？
2. 是否同意 readiness 与 ongoing health 都由 Process/Runtime 状态机提供事实，而不是 Router 自己探测？
3. 是否同意 Router 联动和重启策略分别留给 NODE-502 / NODE-404？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
spawned process
      ↓
STARTING
      ↓ readiness success
READY
      ↓ health failure
UNHEALTHY

STARTING ─ timeout / early exit ─→ FAILED
```

### 2. Evidence

- current `InferenceService` 已定义 `Stopped / Starting / Running / Failed(String)` 状态。
- `wait_for_health_check()` 当前每秒轮询 `http://127.0.0.1:<port>/v1/models`，最多 60 次，成功后才标记 `Running`。
- current prototype 尚无独立 `UNHEALTHY` 状态和持续 health contract；Local Channel 注册也直接跟在初始 health success 后，职责仍有耦合。

### 3. Entry / Starting Point

重新检查：

```text
NODE-402 spawned process handle
NODE-401 readiness/health semantics in ProcessSpec
crates/service/crates/inference/src/lib.rs :: wait_for_health_check
current process exit observation APIs
```

### 4. Reuse Targets / Do Not Recreate

Reuse：current `/v1/models` readiness knowledge、reqwest/Tokio timing primitives、Process Manager ownership。  
Do Not Recreate：Router health tracker、restart manager、Artifact validator。

### 5. Scope

#### Allowed

- Runtime/process state enum；
- readiness polling；
- timeout / backoff policy；
- early-exit detection during startup；
- minimal ongoing health transitions；
- state observation API；
- deterministic state-machine tests。

#### Avoid

- restart policy（NODE-404）；
- Local Channel registration/removal（NODE-501/502）；
- Router state mutation；
- Artifact checksum；
- process spawn implementation beyond NODE-402 ownership。

### 6. Behavior Contract

最小状态语义：

```text
STARTING   = child exists/starting, not routable
READY      = readiness passed and current health acceptable
FAILED     = startup cannot complete / process terminates before ready / terminal startup error
UNHEALTHY  = was operational but current health is not acceptable
STOPPED    = intentionally not running (if shared lifecycle enum includes it)
```

只有 `READY` 可被 NODE-501 视为注册前置条件。

State transition 必须由真实 process/health evidence 驱动，不由 Router candidate status 反向决定。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
spawned => READY
readiness timeout => keep STARTING forever
non-2xx health => assume ready because port is open
early child exit => ignore and continue polling
UNHEALTHY => silently mark READY to preserve traffic
health checker => directly mutate Router channels
```

### 8. Impact / Invariants

```text
persistence: none required unless current architecture proves need
external_calls: loopback readiness/health probes only
billing/auth/routing: no direct mutation
process lifecycle: observes owned child state
```

Candidate invariant：**Process Spawned != Model READY。**

### 9. Dependencies

前置：`NODE-402`。  
后续：`NODE-404`、`NODE-501`、`NODE-502`。

### 10. Stop Conditions

STOP IF：需要 Router mutation 才能表达 health、需要 restart 才能完成状态机、需要把 open port 当 READY、无法观察 owned child 真实退出、或 current main 已有 authoritative health state 与本合同冲突。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] STARTING / READY / FAILED / UNHEALTHY 语义明确。
- [ ] readiness success 才能进入 READY。
- [ ] timeout / early exit 进入明确失败路径。
- [ ] 运行后 health failure 可以离开 READY。
- [ ] 上层能查询/订阅 authoritative Runtime health state。

### ✅ 边界保护

- [ ] 未实现 restart policy。
- [ ] 未直接注册、摘除或修改 Router Channel。
- [ ] 未用 Artifact validation 替代 Runtime health。
- [ ] 未把 spawn success 当 READY。

### ✅ 回归与验证

- [ ] tests 覆盖正常 ready、timeout、非成功状态、连接失败、early exit、READY→UNHEALTHY。
- [ ] 有明确测试锁住 `Spawned != READY`。
- [ ] current local inference happy path 仍能达到 READY。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确 readiness endpoint / timeout / health ownership。
- [ ] 只通过分支 + Pull Request 合并。


---

## 第四层：人类验收（Human Acceptance）

> 本节由 [Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/) 生成。机器测试、CI 或 AI Review 不能替代这里的人工验收。

### NODE-403 — Readiness / Health

**验收者：** 产品负责人 + Runtime 工程师。

**人工步骤：**
1. 启动一个加载需要时间的模型，观察 `spawned → starting → ready` 过程。
2. 在 READY 前立即发真实请求，确认不会被路由进去。
3. 模拟 health endpoint 失败/超时。

**人类通过标准：** Readiness 成功后才 READY；Health 失败会明确降级/失败；真实流量永不进入未 READY Runtime。

**人工判定失败：** PID 创建即 READY、固定 sleep 代替 readiness、health 失败仍保持 routable。

**建议证据：** 状态时间线 + READY 前请求结果 + health failure 记录。
