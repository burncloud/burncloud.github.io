---
title: "List / Get / Status / Delete / IP Whitelist"
slug: /console/token-management/manage/
type: runtime-flow
flow_id: user.console.token.manage
truth: STATIC_CONFIRMED
parent_flow: user.console.token
entry_points:
  - "GET/PUT/DELETE /console/api/tokens*"
---

# List / Get / Status / Delete / IP Whitelist

← [API Token Management](/#/console/token-management/)

## ICFG

```mermaid
flowchart TD
    U["Token management request"] --> M{"Route / method"}
    L["GET collection → TokenService::list()"]
    G["GET {token} → TokenService::validate()"]
    S["PUT {token} → update_status()"]
    D["DELETE {token} → delete()"]
    IP["POST {token}/ip-whitelist → set_ip_whitelist()"]
    DB["RouterTokenModel 对应 DB operation"]
    R["Return success / not-found / error"]
    M -->|list| L --> DB
    M -->|get| G --> DB
    M -->|status| S --> DB
    M -->|delete| D --> DB
    M -->|whitelist| IP --> DB
    DB --> R
    click U "https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/token.rs#L40" "Open token routes" _blank
```

## State / Side Effects

- List/Get: DB reads.
- Update/Delete/IP whitelist: DB mutations.

## Source Evidence

- Routes and handlers: [`crates/server/src/api/token.rs:L40-L260`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/token.rs#L40-L260)
- Service mapping: [`crates/service/crates/token/src/lib.rs:L16-L102`](https://github.com/burncloud/burncloud/blob/main/crates/service/crates/token/src/lib.rs#L16-L102)
