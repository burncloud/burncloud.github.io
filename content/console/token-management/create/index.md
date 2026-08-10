---
title: "Create API Token"
slug: /console/token-management/create/
type: runtime-flow
flow_id: user.console.token.create
truth: STATIC_CONFIRMED
parent_flow: user.console.token
entry_points:
  - "POST /console/api/tokens"
---

# Create API Token

← [API Token Management](/console/token-management/)

## ICFG

```mermaid
flowchart TD
    E["POST /console/api/tokens<br/>create_token()"] --> NOW["读取 UNIX timestamp"]
    KEY["生成 bc_live_{UUID}"]
    OBJ["构造 RouterToken<br/>status=active / used_quota=0 / key_version=1"]
    S["TokenService::create()"]
    DB["RouterTokenModel::create() → DB write"]
    R{"result"}
    OK["Return created + plaintext token"]
    ERR["Return error"]
    E --> NOW --> KEY --> OBJ --> S --> DB --> R
    R -->|Ok| OK
    R -->|Err| ERR
    click E "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/token.rs#L73" "Open handler" _blank
    click S "https://github.com/burncloud/burncloud/blob/main/crates/service/crates/token/src/lib.rs#L22" "Open service" _blank
```

## State / Side Effects

- DB WRITE: new router token row.
- Response returns generated plaintext token.

## Source Evidence

- [`crates/server/src/api/token.rs:L73-L122`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/token.rs#L73-L122)
- [`crates/service/crates/token/src/lib.rs:L22-L25`](https://github.com/burncloud/burncloud/blob/main/crates/service/crates/token/src/lib.rs#L22-L25)
