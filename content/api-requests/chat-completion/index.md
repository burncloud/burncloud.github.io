---
title: "Chat Completion — End-to-End"
slug: /api-requests/chat-completion/
type: runtime-flow
flow_id: user.api.chat
truth: STATIC_CONFIRMED
parent_flow: user.api
entry_points:
  - "POST /v1/chat/completions"
  - "Router::fallback(proxy_handler)"
drill_down:
  - "user.api.chat.entry"
  - "user.api.chat.auth"
  - "user.api.chat.model"
  - "user.api.chat.channel"
  - "user.api.chat.provider"
  - "user.api.chat.streaming"
  - "user.api.chat.billing"
---

# Chat Completion — End-to-End

← [API 请求](/api-requests/)

## What happens here?

`POST /v1/chat/completions` 没有独立注册 handler；它先进入统一 Server，随后由数据面 `Router::fallback(proxy_handler)` 接收。`proxy_handler()` 完成凭据、quota、限流和 body/model 解析，再调用 `proxy_logic()`：后者恢复候选 Channel、按 `/v1/chat/completions` 的协议约束保留 OpenAI/Zai Channel、逐候选执行 Shaper/Circuit Breaker、原生透传或运行时 adaptor 转换，并在失败时尝试后续候选。返回 handler 后再完成 usage/cost、日志与异步 quota 扣减。

## Entry

- **User action:** `POST /v1/chat/completions`
- **HTTP binding:** data-plane fallback, not a dedicated Chat handler
- **Function:** `proxy_handler()`
- **Called From:** `Router::fallback(proxy_handler)`

## End-to-End Request Flow

```mermaid
flowchart TD
    U["用户发送 OpenAI-compatible Chat 请求<br/>POST /v1/chat/completions"]
    S["Server 未命中显式管理路由<br/>fallback_service(router_app)"]
    E["数据面 fallback 接收请求<br/>proxy_handler()"]
    A["认证、quota 与本地限流<br/>proxy_handler() admission phase"]
    B["缓冲 JSON Body 并读取 model<br/>body.collect() + serde_json"]
    P["建立路由上下文<br/>proxy_logic()"]
    C["生成并排序候选 Channel<br/>ModelRouter::route_with_scheduler()"]
    PF["按 Chat path 保留 OpenAI / Zai Channel<br/>proxy_logic() path filter"]
    X["逐候选执行 Shaper / CB / Provider 请求<br/>proxy_logic() candidate loop"]
    D{"Channel protocol"}
    PT["OpenAI 原生请求直接透传<br/>should_passthrough()"]
    CV["Zai 等转换路径进入运行时 adaptor<br/>DynamicAdaptorFactory"]
    SR["处理普通或 Streaming 响应并累计 usage"]
    BILL["计算 cost、写日志、cost>0 异步扣 quota<br/>proxy_handler() settlement"]
    OUT["注入 Channel / Model 响应头并返回客户端"]
    U --> S --> E --> A --> B --> P --> C --> PF --> X --> D
    D -->|OpenAI native| PT --> SR
    D -->|Convert| CV --> SR
    SR --> BILL --> OUT
    click E "/api-requests/chat-completion/request-entry/" "Request Entry" _self
    click A "/api-requests/chat-completion/authentication-admission/" "Authentication & Admission" _self
    click B "/api-requests/chat-completion/model-resolution/" "Model Resolution" _self
    click C "/api-requests/chat-completion/channel-selection/" "Channel Selection" _self
    click X "/api-requests/chat-completion/provider-execution/" "Provider Execution" _self
    click SR "/api-requests/chat-completion/streaming-response/" "Streaming Response" _self
    click BILL "/api-requests/chat-completion/billing-settlement/" "Billing" _self
```

## Decisions

- Missing / invalid credential can end the request before body routing.
- Exhausted quota → `402`; local rate limiter reject → `429`.
- For OpenAI-format paths including `/v1/chat/completions`, candidates whose `ChannelType` is not `OpenAI | Zai` are skipped before `Upstream` construction.
- OpenAI Channel + `/v1/chat/completions` is statically confirmed passthrough; conversion uses **⚠ Dynamic** adaptor resolution for the selected runtime ChannelType/API version.

## Continue Drilling Down

- → [请求进入系统](/api-requests/chat-completion/request-entry/)
- → [身份认证与准入](/api-requests/chat-completion/authentication-admission/)
- → [Model Resolution](/api-requests/chat-completion/model-resolution/)
- → [Channel Selection](/api-requests/chat-completion/channel-selection/)
- → [Provider Execution](/api-requests/chat-completion/provider-execution/)
- → [Streaming Response](/api-requests/chat-completion/streaming-response/)
- → [Billing & Logging](/api-requests/chat-completion/billing-settlement/)

## Source Evidence

- Server fallback composition: [`crates/server/src/lib.rs:L65-L89`](https://github.com/burncloud/burncloud/blob/main/crates/server/src/lib.rs#L65-L89)
- Data-plane explicit routes + fallback: [`crates/router/src/lib.rs:L954-L963`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L954-L963)
- `proxy_handler()`: [`crates/router/src/lib.rs:L1359-L1982`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1359-L1982)
- Chat/OpenAI path channel filtering: [`crates/router/src/lib.rs:L2160-L2182`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2160-L2182)
- Provider candidate loop: [`crates/router/src/lib.rs:L2369-L4167`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2369-L4167)
- Passthrough decision: [`crates/router/src/passthrough.rs:L47-L87`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/passthrough.rs#L47-L87)

**Confidence: HIGH — STATIC CONFIRMED.** Concrete conversion adaptor is runtime-selected and remains **DYNAMIC**.
