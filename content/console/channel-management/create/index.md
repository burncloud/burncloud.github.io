---
title: "Create Channel"
slug: /console/channel-management/create/
type: runtime-flow
flow_id: user.console.channel.create
truth: STATIC_CONFIRMED
parent_flow: user.console.channel
entry_points:
  - "POST /console/api/channel"
---

# Create Channel

← [Channel Management](/console/channel-management/)

## What happens here?

admin handler 把 `ChannelDto` 转成 `Channel` 后调用 service。DB 层在 transaction 中插入 `channel_providers` 并得到新 ID，commit 后立即调用 `sync_abilities()`：删除旧 abilities（新记录通常没有），若 channel enabled，则按 `models × groups` 写入 `channel_abilities`。

## ICFG

```mermaid
flowchart TD
    E["POST /console/api/channel<br/>create_channel()"] --> A["check_admin()"]
    OK{"admin?"}
    DENY["Return access error"]
    DTO["payload.into_channel()"]
    S["ChannelService::create()"]
    DB["ChannelProviderModel::create()"]
    TX["BEGIN transaction"]
    INS["INSERT channel_providers"]
    DIA{"Postgres or SQLite?"}
    PG["RETURNING id"]
    SQ["SELECT last_insert_rowid()"]
    COM["COMMIT"]
    ID["channel.id = id"]
    SYNC["sync_abilities(channel)"]
    EN{"channel.status == 1?"}
    STOP["Return id; disabled channel has no abilities"]
    LOOP["models × groups → INSERT channel_abilities"]
    OUT["Return ChannelCreated{id}"]
    E --> A --> OK
    OK -->|No| DENY
    OK -->|Yes| DTO --> S --> DB --> TX --> INS --> DIA
    DIA -->|Postgres| PG --> COM
    DIA -->|SQLite| SQ --> COM
    COM --> ID --> SYNC --> EN
    EN -->|No| STOP --> OUT
    EN -->|Yes| LOOP --> OUT
    click DB "https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L9" "Open create" _blank
    click SYNC "https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L236" "Open sync_abilities" _blank
```

## State / Side Effects

- DB WRITE: `channel_providers`.
- DB WRITE: `channel_abilities` generated from channel models/groups when enabled.

## Source Evidence

- Handler: [`crates/server/src/api/channel.rs:L161-L176`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/channel.rs#L161-L176)
- DB create: [`crates/database/crates/channel/src/channel_provider.rs:L9-L87`](https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L9-L87)
- Ability sync: [`crates/database/crates/channel/src/channel_provider.rs:L236-L310`](https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_provider.rs#L236-L310)

**Confidence: HIGH — STATIC CONFIRMED**
