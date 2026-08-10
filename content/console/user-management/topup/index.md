---
title: "Top Up User Balance"
slug: /console/user-management/topup/
type: runtime-flow
flow_id: user.console.user.topup
truth: STATIC_CONFIRMED
parent_flow: user.console.user
entry_points:
  - "POST /console/api/user/topup"
---

# Top Up User Balance

← [User & Balance Management](/#/console/user-management/)

## What happens here?

handler 默认 currency=USD 后调用 `UserService::topup()`。service 创建 recharge 记录；注释明确 `create_recharge` 已经更新 balance，随后用 `update_balance(..., 0, currency)` 读回当前余额并返回。

## ICFG

```mermaid
flowchart TD
    E["POST /console/api/user/topup<br/>topup()"] --> CUR["currency = payload.currency or USD"]
    S["UserService::topup(user_id,amount,currency)"]
    OBJ["构造 UserRecharge"]
    CR["UserDatabase::create_recharge()"]
    OK{"create success?"}
    ERR["Return error"]
    BAL["UserDatabase::update_balance(user_id,0,currency)<br/>读回 balance"]
    OUT["Return balance + currency"]
    E --> CUR --> S --> OBJ --> CR --> OK
    OK -->|No| ERR
    OK -->|Yes| BAL --> OUT
    click S "https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L331" "Open topup service" _blank
```

## State / Side Effects

- DB WRITE: recharge record and balance update performed by DB layer.
- DB READ/refresh: return current balance.

## Source Evidence

- Handler: [`crates/server/src/api/user.rs:L48-L65`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/user.rs#L48-L65)
- Service: [`crates/service/crates/user/src/lib.rs:L330-L355`](https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L330-L355)
