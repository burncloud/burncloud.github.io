---
title: "Trip All Circuit Breakers"
slug: /operator/circuit-breaker-trip-all/
type: runtime-flow
flow_id: user.operator.cb
truth: STATIC_CONFIRMED
parent_flow: user.operator
entry_points:
  - "POST /console/internal/circuit-breaker/trip-all"
---

# Trip All Circuit Breakers

← [Internal Operator Actions](/operator/)

## What happens here?

这个 internal endpoint 是一个紧急 operator action。`circuit_breaker_trip_all_handler()` 调用 `state.circuit_breaker.trip_all()`，把该组件已知的 upstream circuits 强制置为 Open，并取得被 trip 的 upstream id 列表；handler 随后返回 status、列表与 count 的 JSON。

## ICFG

```mermaid
flowchart TD
    E["Operator 触发全局 circuit trip<br/>POST /console/internal/circuit-breaker/trip-all"]
    H["进入 handler<br/>circuit_breaker_trip_all_handler()"]
    CB["强制 trip 已知 upstream circuits<br/>state.circuit_breaker.trip_all()"]
    IDS["获得 tripped upstream id list"]
    J["构造 status / tripped_upstreams / count JSON"]
    SER{"serde_json::to_string 成功?"}
    FALL["No → 使用固定 fallback JSON"]
    OUT["Return 200 application/json"]
    E --> H --> CB --> IDS --> J --> SER
    SER -->|Yes| OUT
    SER -->|No| FALL --> OUT
    click H "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1024" "Open handler" _blank
    click CB "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1025" "Open trip_all call" _blank
```

## State / Side Effects

- **STATE WRITE:** mutates in-memory circuit breaker state for known upstreams.
- Response exposes tripped IDs and count.

## Source Evidence

- Internal route registration: [`crates/router/src/lib.rs:L937-L952`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L937-L952)
- Handler body: [`crates/router/src/lib.rs:L1019-L1039`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1019-L1039)

**Confidence: HIGH — STATIC CONFIRMED.**
