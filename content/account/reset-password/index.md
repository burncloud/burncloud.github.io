---
title: "Reset Password"
slug: /account/reset-password/
type: runtime-flow
flow_id: user.account.reset
truth: STATIC_CONFIRMED
parent_flow: user.account
entry_points:
  - "POST /api/auth/reset-password"
---

# Reset Password

← [账号访问](/account/)

## What happens here?

service 读取 reset token，拒绝已使用或过期 token；有效时 bcrypt hash 新密码，更新 user password hash，再把 reset token 标记 used。

## ICFG

```mermaid
flowchart TD
    E["POST /api/auth/reset-password"] --> S["reset_password(db, token, new_password)"]
    T["PasswordResetDatabase::get_token()"]
    F{"token exists?"}
    INV["InvalidCredentials"]
    USED{"used_at 已存在?"}
    EXP["解析 expires_at 并比较 Utc::now()"]
    OLD{"已过期?"}
    HASH["bcrypt::hash(new_password)"]
    UP["UserDatabase::update_password_hash()"]
    MARK["PasswordResetDatabase::mark_used()"]
    OK["Return success"]
    E --> S --> T --> F
    F -->|No| INV
    F -->|Yes| USED
    USED -->|Yes| INV
    USED -->|No| EXP --> OLD
    OLD -->|Yes| INV
    OLD -->|No| HASH --> UP --> MARK --> OK
    click S "https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L395" "Open reset_password" _blank
```

## State / Side Effects

- **DB READ:** password reset token.
- **DB WRITE:** password hash + reset token used marker.

## Source Evidence

- Handler: [`crates/server/src/api/auth.rs:L198-L219`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/auth.rs#L198-L219)
- Service: [`crates/service/crates/user/src/lib.rs:L395-L423`](https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L395-L423)

**Confidence: HIGH — STATIC CONFIRMED**
