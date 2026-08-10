---
title: "API Token Management"
slug: /console/token-management/
type: runtime-flow
flow_id: user.console.token
truth: STATIC_CONFIRMED
parent_flow: user.console
entry_points:
  - "/console/api/tokens"
drill_down:
  - "user.console.token.create"
  - "user.console.token.rotate"
  - "user.console.token.manage"
---

# API Token Management

← [Console 管理](/#/console/)

## User Flow

```mermaid
flowchart TD
    U["JWT-authenticated Console client"] --> R{"Token action"}
    R --> C["Create token"]
    R --> L["List / Get token"]
    R --> S["Update status / Delete"]
    R --> ROT["Rotate key"]
    R --> REV["Revoke old key"]
    R --> IP["Set IP whitelist"]
    click C "/#/console/token-management/create/" "Create" _self
    click ROT "/#/console/token-management/rotate/" "Rotate / revoke" _self
    click S "/#/console/token-management/manage/" "Other token mutations" _self
    click REV "/#/console/token-management/rotate/" "Rotate / revoke" _self
    click IP "/#/console/token-management/manage/" "Whitelist" _self
```

## Entry Routes

`/console/api/tokens` and `/console/api/tokens/{token}` plus rotate/revoke-old/ip-whitelist child routes.

## Source Evidence

- [`crates/server/src/api/token.rs:L40-L56`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/token.rs#L40-L56)
