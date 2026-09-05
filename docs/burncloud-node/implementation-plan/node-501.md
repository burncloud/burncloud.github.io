---
title: "NODE-501：READY Runtime 自动注册 Local Channel / Ability"
slug: /burncloud-node/implementation-plan/node-501/
---

# NODE-501：READY Runtime 自动注册 Local Channel / Ability

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Local Channel Integration**  
**功能依赖：NODE-403**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-501 要让本地 Runtime 一旦真实 READY，就自动变成现有 BurnCloud Router 能看到的 Local Channel / Ability。用户不需要“启用本地模型”。Local 可以通过现有 priority/availability 机制获得本地优先，但绝不能绕过 ModelRouter 写成特殊分支。

### 背景与动机（Why）

current InferenceService 已证明 llama-server READY 后创建 Local Channel + Ability 的路径可行。新的 demand-driven Node 要把这个行为变成稳定合同：Runtime READY 是注册前提，注册完成后 Router 只看到一个普通 Channel，而不是理解 llama.cpp、PID 或内部端口管理细节。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| READY 后自动注册 Channel / Ability | 不要求用户手工启用 |
| 使用 existing Channel/Ability schema | 不创建 LocalRouter |
| 配置明确 local-preference policy | 不绕过 ModelRouter |
| 保持单一 Local Channel identity | 不创建重复 Channel |
| 暴露 loopback endpoint 给 Router | 不修改 Provider 协议 |

### 风险与安全网（Risk）

> “本地优先”只能通过现有 Router 的合法排序/可用性机制表达；不能把 Router 变成 `if local_ready { return local }`。

### 审批者关注点（Reviewer Focus）

1. 是否同意 READY 自动注册，不需要用户操作？
2. 是否同意 Local 仍是普通 Channel，而不是旁路？
3. 是否同意 local-preference 通过既有 Router policy 表达？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
Runtime READY
      ↓
127.0.0.1:<internal-port>
      ↓
Local Channel
      ↓
Channel Ability(model=canonical model)
      ↓
Existing ModelRouter candidate set
```

### 2. Evidence

current InferenceService::register_upstream() 已创建 OpenAI-type Local Channel、loopback base_url 和 ChannelAbility，证明 existing abstraction 可复用。

### 3. Reuse Targets / Do Not Recreate

Reuse：ChannelProviderModel、ChannelAbilityModel、existing ModelRouter、current local-inference prototype。  
Do Not Recreate：NodeRouter、LocalRouter、second gateway、local-only model map。

### 4. Scope

#### Allowed

- READY runtime → idempotent Local Channel registration；
- stable local channel identity/tagging；
- canonical model → ability mapping；
- local-preference priority/weight policy using existing semantics；
- duplicate prevention；
- registration failure diagnostics；
- tests。

#### Avoid

- Router scoring/failover rewrite；
- Provider channel changes；
- process lifecycle；
- health removal/recovery（NODE-502）；
- Billing/Auth semantics。

### 5. Behavior Contract

```text
STARTING != registrable
READY => may register
same managed runtime identity => one Local Channel identity
registration is idempotent
local preference uses existing Router fields/policy
Router does not need to know runtime kind
```

默认 local-preference 的具体数值必须在 READY Audit 中根据 current Router priority semantics 确认，不能猜排序方向。

### 6. Failure / Forbidden Fallbacks

禁止：

```text
process spawned => register before READY
registration failure => bypass Router and call localhost directly
READY event repeated => create duplicate channels
local preference => hard-code Router bypass
Provider priority => mutate globally to force local
```

### 7. Impact / Invariants

```text
persistence: existing channel/ability state
external_calls: none
billing/auth: unchanged
routing: add normal candidate only
```

必须保持 `INV-ROUTER-001`。  
Candidate invariant：**Local models enter the data plane only through existing Channel / Ability.**

### 8. Dependencies

前置：NODE-403。  
后续：NODE-502、NODE-504、NODE-503。

### 9. Stop Conditions

STOP IF：必须创建 LocalRouter、必须绕过 ModelRouter、无法避免 duplicate local channels、或 local-preference 需要重写 Provider ranking/failover 才能实现。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] READY Runtime 自动注册 Local Channel + Ability。
- [ ] 用户无需手工 enable/start route。
- [ ] 相同 Runtime 重复事件不创建重复 Channel。
- [ ] Local candidate 可通过 current Router policy 获得明确本地优先。

### ✅ 边界保护

- [ ] 未创建 NodeRouter / LocalRouter。
- [ ] 未绕过 existing ModelRouter。
- [ ] 未改变 Provider failover/scoring 语义。
- [ ] 未在 STARTING 时注册。

### ✅ 回归与验证

- [ ] tests 覆盖 READY registration、repeat idempotency、registration failure、priority semantics。
- [ ] Provider-only 请求在没有 Local READY 时仍按原机制工作。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 锁定 current Channel/priority semantics。
- [ ] 只通过分支 + Pull Request 合并。


---

## 第四层：人类验收（Human Acceptance）

> 本节由 [Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/) 生成。机器测试、CI 或 AI Review 不能替代这里的人工验收。

### NODE-501 — READY Runtime 自动注册 Local Channel

**验收者：** Router 工程师 + 产品负责人。

**人工步骤：**
1. 让一个本地 Runtime 真正进入 READY。
2. 查看现有 Channel/Ability 体系是否自动出现对应 Local candidate。
3. 通过正常 `/v1` 请求验证 ModelRouter 能选中它。

**人类通过标准：** Local 以现有 Channel/Ability 身份进入 Router，而不是旁路；未 READY 时绝不注册 routable candidate。

**人工判定失败：** 直接从 Gateway 调 localhost runtime、重复 Local Channel、或 STARTING 状态就被 Router 选中。

**建议证据：** READY 前后 Channel/Ability 对比 + `/v1` route trace。
