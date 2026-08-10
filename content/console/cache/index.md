---
title: "Cache Stats & Clear"
slug: /console/cache/
type: runtime-flow
flow_id: user.console.cache
truth: STATIC_CONFIRMED
parent_flow: user.console
entry_points:
  - "GET /console/api/cache/stats"
  - "POST /console/api/cache/clear"
---

# Cache Stats & Clear

← [Console 管理](/#/console/)

## ICFG

```mermaid
flowchart TD
    E["Authenticated cache request"] --> D{"Route"}
    S["GET stats → state.cache.stats().await"]
    C["POST clear → state.cache.clear_all().await"]
    R["Return success / error"]
    D -->|stats| S --> R
    D -->|clear| C --> R
    click S "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/cache.rs#L11" "Open stats" _blank
    click C "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/cache.rs#L20" "Open clear" _blank
```

## State / Side Effects

- stats: cache read/inspection.
- clear: cache mutation (`clear_all`).
- Cache service may be disabled when REDIS_URL is absent; that runtime availability is initialized in `create_app()`.

## Source Evidence

- [`crates/server/src/api/cache.rs:L11-L33`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/cache.rs#L11-L33)
- Cache initialization: [`crates/server/src/lib.rs:L37-L43`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/lib.rs#L37-L43)
