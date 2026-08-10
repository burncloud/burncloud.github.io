---
title: "Internal Operator Actions"
slug: /operator/
type: runtime-flow
flow_id: user.operator
truth: STATIC_CONFIRMED
parent_flow: user.burncloud
drill_down:
  - "user.operator.health"
  - "user.operator.price"
  - "user.operator.cb"
  - "user.operator.metrics"
---

# Internal Operator Actions

← [BurnCloud Runtime Atlas](/)

## User Flow

```mermaid
flowchart TD
    O["Operator / internal caller"] --> H["GET /health or /console/internal/health"]
    O --> P["POST /console/internal/prices/sync"]
    O --> C["POST /console/internal/circuit-breaker/trip-all"]
    O --> M["GET /console/internal/metrics"]
    click H "/#/operator/health/" "Health" _self
    click P "/#/operator/price-sync/" "Price sync" _self
    click C "/#/operator/circuit-breaker-trip-all/" "Circuit breaker" _self
    click M "/#/operator/metrics/" "Metrics" _self
```

Internal Router routes are registered before LiveView catch-all so they return JSON instead of SPA HTML.

## Source Evidence

- [`crates/router/src/lib.rs:L937-L965`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L937-L965)
- Top-level `/health`: [`crates/server/src/lib.rs:L59-L68`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/lib.rs#L59-L68)
