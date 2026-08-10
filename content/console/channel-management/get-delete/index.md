---
title: "Get / Delete Channel"
slug: /console/channel-management/get-delete/
type: runtime-flow
flow_id: user.console.channel.getdelete
truth: STATIC_CONFIRMED
parent_flow: user.console.channel
entry_points:
  - "GET /console/api/channel/{id}"
  - "DELETE /console/api/channel/{id}"
---

# Get / Delete Channel

← [Channel Management](/#/console/channel-management/)

## ICFG

```mermaid
flowchart TD
    E["GET 或 DELETE /console/api/channel/{id}"] --> A["check_admin()"]
    OK{"admin?"}
    DENY["Return access error"]
    M{"HTTP method"}
    GET["get_channel() → ChannelService::get_by_id()"]
    Q["SELECT channel_providers WHERE id"]
    F{"found?"}
    OUT["Return Channel"]
    NF["Return channel not found"]
    DEL["delete_channel() → ChannelService::delete()"]
    DA["DELETE channel_abilities WHERE channel_id"]
    DC["DELETE channel_providers WHERE id"]
    DONE["Return success"]
    E --> A --> OK
    OK -->|No| DENY
    OK -->|Yes| M
    M -->|GET| GET --> Q --> F
    F -->|Yes| OUT
    F -->|No| NF
    M -->|DELETE| DEL --> DA --> DC --> DONE
    click Q "https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L155" "Open get query" _blank
    click DA "https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L136" "Open delete" _blank
```

## State / Side Effects

- GET: DB read only.
- DELETE: removes abilities first, then provider row.

## Source Evidence

- Handlers: [`crates/server/src/api/channel.rs:L198-L227`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/channel.rs#L198-L227)
- DB get/delete: [`crates/database/crates/channel/src/channel_provider.rs:L136-L192`](https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L136-L192)
