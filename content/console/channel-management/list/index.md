---
title: "List Channels"
slug: /console/channel-management/list/
type: runtime-flow
flow_id: user.console.channel.list
truth: STATIC_CONFIRMED
parent_flow: user.console.channel
entry_points:
  - "GET /console/api/channel"
---

# List Channels

← [Channel Management](/console/channel-management/)

## ICFG

```mermaid
flowchart TD
    E["GET /console/api/channel<br/>list_channels()"] --> A["check_admin()"]
    OK{"admin?"}
    DENY["Return access error"]
    P["clamp limit 1..100; offset >=0"]
    S["ChannelService::list(db,limit,offset)"]
    DB["ChannelProviderModel::list()<br/>SELECT channel_providers ORDER BY id DESC"]
    R{"DB result"}
    OUT["Return channels + pagination"]
    ERR["Return error"]
    E --> A --> OK
    OK -->|No| DENY
    OK -->|Yes| P --> S --> DB --> R
    R -->|Ok| OUT
    R -->|Err| ERR
    click E "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/channel.rs#L139" "Open handler" _blank
    click DB "https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L194" "Open DB query" _blank
```

## State / Side Effects

- DB READ only.

## Source Evidence

- [`crates/server/src/api/channel.rs:L139-L159`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/channel.rs#L139-L159)
- [`crates/service/crates/channel/src/lib.rs:L17-L20`](https://github.com/burncloud/burncloud/blob/main/crates/service/crates/channel/src/lib.rs#L17-L20)
- [`crates/database/crates/channel/src/channel_provider.rs:L194-L234`](https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L194-L234)
