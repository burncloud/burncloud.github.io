---
title: "NODE-503：Demand-driven 本地推理完整 E2E"
slug: /burncloud-node/implementation-plan/node-503/
---

# NODE-503：Demand-driven 本地推理完整 E2E

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Local Channel Integration**  
**功能依赖：NODE-004、NODE-304、NODE-502、NODE-504，以及 Node v0.1 全部前置 Issue**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须确认所有前置 Issue 已 DONE，并基于当时 `burncloud/burncloud/main` 重新通过 READY Gate。

### TL;DR

NODE-503 要证明用户只写正常 `/v1` 请求和 `model=qwen-4b` 就能完成整个 Node 产品闭环：协议入口保持兼容；本地 READY 时自动用本地；本地没有但 Provider 有时先用 Provider、后台自动下载并加载；两边都没有但本机能跑时明确返回 `MODEL_PREPARING`；硬件或磁盘不满足时返回真实原因；本地 Artifact 的 inventory/status 也保持真实。这个 E2E 与人工验收全部通过，才算 BurnCloud Node v0.1 产品闭环完成。

### 背景与动机（Why）

前面的 Issue 可以分别证明 Gateway compatibility、Resolver、Download、Artifact lifecycle、Runtime 和 Router 都正确，但产品价值在于它们能否在真实 `/v1` 请求下自动协作。尤其要防止一种“技术上都完成、用户仍需手工下载启动”或“本地链完成但协议入口已经回归”的假完成。

NODE-503 是系统验收，不是大扫除 Issue。任何某层失败都必须回到对应责任边界修复。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 用户只通过 existing `/v1` 声明 model | 不调用管理 API 手工下载/启动作为前置 |
| 验证 NODE-004 已批准协议入口 | 不在 E2E 中重写协议栈 |
| 验证 Local READY 直接服务 | 不直接请求 llama-server 冒充成功 |
| 验证 Provider-first + background local prepare | 不让请求等待完整模型下载 |
| 验证 MODEL_PREPARING / resource errors | 不返回模糊“模型不存在”代替真实状态 |
| 验证并发 demand 去重和自动切 Local | 不借 E2E 重写 Router/Billing/Auth |
| 验证 Artifact inventory/state 不产生 ghost READY | 不要求人工 delete 才能跑通推理 |

### 风险与安全网（Risk）

> 这是最终产品行为验收：只要测试仍需要人工 GGUF、PID、端口、start/stop 命令，或者协议兼容 Gate/Artifact lifecycle 仍未通过，就不能宣布 Node v0.1 完成。

### 审批者关注点（Reviewer Focus）

1. 是否同意“用户只声明正常请求 + model”是 v0.1 的硬完成标准？
2. 是否同意 Provider-first 与后台 Local Preparation 可以并行？
3. 是否同意 NODE-004 / NODE-304 属于完整产品前置，不允许把“协议/Artifact 管理以后再补”当作 v0.1 DONE？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

验证真实产品闭环：

```text
approved protocol request
        ↓
existing Server / Protocol boundary
        ↓
/v1 request(model=qwen-4b)
        ↓
Existing ModelRouter serves current reality
        +
NODE-504 observes demand
        ↓
Resolve / Prepare / Runtime / READY
        ↓
Local Channel appears
        ↓
future requests naturally prefer Local
```

### 2. Mandatory E2E Scenarios

#### Scenario 0 — Protocol compatibility precondition

至少选择 NODE-004 已批准的代表性协议入口验证 Node 模式仍满足：

```text
URL / Path → Protocol Detection
model_id   → Existing ModelRouter
same protocol      → Raw Proxy
protocol mismatch  → Translator
```

NODE-503 不重新实现协议逻辑；若 NODE-004 未 DONE，本 Issue 保持 BLOCKED。

#### Scenario A — Local already READY

```text
Local READY + Provider optional
        ↓
/v1 request
        ↓
Existing Router selects Local according to current policy
        ↓
normal response
```

#### Scenario B — Local absent, Provider available

```text
Request #1
  ↓
Provider response succeeds immediately
  +
exactly one background Model Demand
  ↓
Download → Verify → Runtime → READY
  ↓
Local Channel registered
  ↓
subsequent request prefers Local
```

当前 Provider 响应不能等待本地下载。

#### Scenario C — Local absent, Provider unavailable, local feasible

```text
/v1 request
   ↓
no serving candidate
   + demand accepted
   ↓
503 MODEL_PREPARING
   ↓
background pipeline continues
   ↓
READY
   ↓
retry succeeds through Local
```

#### Scenario D — No Provider and local preparation impossible

至少验证：

```text
INSUFFICIENT_VRAM
INSUFFICIENT_DISK
UNSUPPORTED_RUNTIME or NO_COMPATIBLE_VARIANT
```

返回 machine-readable diagnosis，而不是 generic model-not-found。

#### Scenario E — Concurrent demand dedup

```text
N concurrent requests for same model
        ↓
<= 1 active local preparation pipeline
<= 1 managed runtime identity
<= 1 Local Channel identity
```

#### Scenario F — Artifact truth after lifecycle changes

在安全测试环境中验证：

```text
READY Artifact → inventory shows READY
managed cleanup/delete → inventory no longer shows ghost READY
in-use Artifact → NODE-304 safety contract rejects unsafe delete
```

NODE-503 不要求用户在正常推理流程执行 delete；这里只验证完整产品状态不会因为 Artifact lifecycle 产生假的可用性。

### 3. Reuse Targets / Do Not Recreate

Reuse：existing Server/Router/Auth/Billing、NODE-001~504 production path、curated model manifest、minimal approved test model/runtime artifacts。  
Do Not Recreate：E2E-only Router bypass、direct llama client、test-only protocol bypass、test-only local state impossible in production。

### 4. Scope

#### Allowed

- deterministic E2E harness/fixture；
- controlled provider fixture when required；
- controlled local model/runtime artifacts；
- real approved protocol + `/v1` request path；
- observation of demand/preparation/runtime/channel/artifact states；
- precise assertions on response origin/state transitions。

#### Avoid

- manual pre-download/start steps as success criteria；
- Protocol stack rewrite；
- Provider Router rewrite；
- Auth/Billing weakening；
- test-only bypass；
- direct llama-server success proof；
- architecture changes hidden inside E2E fixes。

### 5. Behavior Contract

客户端只提供：

```text
base URL
existing BurnCloud credential
model
normal protocol request body
```

客户端不得提供：

```text
GGUF path
artifact URL
llama-server path
internal port
PID
gpu_layers
download task ID
start/stop command
```

### 6. Failure / Forbidden Fallbacks

禁止：

```text
protocol regression => ignore because local inference works
provider available => block until local download finishes
no provider + preparing => generic MODEL_NOT_FOUND
hardware insufficient => pretend download is still preparing
local failure => bypass Router/Auth/Billing
direct llama-server call => call Node E2E passed
concurrent requests => duplicate downloads/runtimes/channels
artifact deleted => leave ghost READY/channel
```

### 7. Impact / Invariants

必须保持：

- `INV-RUNTIME-002`；
- `INV-ROUTER-001`；
- `INV-AUTH-002`；
- `INV-BILLING-001`；
- `INV-BILLING-002`；
- Raw Proxy First / Translator only when needed；
- `Process Spawned != Model READY`；
- same model demand is deduplicated；
- Artifact inventory/state 不形成第二份真相。

### 8. Dependencies

实际 READY Gate 必须确认：

```text
NODE-001~004
NODE-101~103
NODE-201~204
NODE-301~304
NODE-400~404
NODE-501~502
NODE-504
```

BurnCloud Network、P2P、AMD/Apple GPU detection、复杂 cache scheduler 不属于 NODE-503 / Node v0.1 前置。

### 9. Stop Conditions

STOP IF：任何前置 Issue 未真实 DONE、E2E 需要手工 model lifecycle、需要绕过 existing Server/Router/Auth/Billing、NODE-004 协议 Gate 未完成、Artifact truth 无法保持一致、需要 test-only production-incompatible path、或必须弱化 invariant 才能通过。

---

## 第三层：验收层（Definition of Done）

### ✅ Scenario 0：协议入口

- [ ] NODE-004 已 DONE。
- [ ] 至少一个 same-protocol Raw Proxy 代表场景在 Node 模式通过。
- [ ] 至少一个需要 Translator 的代表场景按批准合同通过（若 v0.1 matrix 包含该场景）。
- [ ] Node 本地能力接入没有破坏 approved protocol semantics。

### ✅ Scenario A：Local READY

- [ ] `/v1` 只声明 model 即可成功。
- [ ] Local READY 通过 existing Router 被选中。
- [ ] 客户端不知道内部 port/PID/path。

### ✅ Scenario B：Provider-first → 自动 Local

- [ ] Local absent 时 Provider 请求立即成功。
- [ ] 同时自动产生后台 local demand。
- [ ] Provider 响应不等待模型下载。
- [ ] 下载/校验/启动/READY 全自动完成。
- [ ] Local Channel 自动出现。
- [ ] 后续请求按 existing Router policy 优先 Local。

### ✅ Scenario C：无 Provider但可本地准备

- [ ] 初始请求返回 `503 MODEL_PREPARING` 或等价明确合同。
- [ ] background prepare 不因请求结束而取消。
- [ ] READY 后重试成功。

### ✅ Scenario D：不可准备

- [ ] VRAM 不足返回结构化诊断。
- [ ] Disk 不足返回结构化诊断。
- [ ] Runtime/Variant 不支持返回结构化诊断。
- [ ] 不使用 generic model-not-found 掩盖已知原因。

### ✅ Scenario E：并发与生命周期

- [ ] N 个相同请求只产生一个 active prepare pipeline。
- [ ] 不产生重复 Runtime / Local Channel。
- [ ] Node shutdown 自动清理 managed process。
- [ ] crash/unhealthy 后 Local Channel 自动失去 routable 状态。

### ✅ Scenario F：Artifact lifecycle truth

- [ ] NODE-304 已 DONE。
- [ ] READY inventory 与真实文件/状态一致。
- [ ] 安全删除/清理后不残留 ghost READY。
- [ ] in-use / ownership 不明 Artifact 不被强删。

### ✅ 回归验证

- [ ] existing Provider routing 通过。
- [ ] existing Auth / Billing semantics 保持。
- [ ] 未 READY 模型永不接真实流量。
- [ ] inference 请求不同步阻塞等待大型模型下载。

### ✅ 工程流程

- [ ] current-main Evidence Audit 已完成。
- [ ] Engineering Issue 已通过 READY Gate。
- [ ] Task Contract 明确完整 production execution path。
- [ ] 所有实现只通过分支 + Pull Request 合并。

> **NODE-503 的机器验收全部通过后，还必须执行第四层 Human Acceptance；只有机器 + 人类都 PASS，才能宣布 BurnCloud Node v0.1 完成。**
