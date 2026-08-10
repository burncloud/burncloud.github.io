---
title: "Authentication & Admission"
slug: /api-requests/chat-completion/authentication-admission/
type: runtime-flow
flow_id: user.api.chat.auth
truth: STATIC_CONFIRMED
parent_flow: user.api.chat
entry_points:
  - "proxy_handler"
drill_down:
  - "user.api.chat.model"
---

# Authentication & Admission

← [Chat Completion](/#/api-requests/chat-completion/)

## What happens here?

`proxy_handler()` 从三个 header 位置读取用户凭据，优先查询新 token/user 关联；找不到时再走 legacy token 校验，legacy 判 Invalid 时才尝试 JWT。成功得到 user/group/quota 后，还会执行 quota 上限检查和本地 rate limiter。

## Entry

- **Function:** `proxy_handler()`
- **Called From:** data-plane fallback

## ICFG

```mermaid
flowchart TD
    E["进入认证阶段<br/>proxy_handler()"]
    HDR["读取 Authorization Bearer / x-api-key / x-goog-api-key"]
    H{"找到 credential?"}
    E401["Early Return 401 missing_token"]
    V1["查询新 token + user 信息<br/>RouterDatabase::validate_token_and_get_info()"]
    FOUND{"查询到记录?"}
    OK["得到 user_id / group / quota / order_type / price_cap"]
    V2["Legacy token 详细校验<br/>validate_token_detailed()"]
    ST{"Valid / Expired / Invalid / DB error"}
    EXP["Early Return 401 token_expired"]
    JWT["Invalid legacy token → 尝试 JWT decode"]
    JOK{"JWT valid?"}
    INV["Early Return 401 invalid_token"]
    DBE["Early Return 500 Internal Auth Error"]
    Q{"quota_limit >= 0 且 used >= limit?"}
    Q402["Early Return 402 insufficient_quota"]
    RL["本地限流<br/>state.limiter.check(user_id, 1.0)"]
    ROK{"admitted?"}
    R429["Early Return 429 rate_limit_exceeded"]
    NEXT["进入 Body / Model Resolution"]
    E --> HDR --> H
    H -->|No| E401
    H -->|Yes| V1 --> FOUND
    FOUND -->|Yes| OK
    FOUND -->|No| V2 --> ST
    ST -->|Valid| OK
    ST -->|Expired| EXP
    ST -->|Invalid| JWT --> JOK
    JOK -->|No| INV
    JOK -->|Yes| OK
    ST -->|DB error| DBE
    OK --> Q
    Q -->|Yes| Q402
    Q -->|No| RL --> ROK
    ROK -->|No| R429
    ROK -->|Yes| NEXT
    click E "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1359" "Open proxy_handler" _blank
    click V1 "https://github.com/burncloud/burncloud/blob/main/crates/database/crates/router/src/lib.rs#L176" "Open token DB validation" _blank
```

## State / Side Effects

- **DB READ:** token/user/quota/order routing context.
- **ASYNC DB WRITE:** successful DB-token paths spawn `update_token_accessed_time()`.
- **Local state:** rate limiter consumes one local admission unit when accepted.

## Decisions

- JWT is not the first credential path; it is a fallback after new/legacy token checks.
- quota and local rate-limit rejection happen before request body routing.

## Continue Drilling Down

→ [Model / Request Resolution](/#/api-requests/chat-completion/model-resolution/)

## Source Evidence

- [`crates/router/src/lib.rs:L1374-L1519`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1374-L1519)
- [`crates/database/crates/router/src/lib.rs:L176-L227`](https://github.com/burncloud/burncloud/blob/main/crates/database/crates/router/src/lib.rs#L176-L227)

**Confidence: HIGH — STATIC CONFIRMED**
