---
title: "View Logs & User Usage"
slug: /console/logs-usage/
type: runtime-flow
flow_id: user.console.logs
truth: STATIC_CONFIRMED
parent_flow: user.console
entry_points:
  - "GET /console/api/logs"
  - "GET /console/api/usage/{user_id}"
---

# View Logs & User Usage

← [Console 管理](/#/console/)

## ICFG

```mermaid
flowchart TD
    E["Authenticated Console request"] --> D{"Route"}
    L["GET /console/api/logs<br/>list_logs()"]
    P["page/page_size → offset"]
    LS["RouterLogService::get(db,page_size,offset)"]
    LR["Return LogPage"]
    U["GET /console/api/usage/{user_id}<br/>get_user_usage()"]
    US["RouterLogService::get_usage_by_user()"]
    UR["Return prompt/completion/total tokens"]
    D -->|logs| L --> P --> LS --> LR
    D -->|usage| U --> US --> UR
    click L "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/log.rs#L59" "Open list_logs" _blank
    click U "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/log.rs#L81" "Open get_user_usage" _blank
```

## Source Evidence

- [`crates/server/src/api/log.rs:L44-L98`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/log.rs#L44-L98)
