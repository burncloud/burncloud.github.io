---
title: "NODE-502：健康状态联动、摘除与注销"
slug: /burncloud-node/implementation-plan/node-502/
---

# NODE-502：健康状态联动、摘除与注销

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Local Channel Integration**  
**功能依赖：NODE-404、NODE-501**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-502 要让 Local Channel 的可路由状态始终跟随真实 Runtime 健康状态。模型进程 stop、crash 或变成 UNHEALTHY 后，它必须及时退出 Router 候选；重新 READY 后才能按明确策略恢复。完成后，Router 不会继续把已经失效的本地进程当成可用上游。

### 背景与动机（Why）

NODE-501 负责首次把 READY Runtime 注册成 Channel，但“注册成功”并不是永久事实。current InferenceService 在主动 stop 时会删除 ability/channel，可是异常 crash、health 变坏和后续恢复需要更系统的联动，否则数据面可能把请求送到已经死掉的 loopback endpoint。

NODE-502 的职责是**同步可用性，不重新定义路由算法**。Process Manager 提供真实健康状态，Local Channel adapter 将它反映到 existing Channel / availability 机制；Provider failover、Billing 和 Auth 仍保持原语义。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Runtime health → Channel availability | 不修改 Provider failover 算法 |
| stop/crash/unhealthy 后摘除/禁用 | 不绕过 existing ModelRouter |
| 恢复 READY 后按明确策略恢复 | 不修改 Billing / Auth |
| 防止 stale local Channel 接流量 | 不发明第二套 health truth |
| 明确 unregister / disable / re-enable 语义 | 不负责进程 restart 本身 |

### 风险与安全网（Risk）

> 这是**失效保护层**：宁可暂时少一个本地候选，也不能让 Router 把真实流量送到已失效进程；任何不确定健康状态都不能自动视为可用。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Runtime health 是 Local Channel availability 的权威来源？
2. 是否同意失效时优先 fail closed，不能为了保持路由数量而继续 enabled？
3. 是否确认本 Issue 只同步 availability，不改变 Provider routing / Billing / Auth？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
Process/Runtime authoritative state
        ↓
READY        → Local Channel routable
UNHEALTHY    → Local Channel unavailable
FAILED/crash → Local Channel unavailable/unregistered
STOPPED      → Local Channel unavailable/unregistered
READY again  → explicit recovery policy
```

### 2. Evidence

- current `InferenceService::stop_instance()` 主动停止时会删除对应 abilities，再删除 Local Channel。
- current `register_upstream()` 创建的 Local Channel 是 existing `channel_providers / channel_abilities` 数据，因此 availability 必须继续通过已有 Router/Channel 体系表达。
- `ModelRouter::route_with_scheduler()` 当前先通过 `ChannelStateTracker::is_available()` 过滤候选，证明 existing Router 已有可用性层；NODE-502 不应增加平行 local availability pipeline。

### 3. Entry / Starting Point

重新检查：

```text
NODE-404 process state/crash lifecycle
NODE-501 Local Channel identity
current ChannelStateTracker availability semantics
ChannelProviderModel / ChannelAbilityModel
existing InferenceService unregister_upstream prototype
```

### 4. Reuse Targets / Do Not Recreate

Reuse：Runtime authoritative state、existing Channel/Ability storage、ChannelStateTracker/availability mechanisms。  
Do Not Recreate：Local availability router、parallel health tracker、Provider failover logic。

### 5. Scope

#### Allowed

- Runtime state → Channel availability mapping；
- disable/unregister/remove policy；
- recovery/re-register/re-enable policy；
- stale registration cleanup；
- event/idempotency semantics；
- tests proving no stale routing。

#### Avoid

- process restart（NODE-404）；
- Router scoring / affinity / failover changes；
- Billing / quota；
- Auth / security boundary；
- provider channel health semantics rewrite。

### 6. Behavior Contract

必须满足：

```text
READY        => may be routable
STARTING     => not routable
UNHEALTHY    => not routable
FAILED       => not routable
STOPPED      => not routable
unknown/stale state => fail closed
```

Recovery policy 必须明确是 re-enable 还是 recreate，但不得产生重复 Local Channels。

Health flow 单向：

```text
Process/Runtime truth
      ↓
Local Channel availability
      ↓
ModelRouter candidate filtering
```

Router candidate status 不得反向伪造 Runtime health。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
crash => leave enabled channel
unknown health => keep routing
unregister failure => pretend channel is removed
recovery => create duplicate channels indefinitely
local health failure => alter Provider priority/failover
local failure => bypass auth/billing for fallback
```

### 8. Impact / Invariants

```text
persistence: existing channel/ability availability state
external_calls: none beyond local state integration
billing_usage_quota: unchanged
auth_authorization: unchanged
routing_provider: availability only, algorithm unchanged
process lifecycle: consume state, do not own restart
```

必须保持：
- `INV-ROUTER-001`；
- `INV-AUTH-002`；
- `INV-BILLING-001`；
- `INV-BILLING-002`。

Candidate invariant：**只有真实 READY 的本地 Runtime 才能保持 routable Local Channel。**

### 9. Dependencies

前置：`NODE-404`、`NODE-501`。  
后续：`NODE-503`。

### 10. Stop Conditions

STOP IF：必须修改 Provider failover/scorer、必须绕过 ChannelStateTracker/现有 availability、无法避免 stale enabled Channel、需要改变 Billing/Auth、或健康 truth 无法从 Process Manager 明确获得。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] READY Runtime 的 Local Channel 可路由。
- [ ] STARTING / UNHEALTHY / FAILED / STOPPED Runtime 不可路由。
- [ ] stop/crash/health failure 能及时驱动摘除/禁用。
- [ ] recovery 不产生无限重复 Channel。
- [ ] stale/unknown state fail closed。

### ✅ 边界保护

- [ ] 未修改 Provider ranking / failover / affinity 语义。
- [ ] 未实现 process restart。
- [ ] 未修改 Billing / Auth / quota。
- [ ] 未建立第二套 local health/router subsystem。

### ✅ 回归与验证

- [ ] tests 覆盖 READY→UNHEALTHY、READY→crash、stop、recovery、unregister failure。
- [ ] Router candidate lookup 不再返回失效 Local Channel。
- [ ] existing Provider routing 在 Local Channel 失效时仍按原机制工作。
- [ ] 相关 INV-* 保持成立。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确 availability integration 与 recovery policy。
- [ ] 只通过分支 + Pull Request 合并。
