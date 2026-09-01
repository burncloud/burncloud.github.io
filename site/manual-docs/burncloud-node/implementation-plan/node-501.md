---
title: "NODE-501：READY Runtime 注册 Local Channel / Ability"
slug: /burncloud-node/implementation-plan/node-501/
---

# NODE-501：READY Runtime 注册 Local Channel / Ability

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Local Channel Integration**  
**功能依赖：NODE-403**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-501 要把一个已经 `READY` 的本地 Runtime 注册成 BurnCloud 现有 Router 能理解的 `Channel + Channel Ability`。Router 不需要知道背后是 llama.cpp，只需要把它当成一个正常 OpenAI-compatible upstream。完成后，本地模型会进入现有 ModelRouter，而不是拥有自己的 LocalRouter。

### 背景与动机（Why）

current `InferenceService` 已经证明这条路可行：健康检查通过后，它创建一个 `Local: <model_id>` Channel，base URL 指向 `127.0.0.1:<port>`，并创建对应 Channel Ability。这个原型非常重要，因为它说明 BurnCloud 已有抽象足以容纳本地模型。

真正需要做的不是设计新的 NodeRouteEngine，而是把这个行为从混合的 InferenceService 中抽成**明确的 Local Channel adapter**，并锁住前置条件：只有 Runtime READY 才能注册。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| READY Runtime → existing Channel | 不创建 LocalRouter / NodeRouteEngine |
| 创建对应 Channel Ability | 不绕过 ModelRouter |
| endpoint 使用 loopback runtime 地址 | 不在 READY 前注册 |
| 复用 existing channel/database model | 不改变 Provider routing 算法 |
| 明确本地 channel metadata/tag | 不修改 Billing / Auth 语义 |

### 风险与安全网（Risk）

> 这是**接入已有 Router 的适配层**：如果现有 Channel 抽象无法承载本地 Runtime，必须停下来审架构，不能以此为理由发明第二套路由系统。

### 审批者关注点（Reviewer Focus）

1. 是否确认 Local Model 必须通过 existing Channel / Ability 进入 ModelRouter？
2. 是否确认只有 Runtime `READY` 才有注册资格？
3. 是否确认 Router 不需要知道 llama.cpp 等 Runtime 细节？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
Runtime READY
    + canonical model identity
    + loopback endpoint
          ↓
Local Channel
+ Channel Ability
          ↓
existing ModelRouter candidate set
```

### 2. Evidence

- current `InferenceService::register_upstream()` 已创建 `Channel`，`base_url = http://127.0.0.1:<port>`，`tag = local-inference`，并写入 `ChannelProviderModel`。
- current implementation 同时创建 `ChannelAbilityInput`，将 local model 加入 `default` group，证明 existing Channel / Ability abstraction 已可表达本地 upstream。
- `ModelRouter::get_candidates()` 当前从 `channel_abilities` + `channel_providers` 获取候选；本地模型不需要额外 Route Engine。

### 3. Entry / Starting Point

重新检查：

```text
crates/service/crates/inference/src/lib.rs :: register_upstream
crates/database channel provider/ability models
crates/router/src/model_router.rs :: get_candidates
NODE-403 READY state contract
```

### 4. Reuse Targets / Do Not Recreate

Reuse：Channel、ChannelProviderModel、ChannelAbilityModel、existing ModelRouter。  
Do Not Recreate：NodeRouteEngine、LocalRouter、separate local routing table。

### 5. Scope

#### Allowed

- Local Channel adapter；
- Channel / Ability metadata mapping；
- READY precondition；
- idempotent registration semantics；
- mapping of canonical model identity to ability；
- tests proving Router candidate visibility。

#### Avoid

- health-change unregister/disable policy（NODE-502）；
- Provider routing algorithm changes；
- Router scorer/failover changes；
- Runtime spawn / health implementation；
- Billing / Auth / quota changes。

### 6. Behavior Contract

Inputs：Runtime state = READY + internal endpoint + canonical model / capability metadata。  
Output：existing database 中一个可识别的 Local Channel + enabled Channel Ability。

必须满足：

```text
non-READY runtime => no registration
READY runtime => registration may proceed
same runtime identity => idempotent / no duplicate uncontrolled channels
Router consumes normal Channel abstraction
runtime implementation details are not part of ModelRouter contract
```

### 7. Failure / Forbidden Fallbacks

禁止：

```text
STARTING/UNHEALTHY => register enabled channel
registration failure => create LocalRouter
registration failure => bypass DB and inject candidate directly
local model => special-case ModelRouter selection logic
missing ability => mutate provider routing semantics
```

### 8. Impact / Invariants

```text
persistence: existing channel_providers / channel_abilities
external_calls: none
billing/auth: must remain unchanged
routing: adds a normal candidate, does not change algorithm
runtime/process: consumes READY facts only
```

必须保持：
- `INV-ROUTER-001`；
- `INV-AUTH-002`；
- `INV-BILLING-001`；
- `INV-BILLING-002`。

Candidate invariant：**Local model 通过 existing Channel / Ability 进入 data plane。**

### 9. Dependencies

前置：`NODE-403`。  
后续：`NODE-502`、`NODE-503`。

### 10. Stop Conditions

STOP IF：需要 NodeRouteEngine/LocalRouter、需要在 ModelRouter 添加 llama.cpp 特判、需要 READY 前注册、需要改变 Billing/Auth/Provider routing、或 existing Channel abstraction 被 current main 证据证明无法安全承载本地 endpoint。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] READY Runtime 可注册为 existing Local Channel。
- [ ] 对应 Channel Ability 正确表达 canonical model。
- [ ] existing ModelRouter 能把该 Channel 视为正常候选。
- [ ] registration 具有明确 idempotency / duplicate policy。

### ✅ 边界保护

- [ ] 非 READY Runtime 不会注册 enabled Channel。
- [ ] 未创建 LocalRouter / NodeRouteEngine。
- [ ] 未修改 ModelRouter scorer / failover / Provider semantics。
- [ ] 未修改 Billing / Auth / quota。

### ✅ 回归与验证

- [ ] tests 覆盖 READY 注册、非 READY 拒绝、重复注册、ability 创建失败。
- [ ] Router candidate lookup 能看到合法 Local Channel。
- [ ] existing Provider candidates 仍按原算法工作。
- [ ] `INV-ROUTER-001` 等相关 invariants 保持成立。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确 Local Channel identity / metadata / idempotency。
- [ ] 只通过分支 + Pull Request 合并。
