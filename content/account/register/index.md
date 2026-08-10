---
title: "Register Account"
slug: /account/register/
type: runtime-flow
flow_id: user.account.register
truth: STATIC_CONFIRMED
parent_flow: user.account
entry_points:
  - "POST /api/auth/register"
  - "create_user"
---

# Register Account

← [账号访问](/account/)

## What happens here?

注册 handler 调用 `UserService::register_user()`：先查 username 是否已存在，再 bcrypt hash 密码，构造新 user；在写用户前统计真实用户数决定首个用户是否为 admin，随后写 user 并尝试 assign role。handler 再读取 roles 并生成 JWT。

## ICFG

```mermaid
flowchart TD
    E["POST /api/auth/register<br/>create_user()"]
    REG["UserService::register_user()"]
    EXIST["UserDatabase::get_user_by_username()"]
    X{"已存在?"}
    DUP["Return UserAlreadyExists"]
    HASH["bcrypt::hash(password)"]
    CNT["UserDatabase::count_users()"]
    ROLE["count==0 ? admin : user"]
    CU["UserDatabase::create_user()"]
    AR["UserDatabase::assign_role()"]
    RID["Return user_id"]
    GR["handler: get_user_roles()"]
    JWT["generate_token(user_id, username)"]
    OUT["Return id + username + roles + JWT"]
    E --> REG --> EXIST --> X
    X -->|Yes| DUP
    X -->|No| HASH --> CNT --> ROLE --> CU --> AR --> RID --> GR --> JWT --> OUT
    click E "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/auth.rs#L91" "Open register handler" _blank
    click REG "https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L180" "Open register_user" _blank
```

## State / Side Effects

- **DB READ:** username existence, user count.
- **DB WRITE:** user account, role assignment.
- Password hashing is local CPU work.

## Source Evidence

- Handler: [`crates/server/src/api/auth.rs:L91-L130`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/auth.rs#L91-L130)
- Service control flow: [`crates/service/crates/user/src/lib.rs:L180-L238`](https://github.com/burncloud/burncloud/blob/main/crates/service/crates/user/src/lib.rs#L180-L238)

**Confidence: HIGH — STATIC CONFIRMED**
