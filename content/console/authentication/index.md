---
title: "Protected Console Authentication"
slug: /console/authentication/
type: runtime-flow
flow_id: user.console.auth
truth: STATIC_CONFIRMED
parent_flow: user.console
entry_points:
  - "/console/api/* protected router"
  - "auth_middleware"
---

# Protected Console Authentication

← [Console 管理](/console/)

## What happens here?

所有合并到 protected router 的管理 API 先经过 `auth_middleware()`。middleware 只接受 `Authorization: Bearer ...`，调用 `verify_jwt()`；成功后把 `Claims` 注入 request extensions，再执行真正 handler。

## ICFG

```mermaid
flowchart TD
    E["受保护 Console API 请求"] --> M["auth_middleware(req,next)"]
    H["读取 Authorization header"]
    P{"存在 Bearer prefix?"}
    U["Return 401"]
    V["verify_jwt(token)"]
    OK{"JWT valid?"}
    X["req.extensions_mut().insert(Claims)"]
    N["next.run(req) → 具体业务 handler"]
    E --> M --> H --> P
    P -->|No| U
    P -->|Yes| V --> OK
    OK -->|No| U
    OK -->|Yes| X --> N
    click M "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/auth.rs#L242" "Open auth_middleware" _blank
```

## State / Side Effects

- Request-local mutation: inject `Claims` extension.
- No DB query in this middleware; JWT is decoded with secret.

## Source Evidence

- Protected middleware composition: [`crates/server/src/api/mod.rs:L18-L55`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/mod.rs#L18-L55)
- Middleware: [`crates/server/src/api/auth.rs:L239-L265`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/auth.rs#L239-L265)

**Confidence: HIGH — STATIC CONFIRMED**
