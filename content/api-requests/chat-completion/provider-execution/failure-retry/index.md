---
title: "Failure & Retry"
slug: /api-requests/chat-completion/provider-execution/failure-retry/
type: runtime-flow
flow_id: user.api.chat.provider.failure
truth: STATIC_CONFIRMED
parent_flow: user.api.chat.provider
entry_points:
  - "HTTP/stream failure inside candidate loop"
---

# Failure & Retry

← [Provider Execution](/api-requests/chat-completion/provider-execution/)

## What happens here?

Provider 失败不是统一“返回错误”。代码会先分类 failure 并更新 Circuit Breaker / ChannelStateTracker；部分 health failures 还会 evict affinity。5xx、network error、429，以及 passthrough 中的 401/402 都有明确的继续下一个 candidate 分支；其他 4xx 通常直接形成终止 `ProxyResult`。候选耗尽后根据“是否全部被 Shaper 拒绝”返回 503 或 502。

## ICFG

```mermaid
flowchart TD
    E["当前 Provider attempt 失败"]
    KIND{"失败来源"}
    NET["Network error<br/>Timeout / ConnectionError"]
    HTTP["HTTP non-success"]
    SSE["首块 SSE error / empty response"]
    CLASS["classify_upstream_error()"]
    REC["record_upstream_failure()<br/>CB + channel state + conditional affinity eviction"]
    RTRY{"代码分支允许 retry?"}
    NEXT["continue → next candidate"]
    TERM["return 当前 error ProxyResult"]
    EXH{"candidate loop exhausted"}
    ALLSH{"所有 candidates 都被 Shaper reject?"}
    E503["503 rate_budget_exhausted<br/>X-Rejected-By: shaper"]
    E502["502 all_upstreams_failed"]
    E --> KIND
    KIND -->|Network| NET --> REC
    KIND -->|HTTP| HTTP --> CLASS --> REC
    KIND -->|Streaming peek| SSE --> REC
    REC --> RTRY
    RTRY -->|Yes| NEXT
    RTRY -->|No| TERM
    NEXT --> EXH
    EXH --> ALLSH
    ALLSH -->|Yes| E503
    ALLSH -->|No| E502
    click CLASS "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L417" "Open error classifier" _blank
    click REC "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L311" "Open failure state update" _blank
    click E503 "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L4106" "Open terminal outcomes" _blank
```

## Decisions

- `record_upstream_failure()` evicts affinity only for ServerError / Timeout / ConnectionError / EmptyResponse.
- HTTP 429 explicitly retries next candidate in converted path.
- Passthrough explicitly retries 429 / 401 / 402.
- API-version deprecation can spawn async detector/update, but that does not make the current 4xx retryable by itself.

## State / Side Effects

- Circuit breaker mutation.
- Channel state error mutation.
- Conditional affinity cache eviction.
- Failover history appended when detailed logging is active.

## Source Evidence

- Failure state semantics: [`crates/router/src/lib.rs:L304-L366`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L304-L366)
- Error classification: [`crates/router/src/lib.rs:L414-L439`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L414-L439)
- Passthrough retry/error branches: [`crates/router/src/lib.rs:L2561-L3064`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2561-L3064)
- Converted retry/error branches and terminal outcomes: [`crates/router/src/lib.rs:L3158-L4166`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L3158-L4166)

**Confidence: HIGH — STATIC CONFIRMED**
