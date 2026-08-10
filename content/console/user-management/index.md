---
title: "User & Balance Management"
slug: /console/user-management/
type: runtime-flow
flow_id: user.console.user
truth: STATIC_CONFIRMED
parent_flow: user.console
entry_points:
  - "/console/api/user/*"
drill_down:
  - "user.console.user.list"
  - "user.console.user.topup"
  - "user.console.user.recharges"
---

# User & Balance Management

← [Console 管理](/#/console/)

## User Flow

```mermaid
flowchart TD
    U["JWT-authenticated Console request"] --> D{"Action"}
    L["List users"]
    T["Top up user balance"]
    R["List recharge history"]
    C["Check username / console register/login"]
    D -->|GET list_users| L
    D -->|POST topup| T
    D -->|GET recharges| R
    D -->|other user routes| C
    click L "/#/console/user-management/list-users/" "List users" _self
    click T "/#/console/user-management/topup/" "Top up" _self
    click R "/#/console/user-management/recharges/" "Recharge history" _self
```

注意：这些 `user::routes()` 被 merge 到 protected router，因此即使 path 名称包含 `register/login`，在当前组合方式下也会经过 Console `auth_middleware`。

## Source Evidence

- Route definitions: [`crates/server/src/api/user.rs:L67-L78`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/user.rs#L67-L78)
- Protected merge: [`crates/server/src/api/mod.rs:L18-L55`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/mod.rs#L18-L55)
