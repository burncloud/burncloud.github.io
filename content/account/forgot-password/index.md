---
title: "Forgot Password"
slug: /account/forgot-password/
type: runtime-flow
flow_id: user.account.forgot
truth: STATIC_CONFIRMED
parent_flow: user.account
entry_points:
  - "POST /api/auth/forgot-password"
---

# Forgot Password

← [账号访问](/account/)

## What happens here?

handler 交给 `request_password_reset(email)`。service 按 email 查 user，生成 UUID reset token 与 1 小时过期时间，并写 password reset token。为了避免 email enumeration，handler 在 `UserNotFound` 时仍返回与成功相同的消息。

## ICFG

```mermaid
flowchart TD
    E["POST /api/auth/forgot-password"] --> S["request_password_reset(db,email)"]
    U["UserDatabase::get_user_by_email()"]
    F{"user exists?"}
    NF["UserNotFound"]
    T["生成 UUID token + expires_at=now+1h"]
    W["PasswordResetDatabase::create_token()"]
    OK["Return generic success message"]
    ER["Other error → failed response"]
    E --> S --> U --> F
    F -->|No| NF --> OK
    F -->|Yes| T --> W --> OK
    S -->|other error| ER
    click S "https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L383" "Open reset request service" _blank
```

## State / Side Effects

- **DB READ:** user by email.
- **DB WRITE:** password reset token.

## Source Evidence

- Handler: [`crates/server/src/api/auth.rs:L166-L196`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/auth.rs#L166-L196)
- Service: [`crates/service/crates/user/src/lib.rs:L383-L393`](https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L383-L393)

**Confidence: HIGH — STATIC CONFIRMED**
