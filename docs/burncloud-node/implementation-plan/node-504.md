---
title: "NODE-504：Model Demand Reconciliation"
slug: /burncloud-node/implementation-plan/node-504/
---

# NODE-504：Model Demand Reconciliation

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Local Channel Integration**  
**功能依赖：NODE-201~204、NODE-301~303、NODE-400~404、NODE-501~502、NODE-003**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须确认全部前置能力已真实存在，并基于当时 `burncloud/burncloud/main` 重新做 Evidence Audit、通过 READY Gate。

### TL;DR

NODE-504 是 BurnCloud Node 自动化体验的核心：当真实 `/v1` 请求出现 `model=qwen-4b` 时，它把这个“需求”异步收敛成本地 READY 能力。当前请求仍由现有 Router 根据现实情况选择 Local 或 Provider；Reconciler 不路由请求，只负责后台 `Resolve → Prepare → Runtime → READY → Local Channel`。相同模型的 1000 个并发请求也只能产生一条本地准备链。

### 背景与动机（Why）

前面的 Issue 可以让 BurnCloud“有能力”下载、启动和注册本地模型，但如果还需要用户先点击下载、再点击启动，那么产品仍然是传统模型管理器，而不是 BurnCloud Node。

用户真正声明的是意图：

```text
model = qwen-4b
```

BurnCloud 应自动管理现实：

```text
现在有没有 Local？
Provider 能不能先服务？
本机能不能跑？
该下载哪个 Variant？
下载是否已在进行？
何时启动？
什么时候 READY？
什么时候注册 Local Channel？
失败原因是什么？
```

这需要一个薄的 orchestration / reconciliation 层，但它绝不能演变成第二个 Router。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 观察真实 model demand | 不改变 Router scoring/failover |
| 相同模型需求去重 | 不在请求线程同步下载 |
| 驱动 Resolve → Prepare → Runtime → READY | 不自己实现 Downloader/Process Manager |
| 保留 machine-readable progress/failure state | 不伪造 READY |
| Node 重启后清理 stale local execution state | 不自动恢复不存在的新需求为永久 warm-set |
| no-route 时映射 MODEL_PREPARING / blocked diagnosis | 不绕过 existing Server/Auth/Billing |

### 风险与安全网（Risk）

> Reconciler 可以“协调”，但不能“拥有所有东西”。任何一步必须调用已有责任模块；如果实现开始复制 Resolver、Download、Process 或 Router 逻辑，就已经越界。

### 审批者关注点（Reviewer Focus）

1. **是否同意 `/v1` 中的 model demand 自动触发后台本地准备？**
2. **是否同意当前请求与后台准备解耦：Provider 能服务就立即服务，不等下载？**
3. **是否同意相同 model demand 必须严格去重，并且 Reconciler 不能成为第二个 Router？**

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
Observed model demand
        ↓
canonicalize / dedup
        ↓
Local READY?
  ├─ yes → no-op
  └─ no
       ↓
active reconciliation?
  ├─ yes → observe existing state
  └─ no
       ↓
Resolve
       ↓
Prepare Artifact
       ↓
Ensure Runtime
       ↓
Process Spawn
       ↓
Readiness / Health
       ↓
READY
       ↓
Local Channel registration
```

### 2. Current-request routing remains separate

Reconciler **不得决定当前请求走哪里**。

```text
/v1 request
     ↓
Existing ModelRouter
  ├─ Local READY candidate
  └─ Provider candidate
```

并行：

```text
same request model identity
        ↓
non-blocking demand signal
        ↓
NODE-504
```

如果 Provider 可用，当前请求照常走 Provider。  
如果没有任何 serving candidate，但 NODE-504 已接受并正在准备，则 request boundary 可将“无当前 route”映射为 `MODEL_PREPARING`。

### 3. Evidence

- existing ModelRouter 已负责 Channel candidate / availability / failover；不需要为本地准备新增 route engine。
- current InferenceService 已证明 Local Runtime READY 后可注册 Channel/Ability。
- NODE-201~204、301~303、400~404、501~502 分别提供 Resolver、Preparation、Runtime、Process 与 Channel 能力。
- current plan 尚缺把真实 model request 自动连接到这些能力的 orchestration contract。

### 4. Entry / Starting Point

READY Audit 必须重新确定最小 demand observation 点，优先选择现有 data-plane request path 中**不改变 Router 选择算法**的位置。

候选调查点：

```text
existing /v1 request model extraction
existing Router invocation boundary
route-miss/error mapping boundary
NodeContext / Node Core background task facilities
```

不得预先假设必须修改 ModelRouter 内部。

### 5. Reuse Targets / Do Not Recreate

#### Reuse

- canonical model identity / alias resolution；
- NODE-203/204 Resolver contract；
- NODE-301~303 Preparation；
- NODE-400~404 Runtime / Process；
- NODE-501~502 Local Channel integration；
- existing ModelRouter for serving decisions；
- existing tracing/events/background task infrastructure where available。

#### Do Not Recreate

```text
DemandRouter
LocalRouter
NodeDownloader
NodeProcessManager2
second model state database
request-local download pipeline
```

### 6. Reconciliation State Contract

最小状态建议：

```text
IDLE / ABSENT
RESOLVING
BLOCKED
PREPARING
VERIFYING
RUNTIME_PREPARING
STARTING
READY
FAILED
```

状态必须携带结构化 diagnosis / cause when applicable。

可能的 blocked/failure reasons：

```text
MODEL_UNKNOWN
NO_COMPATIBLE_VARIANT
INSUFFICIENT_VRAM
INSUFFICIENT_RAM
INSUFFICIENT_DISK
RUNTIME_UNSUPPORTED_PLATFORM
RUNTIME_UNAVAILABLE
ARTIFACT_SOURCE_UNAVAILABLE
DOWNLOAD_FAILED
VERIFICATION_FAILED
PROCESS_SPAWN_FAILED
READINESS_FAILED
```

### 7. Demand Identity / Dedup Contract

必须明确 demand key，至少基于 canonical model identity；如果未来 execution profile 会改变 Artifact/Runtime identity，需在 READY Audit 中扩展 key。

硬约束：

```text
N concurrent demands for same demand key
        ↓
<= 1 active reconciliation pipeline
```

重复 demand：

- 不新建下载；
- 不新建进程；
- 不创建重复 Local Channel；
- 只更新/观察当前 reconciliation state。

### 8. Request-visible Behavior

#### Local READY

Reconciler no-op；现有 Router 正常选 Local。

#### Local not READY + Provider available

```text
current request => Provider response
background => reconciliation continues
```

不得给正常成功响应附加失败语义；本地准备的 blocked/failed 原因记录为 Node diagnostics/state。

#### No serving Provider + preparation active/accepted

返回稳定错误合同，例如：

```text
HTTP 503
code = MODEL_PREPARING
model = canonical model
state = PREPARING | VERIFYING | STARTING | ...
Retry-After = optional policy
```

#### No serving Provider + local impossible

将 authoritative diagnosis 映射为稳定 client error；不能退化为 generic model-not-found。

### 9. Startup Reconciliation

Node restart 后，内存 Child/PID truth 不可恢复为“仍然 READY”。NODE-504 在启动时必须协助确保：

```text
stale Local Channel + no real READY process => not routable / cleanup
persisted PREPARING download => delegate to existing DownloadManager recovery
stale runtime state => re-evaluate actual state
new model process => only start when current demand / approved warm policy requires
```

v0.1 默认不要求持久化无限“曾经请求过的模型”并在每次开机全部自动 warm。产品默认是 demand-driven；额外 warm-set 属于后续策略。

### 10. Side Effects / Ownership

NODE-504 owns：

- model demand observation/normalization；
- in-flight reconciliation registry；
- state progression coordination；
- dedup；
- calling existing subsystem contracts；
- mapping reconciliation state to diagnostics；
- startup stale-state reconciliation orchestration。

NODE-504 does not own：

- Router selection；
- Variant selection implementation；
- file download implementation；
- runtime binary implementation；
- Child lifecycle mechanics；
- Channel storage semantics；
- Billing/Auth decisions。

### 11. Failure / Forbidden Fallbacks

禁止：

```text
request => wait synchronously until full model download
100 requests => 100 preparation pipelines
Provider success => stop/cancel local preparation by default
Resolver failure => choose arbitrary smaller GGUF
Download failure => mark READY
Process spawn => mark READY before readiness
no route => bypass Router and call llama directly
local blocked => change Provider priority/failover
restart => trust stale persisted READY without real process health
```

### 12. Impact / Invariants

```text
persistence: only minimal reconciliation/state facts if necessary; reuse existing model/download/channel state
external_calls: through delegated Preparation/Runtime only
billing_usage_quota: unchanged
auth_authorization: unchanged
routing_provider: unchanged selection semantics
process_lifecycle: delegated
```

新增候选 invariants：

- **Model demand is a signal, not a synchronous download command.**
- **One demand key has at most one active reconciliation pipeline.**
- **Reconciler never replaces ModelRouter.**
- **Only READY Runtime may yield routable Local Channel.**

### 13. Dependencies

前置：

```text
NODE-003
NODE-201~204
NODE-301~303
NODE-400~404
NODE-501~502
```

后续：NODE-503 final E2E。

### 14. Stop Conditions

```text
STOP IF:
- implementation requires moving download/spawn logic into ModelRouter
- demand observation cannot be added without changing Router selection semantics
- identical demands cannot be deduplicated reliably
- current request must block for large download to make feature work
- stale local state cannot be made fail-closed after restart
- Provider/Auth/Billing semantics must change
- an INV-* must be weakened without architecture approval
```

触发后：

```text
SCOPE / ARCHITECTURE CONFLICT DETECTED
No out-of-scope code changed.
Evidence: ...
Conflict: ...
Decision required: ...
```

---

## 第三层：验收层（Definition of Done）

### ✅ Demand 观察与去重

- [ ] `/v1` 的 model identity 可以非阻塞地产生 model demand。
- [ ] demand 被 canonicalize。
- [ ] N 个相同 demand &lt;= 1 个 active reconciliation pipeline。
- [ ] 重复 demand 不产生重复下载、Runtime 或 Channel。

### ✅ 自动收敛

- [ ] ABSENT model 可自动进入 Resolve。
- [ ] Resolve 成功后自动进入 Preparation。
- [ ] READY Artifact 后自动进入 Runtime/Process。
- [ ] Readiness/Health 成功后自动注册 Local Channel。
- [ ] 用户不需要手工 download/start/stop。

### ✅ 当前请求行为

- [ ] Provider 可用时当前请求不等待 Local Preparation。
- [ ] Provider 成功响应与后台本地准备可并行。
- [ ] 无 serving candidate 且正在准备时返回 `MODEL_PREPARING`。
- [ ] 无 serving candidate 且本地不可行时返回结构化 root cause。
- [ ] Reconciler 不直接选择当前请求 Channel。

### ✅ 生命周期与恢复

- [ ] Node restart 后 stale READY/Channel 不会被直接信任。
- [ ] 没有真实 READY process 的 Local Channel fail closed。
- [ ] existing DownloadManager 的 incomplete recovery 可继续被复用。
- [ ] v0.1 不会因为历史 demand 自动把所有曾用模型全部 warm 起。

### ✅ 边界保护

- [ ] 未创建第二个 Router/Downloader/Process system。
- [ ] 未改变 Provider scoring/failover/Auth/Billing 语义。
- [ ] 未在 request handler 内同步完成大型下载。
- [ ] 未绕过 readiness/health。

### ✅ 回归与验证

- [ ] tests 覆盖 Local READY、Provider-first、MODEL_PREPARING、resource blocked、download failure、restart stale state。
- [ ] concurrency test 证明 demand dedup。
- [ ] local pipeline failure 不破坏 Provider-only 请求。

### ✅ 工程流程

- [ ] 所有前置 Issue 有真实 DONE evidence。
- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确 demand observation point 与 state ownership。
- [ ] 所有实现只通过分支 + Pull Request 合并。


---

## 第四层：人类验收（Human Acceptance）

> 本节由 [Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/) 生成。机器测试、CI 或 AI Review 不能替代这里的人工验收。

### NODE-504 — Model Demand Reconciliation

**验收者：** 架构负责人 + 产品负责人。

**人工步骤：**
1. 对一个本地不存在的模型发送真实 `/v1` 请求。
2. 观察请求产生一个非阻塞 model demand。
3. 连续/并发重复请求，确认只存在一个 reconciliation pipeline。
4. 在 Provider 可用和不可用两种情况下观察当前请求与后台准备互不阻塞。
5. 重启 Node，确认 stale READY/Channel 不被盲目信任。

**人类通过标准：** Reconciler 只协调未来本地现实，不替代 ModelRouter；同 demand 去重；状态和失败原因可解释；重启 fail closed。

**人工判定失败：** Reconciler 自己选择当前 Channel、把下载/spawn 塞进 Router、Provider success 取消本地准备、或重启后信任不存在的进程。

**建议证据：** demand registry/state trace + 并发记录 + 重启前后状态。
