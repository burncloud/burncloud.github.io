---
title: "Console 管理"
slug: /console/
type: runtime-flow
flow_id: user.console
truth: STATIC_CONFIRMED
parent_flow: user.burncloud
drill_down:
  - "user.console.auth"
  - "user.console.channel"
  - "user.console.token"
  - "user.console.user"
  - "user.console.logs"
  - "user.console.billing"
  - "user.console.monitor"
  - "user.console.cache"
  - "user.console.security"
---

# Console 管理

← [BurnCloud Runtime Atlas](/)

## What happens here?

`api::routes()` 把 auth public routes 与受保护的 Console routes 分开。Channel、Token、Log、Monitor、User、Security、Billing、Cache 等 routes 合并后统一套 `auth_middleware`；其中 Channel handler 还会额外执行 admin role 检查。

## User Execution Tree

```mermaid
flowchart TD
    C["Console / 管理客户端"] --> A["JWT Protected API Authentication"]
    A --> CH["Channel 管理"]
    A --> TK["API Token 管理"]
    A --> U["用户 / 余额管理"]
    A --> L["Logs / Usage"]
    A --> B["Billing Summary"]
    A --> M["Monitor"]
    A --> CA["Cache"]
    A --> S["Security"]
    click A "/console/authentication/" "Protected auth" _self
    click CH "/console/channel-management/" "Channel management" _self
    click TK "/console/token-management/" "Token management" _self
    click U "/console/user-management/" "User management" _self
    click L "/console/logs-usage/" "Logs / usage" _self
    click B "/console/billing-summary/" "Billing summary" _self
    click M "/console/monitor/" "Monitor" _self
    click CA "/console/cache/" "Cache" _self
    click S "/console/security/" "Security" _self
```

## Source Evidence

- Protected router composition: [`crates/server/src/api/mod.rs:L18-L55`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/api/mod.rs#L18-L55)
