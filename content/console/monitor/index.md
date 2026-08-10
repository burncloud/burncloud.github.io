---
title: "View System Monitor"
slug: /console/monitor/
type: runtime-flow
flow_id: user.console.monitor
truth: STATIC_CONFIRMED
parent_flow: user.console
entry_points:
  - "GET /console/api/monitor"
---

# View System Monitor

← [Console 管理](/console/)

## ICFG

```mermaid
flowchart TD
    E["GET /console/api/monitor"] --> JWT["auth_middleware"] --> H["get_system_metrics()"] --> S["state.monitor.get_metrics().await"] --> R{"result"}
    R -->|Ok| OK["Return metrics"]
    R -->|Err| ERR["Return error"]
    click H "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/monitor.rs#L10" "Open handler" _blank
```

## Source Evidence

- [`crates/server/src/api/monitor.rs:L5-L15`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/monitor.rs#L5-L15)
