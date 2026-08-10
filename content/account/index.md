---
title: "账号访问"
slug: /account/
type: runtime-flow
flow_id: user.account
truth: STATIC_CONFIRMED
parent_flow: user.burncloud
drill_down:
  - "user.account.register"
  - "user.account.login"
  - "user.account.forgot"
  - "user.account.reset"
  - "user.account.oauth"
---

# 账号访问

← [BurnCloud Runtime Atlas](/)

## User Flow

```mermaid
flowchart TD
    U["用户进行账号操作"]
    R["POST /api/auth/register"]
    L["POST /api/auth/login"]
    F["POST /api/auth/forgot-password"]
    P["POST /api/auth/reset-password"]
    O["GET /api/auth/google 或 /github"]
    U --> R
    U --> L
    U --> F
    U --> P
    U --> O
    click R "/account/register/" "Register" _self
    click L "/account/login/" "Login" _self
    click F "/account/forgot-password/" "Forgot password" _self
    click P "/account/reset-password/" "Reset password" _self
    click O "/account/oauth/" "OAuth URL" _self
```

这些 routes 在 `auth::public_routes()` 中注册，不经过 `/console/api/*` 的 JWT middleware。

## Source Evidence

- [`crates/server/src/api/auth.rs:L68-L90`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/auth.rs#L68-L90)
