---
title: "Candidate Attempt Loop"
slug: /api-requests/chat-completion/provider-execution/candidate-attempt-loop/
type: runtime-flow
flow_id: user.api.chat.provider.loop
truth: STATIC_CONFIRMED
parent_flow: user.api.chat.provider
entry_points:
  - "proxy_logic for candidates"
drill_down:
  - "user.api.chat.provider.guard"
---

# Candidate Attempt Loop

← [Provider Execution](/api-requests/chat-completion/provider-execution/)

## What happens here?

每个候选对应一次 attempt。attempt>0 时 routing decision 被标记为 `Failover { attempt }`；当前候选的 `pricing_region` 也成为后续计费 region。循环中任何 `continue` 都意味着转到下一个 ranked candidate。

## ICFG

```mermaid
flowchart TD
    E["进入候选循环"] --> L["for (attempt, upstream) in candidates.iter().enumerate()"]
    F{"attempt > 0?"}
    FD["routing_decision = Failover{attempt}"]
    ID["last_upstream_id = upstream.id<br/>pricing_region = upstream.pricing_region"]
    GUARD["执行 Shaper + Circuit Breaker"]
    EXEC["执行 Provider request branch"]
    OUT{"branch result"}
    CONT["continue → 下一个候选"]
    RET["return ProxyResult → 结束循环"]
    END{"候选耗尽"}
    E --> L --> F
    F -->|Yes| FD --> ID
    F -->|No| ID
    ID --> GUARD --> EXEC --> OUT
    OUT -->|retryable / skipped| CONT --> L
    OUT -->|terminal response| RET
    L --> END
    click L "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2369" "Open loop" _blank
    click GUARD "/api-requests/chat-completion/provider-execution/shaper-circuit-breaker/" "Guard drill-down" _self
```

## Continue Drilling Down

→ [Shaper + Circuit Breaker](/api-requests/chat-completion/provider-execution/shaper-circuit-breaker/)

## Source Evidence

- [`crates/router/src/lib.rs:L2369-L2443`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2369-L2443)
- End-of-loop terminal outcomes: [`crates/router/src/lib.rs:L4106-L4166`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L4106-L4166)

**Confidence: HIGH — STATIC CONFIRMED**
