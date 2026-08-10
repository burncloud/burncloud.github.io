---
title: "Channel Management"
slug: /console/channel-management/
type: runtime-flow
flow_id: user.console.channel
truth: STATIC_CONFIRMED
parent_flow: user.console
entry_points:
  - "/console/api/channel"
drill_down:
  - "user.console.channel.list"
  - "user.console.channel.create"
  - "user.console.channel.update"
  - "user.console.channel.getdelete"
---

# Channel Management

← [Console 管理](/console/)

## What happens here?

同一 `/console/api/channel` route 根据 HTTP method 分派 list/create/update，`/console/api/channel/{id}` 分派 get/delete。所有操作先经过 Console JWT middleware；Channel handlers 再调用 `check_admin()` 查询用户 roles，只有 admin 才进入 `ChannelService`。

## End-to-End Flow

```mermaid
flowchart TD
    U["Admin 对 Channel 发起 CRUD 请求"] --> JWT["auth_middleware() 验证 JWT"]
    JWT --> H["进入 Channel handler"]
    H --> ADM["check_admin() → UserDatabase::get_user_roles()"]
    A{"包含 admin role?"}
    DENY["Return Admin access required"]
    D{"HTTP method / path"}
    LIST["GET collection → list_channels()"]
    CREATE["POST → create_channel()"]
    UPDATE["PUT → update_channel()"]
    GETDEL["GET/DELETE {id} → get/delete"]
    U --> JWT --> H --> ADM --> A
    A -->|No| DENY
    A -->|Yes| D
    D -->|GET collection| LIST
    D -->|POST| CREATE
    D -->|PUT| UPDATE
    D -->|GET/DELETE id| GETDEL
    click LIST "/console/channel-management/list/" "List" _self
    click CREATE "/console/channel-management/create/" "Create" _self
    click UPDATE "/console/channel-management/update/" "Update" _self
    click GETDEL "/console/channel-management/get-delete/" "Get / Delete" _self
```

## Source Evidence

- Route bindings + admin check: [`crates/server/src/api/channel.rs:L111-L137`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/channel.rs#L111-L137)
