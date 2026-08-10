---
title: "Login Account"
slug: /account/login/
type: runtime-flow
flow_id: user.account.login
truth: STATIC_CONFIRMED
parent_flow: user.account
entry_points:
  - "POST /api/auth/login"
  - "login"
---

# Login Account

← [账号访问](/#/account/)

## What happens here?

登录读取用户记录并验证 bcrypt password hash；成功后生成 JWT，再由 handler 查询角色并返回认证数据。用户不存在和密码错误是两个明确 error path。

## ICFG

```mermaid
flowchart TD
    E["POST /api/auth/login<br/>login()"]
    LS["UserService::login_user()"]
    U["UserDatabase::get_user_by_username()"]
    F{"user exists?"}
    NF["Return UserNotFound"]
    PH{"password_hash exists?"}
    INV["Return InvalidCredentials"]
    V["bcrypt::verify(password, hash)"]
    OK{"valid?"}
    JWT["generate_token(user.id, username)"]
    ROLE["handler: get_user_roles()"]
    OUT["Return AuthData + JWT"]
    E --> LS --> U --> F
    F -->|No| NF
    F -->|Yes| PH
    PH -->|No| INV
    PH -->|Yes| V --> OK
    OK -->|No| INV
    OK -->|Yes| JWT --> ROLE --> OUT
    click E "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/auth.rs#L131" "Open login handler" _blank
    click LS "https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L250" "Open login_user" _blank
```

## Source Evidence

- Handler: [`crates/server/src/api/auth.rs:L131-L164`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/auth.rs#L131-L164)
- Credential verification: [`crates/service/crates/user/src/lib.rs:L250-L310`](https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L250-L310)

**Confidence: HIGH — STATIC CONFIRMED**
