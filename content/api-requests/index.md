---
title: "API 请求"
slug: /api-requests/
type: runtime-flow
flow_id: user.api
truth: STATIC_CONFIRMED
parent_flow: user.burncloud
drill_down:
  - "user.api.chat"
  - "user.api.video_poll"
  - "user.api.models"
  - "user.api.usage"
---

# API 请求

← [BurnCloud Runtime Atlas](/)

## What happens here?

BurnCloud 的数据面 Router 只有三个显式 route：`GET /v1/models`、`GET /api/v1/usage`、`GET /api/v1/usage/models`；其余数据面路径进入 `Router::fallback(proxy_handler)`。本 Atlas 把最重要的用户动作 `POST /v1/chat/completions` 独立展开，并把 `GET /v1/videos/{task_id}` 的特殊 polling 分支作为另一个用户流程。

## End-to-End Entry Split

```mermaid
flowchart TD
    C["客户端发送 HTTP 请求"]
    APP["统一 Axum Server<br/>server::create_app()"]
    M{"Server 显式 Management / Internal / LiveView route 命中?"}
    MGMT["Yes → 执行对应 Server handler"]
    DP["No → fallback_service(router_app)<br/>进入数据面 Router"]
    R{"数据面显式 route 命中?"}
    MODELS["GET /v1/models<br/>models_handler()"]
    USAGE["GET /api/v1/usage*<br/>usage_handler() / usage_models_handler()"]
    FB["其他路径 → fallback(proxy_handler)"]
    CHAT{"path = /v1/chat/completions ?"}
    CF["进入 Chat Completion 执行树"]
    VIDEO["GET /v1/videos/{task_id}<br/>进入 proxy_handler 特殊 polling 分支"]
    OTHER["其他 fallback path<br/>本 Atlas 不在此页假定其具体业务语义"]
    C --> APP --> M
    M -->|Yes| MGMT
    M -->|No| DP --> R
    R -->|/v1/models| MODELS
    R -->|/api/v1/usage*| USAGE
    R -->|No| FB --> CHAT
    CHAT -->|Yes| CF
    CHAT -->|No| VIDEO
    VIDEO -->|不是该 GET path| OTHER
    click APP "https://github.com/burncloud/burncloud/blob/main/crates/server/src/lib.rs#L31" "Open create_app source" _blank
    click CF "/#/api-requests/chat-completion/" "Drill into Chat Completion" _self
    click VIDEO "/#/api-requests/video-task-polling/" "Drill into video task polling" _self
    click MODELS "/#/api-requests/models/" "Drill into models API" _self
    click USAGE "/#/api-requests/usage/" "Drill into usage API" _self
```

## Continue Drilling Down

- → [Chat Completion](/#/api-requests/chat-completion/)
- → [Video Task Polling](/#/api-requests/video-task-polling/)
- → [Query Models](/#/api-requests/models/)
- → [Query API Usage](/#/api-requests/usage/)

## Source Evidence

- Server composition and fallback: [`crates/server/src/lib.rs:L31-L91`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/lib.rs#L31-L91)
- Data-plane explicit routes and fallback: [`crates/router/src/lib.rs:L937-L965`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L937-L965)
- Video polling branch: [`crates/router/src/lib.rs:L1626-L1707`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1626-L1707)

**Confidence: HIGH — STATIC CONFIRMED.** The `OTHER` branch is intentionally not assigned a business flow on this page.
