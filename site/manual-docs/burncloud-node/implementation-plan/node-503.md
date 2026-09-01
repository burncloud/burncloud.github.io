---
title: "NODE-503：localhost:3000 本地推理完整 E2E"
slug: /burncloud-node/implementation-plan/node-503/
---

# NODE-503：localhost:3000 本地推理完整 E2E

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Local Channel Integration**  
**功能依赖：NODE-003、NODE-502，以及 Node v0.1 本地执行链全部前置 Issue**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对当时的 `burncloud/burncloud/main`、确认所有前置 Issue 已 DONE，并通过 READY Gate。

### TL;DR

NODE-503 不再增加新的核心能力，而是证明 BurnCloud Node v0.1 的整条本地推理链真的能从“逻辑模型”一路走到 `localhost:3000/v1/...` 并返回响应。客户端不需要知道 GGUF 路径、内部端口、PID 或 llama-server 命令，未 READY 的模型也绝不能接到真实流量。这个 E2E 稳定通过，才说明 Node 的本地执行闭环真正完成。

### 背景与动机（Why）

前面的 Issue 都可以单独测试通过，但系统级失败往往发生在模块连接处：Resolver 选出的 Artifact Runtime 不认、Process 已 READY 但 Channel 没注册、Channel 注册了却被 Router 错误过滤，或者本地链能跑但破坏了 Provider/Auth/Billing 回归。

因此 NODE-503 是**闭环证明**，不是“大扫除 Issue”。如果 E2E 暴露某个前置合同错误，应回到对应 Issue / 新 Engineering Issue 修正，而不是借 E2E 权限顺手重构 Router、Billing 或 Auth。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 验证完整本地执行链 | 不新增第二套核心架构 |
| 从逻辑 Model ID 发起准备/运行 | 不要求客户端提供 GGUF 绝对路径 |
| 通过 existing Router 的 `localhost:3000/v1/...` 请求 | 不让客户端管理 PID / 内部端口 |
| 验证 non-READY 不接流量 | 不借 E2E 修改 Provider/Billing/Auth 语义 |
| 验证 Provider/Auth/Billing 回归 | 不把失败藏在测试专用 bypass 里 |

### 风险与安全网（Risk）

> 这是**系统验收 Issue，不是扩权 Issue**：E2E 如果发现某层合同不成立，Codex 必须定位并停止在对应责任边界，而不是扩大 NODE-503 来“把所有东西修通”。

### 审批者关注点（Reviewer Focus）

1. **是否同意这条链稳定通过才算 Node v0.1 本地执行闭环完成？**
2. **是否同意客户端只提供逻辑模型/API 请求，不承担 GGUF、PID、内部端口等内部实现细节？**
3. **是否同意本地能力上线不能以破坏现有 Provider routing、Auth、Billing 为代价？**

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

验证以下主链在真实/受控测试环境中可重复成立：

```text
logical model ID
      ↓
HardwareProfile
      ↓
Model Resolver
      ↓
ResolvedModel
      ↓
Model Preparation
      ↓
READY Artifact
      ↓
llama.cpp Runtime Adapter
      ↓
ProcessSpec
      ↓
Process Spawn
      ↓
Readiness / Health = READY
      ↓
Local Channel / Ability
      ↓
Existing ModelRouter
      ↓
Existing BurnCloud Server
      ↓
http://localhost:3000/v1/...
      ↓
normal model response
```

### 2. Evidence

以下证据基于 current main 的现有基础能力：

- `src/main.rs` / `burncloud_server::start_server()` 已提供统一 BurnCloud Server startup。
- `crates/server/src/lib.rs :: create_app` 已把 data-plane Router 作为统一 App 的 fallback，并应用全局 security boundary。
- current `InferenceService` 已证明 `llama-server → /v1/models readiness → Local Channel + Ability` 的原型路径存在。
- `ModelRouter` 已从 existing Channel / Ability 数据中选择候选并执行 availability / scheduler / failover。

NODE-503 的任务是验证前置 Issue 完成后这些能力形成一个闭环，而不是重新定义它们。

### 3. Entry / Starting Point

READY Audit 必须确认所有前置 Issue 的真实 DONE evidence，并重新检查：

```text
burncloud node runtime entry
NodeContext / Server composition
HardwareProfile / Resolver
Model Preparation
Runtime / Process Manager
Local Channel integration
existing /v1 data plane
```

### 4. Reuse Targets / Do Not Recreate

#### Reuse

- existing BurnCloud Server / Router；
- 已完成的 NODE-001~502 contracts；
- existing Auth / Billing / quota path；
- 最小可控 GGUF fixture 或明确批准的测试模型资源；
- existing E2E test infrastructure。

#### Do Not Recreate

```text
E2E-only Router bypass
E2E-only authentication bypass
E2E-only direct llama-server client as success proof
second local API gateway
test-only model state that cannot occur in production path
```

### 5. Scope

#### Allowed

- 建立完整 E2E fixture / harness；
- 使用最小、可重复的本地测试模型资源；
- 启动完整 Node local chain；
- 通过真实 existing `/v1/...` 入口发请求；
- 观测前置合同状态；
- 对明确属于 integration wiring 的小型修复提出对应 scoped change。

#### Avoid

- 借 E2E 重构 Provider Router；
- 修改 Billing / quota / Auth 语义；
- 重新设计 Resolver / Runtime / Process contracts；
- 引入 P2P / BurnCloud Network；
- 多机 scheduling；
- 用 test-only bypass 代替生产路径。

### 6. Behavior Contract

#### Client-visible inputs

客户端只需要使用 BurnCloud 正常 API 合同，例如：

```text
base URL: http://localhost:3000
model: logical/canonical model identity exposed by product contract
API credential: existing BurnCloud data-plane credential semantics
request body: existing compatible /v1 request
```

客户端不得要求提供：

```text
GGUF absolute path
llama-server binary path
internal runtime port
PID / Child handle
gpu_layers command argument
download GID
```

#### Required system behavior

```text
model not READY => no real inference traffic reaches local runtime
model READY => Local Channel may become routable
local runtime fails => stale channel becomes unavailable
request => existing ModelRouter chooses according to current routing semantics
response => returns through existing BurnCloud data plane
```

### 7. Failure / Forbidden Fallbacks

E2E 失败必须定位责任层，不得通过扩大 NODE-503 掩盖：

```text
Resolver contract failure -> stop / route to Resolver issue
Artifact failure          -> stop / route to Preparation issue
Runtime/Process failure   -> stop / route to Runtime issue
Channel health failure    -> stop / route to Local Channel issue
Auth/Billing regression   -> reject integration; do not weaken invariant
```

禁止：

```text
call llama-server directly and call E2E successful
skip existing Router
skip API credential/security boundary
mark model READY only for tests
hard-code internal port/PID/path in client test
change Provider routing to make local path win
silently auto-download huge model inside inference request
```

### 8. Impact / Invariants

```text
persistence: exercise existing model/download/channel state
external_calls: optional artifact preparation source + loopback runtime
billing_usage_quota: existing semantics must remain intact
auth_authorization: existing data-plane credential semantics must remain intact
routing_provider: existing ModelRouter semantics must remain intact
process_runtime_lifecycle: full local runtime lifecycle exercised
public_api: existing localhost:3000 /v1/... path
```

必须保持：

- `INV-RUNTIME-002`；
- `INV-ROUTER-001`；
- `INV-AUTH-002`；
- `INV-BILLING-001`；
- `INV-BILLING-002`。

### 9. Dependencies

最低前置：`NODE-003`、`NODE-502`。  
实际 READY Gate 必须确认 Node v0.1 local chain 所有必需 Issue 已 DONE：

```text
NODE-001~003
NODE-101~103
NODE-201~204
NODE-301~303
NODE-401~404
NODE-501~502
```

### 10. Stop Conditions

```text
STOP IF:
- any required predecessor is not actually DONE
- E2E requires bypassing existing Server/Router/Auth/Billing
- client must supply GGUF path/PID/internal port to succeed
- non-READY model must be made routable for the test
- integration requires changing an upstream contract outside this Issue
- a test-only code path would differ materially from production execution
- an INV-* must be weakened to make the E2E pass
```

触发时必须输出责任层、证据和需要的新/返工 Issue；不得在 NODE-503 内扩大架构权限。

---

## 第三层：验收层（Definition of Done）

### ✅ 完整链路

- [ ] 所有必需前置 Issue 已有真实 DONE evidence。
- [ ] 从 logical Model ID 能进入 Resolver，而不是由客户端指定 Artifact。
- [ ] Artifact 可按 Preparation contract 到达 READY。
- [ ] llama.cpp Runtime 由 ProcessSpec 启动，不需要客户端提供命令参数。
- [ ] Process 通过 readiness 后才进入 READY。
- [ ] READY Runtime 注册为 existing Local Channel / Ability。
- [ ] 请求通过 existing ModelRouter + existing Server 到达本地 Runtime。
- [ ] `http://localhost:3000/v1/...` 返回正常模型响应。

### ✅ 客户端体验

- [ ] 客户端不提供 GGUF absolute path。
- [ ] 客户端不提供 internal runtime port。
- [ ] 客户端不管理 PID / Child handle。
- [ ] 客户端不直接调用 llama-server。
- [ ] inference 请求不会因为隐藏下载大型模型而无限阻塞。

### ✅ 安全与失败行为

- [ ] 未 READY 模型不接真实流量。
- [ ] Runtime stop/crash/unhealthy 后 Local Channel 不再可路由。
- [ ] E2E 未使用 Router/Auth/Billing bypass。
- [ ] 任何前置合同失败都能定位责任层，而不是被 NODE-503 静默修补。

### ✅ 回归验证

- [ ] existing Provider routing regression 通过。
- [ ] existing data-plane authentication regression 通过。
- [ ] `INV-AUTH-002` 保持成立。
- [ ] `INV-BILLING-001/002` 保持成立。
- [ ] `INV-RUNTIME-002`、`INV-ROUTER-001` 保持成立。

### ✅ 可重复性

- [ ] E2E fixture/model resource 有明确版本或稳定 identity。
- [ ] 测试可从干净状态重复执行。
- [ ] 失败日志能指出 Hardware / Resolver / Preparation / Runtime / Channel / Router 中的责任层。
- [ ] 不依赖手工修改数据库、PID 或内部端口才能通过。

### ✅ 工程流程

- [ ] current-main Evidence Audit 已完成。
- [ ] Engineering Issue 已通过 READY Gate。
- [ ] Task Contract 明确完整 execution path 和 protected invariants。
- [ ] 所有实现只通过分支 + Pull Request 合并。

> **只有这一页对应的 E2E Checklist 全部通过，BurnCloud Node v0.1 的本地执行闭环才可以宣布完成。**
