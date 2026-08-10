---
title: "List Users"
slug: /console/user-management/list-users/
type: runtime-flow
flow_id: user.console.user.list
truth: STATIC_CONFIRMED
parent_flow: user.console.user
entry_points:
  - "GET /console/api/list_users"
---

# List Users

← [User & Balance Management](/console/user-management/)

## ICFG

```mermaid
flowchart TD
    E["GET /console/api/list_users<br/>list_users()"] --> S["user_service.list_users(db)"]
    R{"DB result"}
    LOOP["for each user"]
    ROLE["get_user_roles(user.id)"]
    SUM["构造 UserSummary"]
    OUT["Return summaries"]
    ERR["Return error"]
    E --> S --> R
    R -->|Err| ERR
    R -->|Ok| LOOP --> ROLE --> SUM --> LOOP
    LOOP --> OUT
    click E "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/user.rs#L163" "Open list_users" _blank
```

## State / Side Effects

- DB READ: all users + per-user roles.

## Source Evidence

- [`crates/server/src/api/user.rs:L163-L205`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/user.rs#L163-L205)
- UserService list/get roles: [`crates/service/crates/user/src/lib.rs:L312-L328`](https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L312-L328)
