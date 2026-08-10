---
title: "Recharge History"
slug: /console/user-management/recharges/
type: runtime-flow
flow_id: user.console.user.recharges
truth: STATIC_CONFIRMED
parent_flow: user.console.user
entry_points:
  - "GET /console/api/user/recharges"
---

# Recharge History

← [User & Balance Management](/console/user-management/)

## What happens here?

该 Console route 位于受 `auth_middleware` 保护的 router 中，因此 handler 可从 Axum request extensions 获得 `Claims`。`list_recharges()` 直接使用 `claims.sub` 作为 user id，调用 `UserService::list_recharges()`，再进入数据库层读取该用户的 recharge history；成功返回列表，失败走统一 `err(e)` response。

## ICFG

```mermaid
flowchart TD
    E["用户查询自己的充值记录<br/>GET /console/api/user/recharges"]
    MW["受保护 Router 已完成 JWT middleware<br/>Claims 注入 request extensions"]
    H["读取 Claims.sub<br/>list_recharges()"]
    S["调用 UserService::list_recharges(db, claims.sub)"]
    DB["查询用户 recharge rows<br/>UserRecharge database path"]
    Q{"Result"}
    OK["Ok → Return recharge list"]
    ERR["Err → Return err(e)"]
    E --> MW --> H --> S --> DB --> Q
    Q -->|Ok| OK
    Q -->|Err| ERR
    click H "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/user.rs#L251" "Open handler" _blank
    click S "https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L357" "Open service" _blank
    click DB "https://github.com/burncloud/burncloud/blob/main/crates/database/crates/user/src/lib.rs#L504" "Open DB query" _blank
```

## State / Side Effects

- **DB READ:** recharge history for authenticated `claims.sub`.
- No write is visible on this GET path.

## Source Evidence

- Route group: [`crates/server/src/api/user.rs:L67-L78`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/user.rs#L67-L78)
- Handler and exact user-id source: [`crates/server/src/api/user.rs:L250-L262`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/user.rs#L250-L262)
- Service: [`crates/service/crates/user/src/lib.rs:L357-L362`](https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L357-L362)
- Database: [`crates/database/crates/user/src/lib.rs:L504-L510`](https://github.com/burncloud/burncloud/blob/main/crates/database/crates/user/src/lib.rs#L504-L510)

**Confidence: HIGH — STATIC CONFIRMED.**
