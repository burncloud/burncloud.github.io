---
title: "Shaper & Circuit Breaker"
slug: /api-requests/chat-completion/provider-execution/shaper-circuit-breaker/
type: runtime-flow
flow_id: user.api.chat.provider.guard
truth: STATIC_CONFIRMED
parent_flow: user.api.chat.provider
entry_points:
  - "candidate iteration preflight"
drill_down:
  - "user.api.chat.provider.dispatch"
---

# Shaper & Circuit Breaker

← [Provider Execution](/#/api-requests/chat-completion/provider-execution/)

## What happens here?

每个候选在真正发 HTTP 之前先经过本地 Rate Budget Shaper，然后才检查 Circuit Breaker。未配置 Shaper 的 Channel fail-open；配置了但 `try_consume` 返回 `Rejected` 时记录 failover 并直接跳下一个候选。Circuit Breaker open 同样直接 skip，且预留的 BudgetGuard 通过 Drop 退款。

## ICFG

```mermaid
flowchart TD
    E["当前 upstream candidate"]
    CFG{"rate_budget 已配置该 channel?"}
    FO["fail_open_count++<br/>label=shaper_unconfigured"]
    TRY["try_consume(channel,color,est_tpm)"]
    REJ{"ConsumeOutcome::Rejected?"}
    RF["rejected_count++ + record_failover_attempt()"]
    NEXT["continue → next candidate"]
    GUARD["BudgetGuard::new() 保留预算"]
    CB["circuit_breaker.allow_request(upstream.id)"]
    CBO{"allowed?"}
    CBF["记录 last_error + failover history"]
    HTTP["继续构造 Provider 请求"]
    E --> CFG
    CFG -->|No| FO --> CB
    CFG -->|Yes| TRY --> REJ
    REJ -->|Yes| RF --> NEXT
    REJ -->|No| GUARD --> CB
    CB --> CBO
    CBO -->|No| CBF --> NEXT
    CBO -->|Yes| HTTP
    click TRY "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2396" "Open shaper branch" _blank
    click CB "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2428" "Open circuit breaker branch" _blank
    click HTTP "/#/api-requests/chat-completion/provider-execution/protocol-dispatch/" "Continue to dispatch" _self
```

## State / Side Effects

- `fail_open_count` increments for unconfigured Shaper channels.
- `shaper_ctx.rejected_count` tracks local rejections for final all-rejected `503` decision.
- Circuit Breaker state is read here; failure/success mutation happens later.

## Continue Drilling Down

→ [Protocol Dispatch](/#/api-requests/chat-completion/provider-execution/protocol-dispatch/)

## Source Evidence

- [`crates/router/src/lib.rs:L2381-L2443`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2381-L2443)

**Confidence: HIGH — STATIC CONFIRMED**
