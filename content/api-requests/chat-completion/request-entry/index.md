---
title: "Request Entry"
slug: /api-requests/chat-completion/request-entry/
type: runtime-flow
flow_id: user.api.chat.entry
truth: STATIC_CONFIRMED
parent_flow: user.api.chat
entry_points:
  - "server::create_app"
  - "Router::fallback(proxy_handler)"
drill_down:
  - "user.api.chat.auth"
---

# Request Entry

← [Chat Completion](/api-requests/chat-completion/)

## What happens here?

本页只回答“`POST /v1/chat/completions` 为什么会到 `proxy_handler()`”。Server 先合并 Management API、internal routes 和可选 LiveView；未命中的请求交给 `router_app`。在 `router_app` 内，只有 models / usage 是显式路由，`/v1/chat/completions` 不属于这些显式 route，因此进入 `fallback(proxy_handler)`。

## Entry

- **Function:** `server::create_app()`
- **Next:** `router::create_router_app()` → `proxy_handler()`

## ICFG

```mermaid
flowchart TD
    S["create_app() — 组装统一 Axum Router"]
    M["merge(api_router) + merge(internal_app)"]
    L{"enable_liveview?"}
    LV["merge(liveview_router)"]
    F["fallback_service(router_app)"]
    DP["router_app 显式匹配 /v1/models / usage"]
    D{"显式数据面 route 命中?"}
    H["/v1/chat/completions 未命中显式 route<br/>fallback(proxy_handler)"]
    S --> M --> L
    L -->|Yes| LV --> F
    L -->|No| F
    F --> DP --> D
    D -->|Yes| R["执行 models / usage handler"]
    D -->|No| H
    click S "https://github.com/burncloud/burncloud/blob/main/crates/server/src/lib.rs#L31" "Open create_app" _blank
    click F "https://github.com/burncloud/burncloud/blob/main/crates/server/src/lib.rs#L81" "Open fallback_service" _blank
    click H "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L954" "Open data-plane router" _blank
```

## Decisions

- `enable_liveview` only affects whether LiveView routes are merged; it does not remove the data-plane fallback.
- `router_app` explicitly intercepts models / usage before the fallback.

## Continue Drilling Down

→ [Authentication & Admission](/api-requests/chat-completion/authentication-admission/)

## Source Evidence

- [`crates/server/src/lib.rs:L31-L91`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/lib.rs#L31-L91)
- [`crates/router/src/lib.rs:L944-L965`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L944-L965)

**Confidence: HIGH — STATIC CONFIRMED**
