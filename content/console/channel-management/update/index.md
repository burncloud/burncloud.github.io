---
title: "Update Channel"
slug: /console/channel-management/update/
type: runtime-flow
flow_id: user.console.channel.update
truth: STATIC_CONFIRMED
parent_flow: user.console.channel
entry_points:
  - "PUT /console/api/channel"
---

# Update Channel

← [Channel Management](/console/channel-management/)

## ICFG

```mermaid
flowchart TD
    E["PUT /console/api/channel<br/>update_channel()"] --> A["check_admin()"]
    OK{"admin?"}
    DENY["Return access error"]
    DTO["payload.into_channel()"]
    ID{"channel.id == 0?"}
    BAD["Return 'id is required'"]
    S["ChannelService::update()"]
    DB["UPDATE channel_providers WHERE id"]
    SYNC["sync_abilities(): delete existing abilities"]
    EN{"channel enabled?"}
    RET["Return updated channel"]
    INS["rebuild abilities from models × groups"]
    E --> A --> OK
    OK -->|No| DENY
    OK -->|Yes| DTO --> ID
    ID -->|Yes| BAD
    ID -->|No| S --> DB --> SYNC --> EN
    EN -->|No| RET
    EN -->|Yes| INS --> RET
    click E "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/channel.rs#L178" "Open handler" _blank
    click DB "https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L89" "Open DB update" _blank
```

## State / Side Effects

- DB WRITE: update provider row.
- DB WRITE: delete/rebuild channel abilities.

## Source Evidence

- [`crates/server/src/api/channel.rs:L178-L196`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/channel.rs#L178-L196)
- [`crates/database/crates/channel/src/channel_provider.rs:L89-L134`](https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L89-L134)
- [`crates/database/crates/channel/src/channel_provider.rs:L236-L310`](https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L236-L310)
