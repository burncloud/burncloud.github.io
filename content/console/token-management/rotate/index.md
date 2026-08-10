---
title: "Rotate / Revoke Old Token Key"
slug: /console/token-management/rotate/
type: runtime-flow
flow_id: user.console.token.rotate
truth: STATIC_CONFIRMED
parent_flow: user.console.token
entry_points:
  - "POST /console/api/tokens/{token}/rotate"
  - "POST .../revoke-old"
---

# Rotate / Revoke Old Token Key

← [API Token Management](/#/console/token-management/)

## What happens here?

rotate handler 把当前 token、transition hours 与 `revoke_old` 交给 `TokenService::rotate()`，真正 rotation semantics 在 `RouterTokenModel::rotate()`。单独的 revoke-old route 则直接调用 `revoke_old_key()`。

## ICFG

```mermaid
flowchart TD
    E["POST .../{token}/rotate"] --> H["rotate_token()"]
    P["读取 transition_period_hours / revoke_old"]
    S["TokenService::rotate()"]
    DB["RouterTokenModel::rotate()"]
    R{"result"}
    OK["Return TokenRotationResult"]
    ERR["Return error"]
    REV["POST .../{token}/revoke-old"] --> RH["revoke_old_key()"] --> RS["TokenService::revoke_old_key()"] --> RDB["RouterTokenModel::revoke_old_key()"]
    E --> H --> P --> S --> DB --> R
    R -->|Ok| OK
    R -->|Err| ERR
    click H "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/token.rs#L192" "Open rotate handler" _blank
    click S "https://github.com/burncloud/burncloud/blob/main/crates/service/crates/token/src/lib.rs#L79" "Open rotate service" _blank
```

## Source Evidence

- Rotate handler: [`crates/server/src/api/token.rs:L192-L225`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/token.rs#L192-L225)
- Revoke handler: [`crates/server/src/api/token.rs:L227-L251`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/token.rs#L227-L251)
- Service dispatch: [`crates/service/crates/token/src/lib.rs:L68-L96`](https://github.com/burncloud/burncloud/blob/main/crates/service/crates/token/src/lib.rs#L68-L96)

**Confidence: HIGH for handler→service→DB model dispatch.**
