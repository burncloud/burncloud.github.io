---
title: "Health Checks"
slug: /operator/health/
type: runtime-flow
flow_id: user.operator.health
truth: STATIC_CONFIRMED
parent_flow: user.operator
entry_points:
  - "GET /health"
  - "GET /console/internal/health"
---

# Health Checks

← [Internal Operator Actions](/#/operator/)

## What happens here?

BurnCloud 有两个不同深度的 health user flow。顶层 `/health` 是未认证 liveness probe，只返回文本 `ok`。`/console/internal/health` 进入 `health_status_handler()`，读取 circuit breaker 状态、channel state、scheduler policies、rate-budget snapshots 和若干 billing/fail-open counters，并组装 JSON report。

## ICFG

```mermaid
flowchart TD
    E{"调用哪个 health endpoint?"}
    TOP["GET /health<br/>top-level liveness route"]
    OK["async closure → Return 'ok'"]
    INT["GET /console/internal/health<br/>health_status_handler()"]
    CB["读取 circuit breaker status map"]
    CH["读取 all channel states"]
    SP["read().await scheduler_policies"]
    BUD["按 known channel 读取 rate_budget.snapshot()"]
    CNT["读取 fail-open / billing counters"]
    JSON["组装 comprehensive health_report JSON"]
    SER["serialize JSON"]
    OUT["Return 200 application/json"]
    E -->|/health| TOP --> OK
    E -->|internal| INT --> CB --> CH --> SP --> BUD --> CNT --> JSON --> SER --> OUT
    click TOP "https://github.com/burncloud/burncloud/blob/main/crates/server/src/lib.rs#L65" "Open liveness route" _blank
    click INT "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1263" "Open rich health handler" _blank
```

## State / Side Effects

- Top-level liveness has no visible state mutation.
- Internal health reads in-memory router state/policies/budgets/counters; no DB write is visible in this handler.

## Source Evidence

- Top-level liveness route: [`crates/server/src/lib.rs:L59-L68`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/lib.rs#L59-L68)
- Internal route binding: [`crates/router/src/lib.rs:L937-L952`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L937-L952)
- Rich handler: [`crates/router/src/lib.rs:L1263-L1357`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1263-L1357)

**Confidence: HIGH — STATIC CONFIRMED.**
