---
title: "Chat Model Resolution"
slug: /api-requests/chat-completion/model-resolution/
type: runtime-flow
flow_id: user.api.chat.model
truth: STATIC_CONFIRMED
parent_flow: user.api.chat
entry_points:
  - "proxy_handler body phase"
drill_down:
  - "user.api.chat.channel"
---

# Chat Model Resolution

← [Chat Completion](/#/api-requests/chat-completion/)

## What happens here?

认证通过后，`proxy_handler()` 把请求 body 完整缓冲为 bytes，再从 JSON 顶层读取 `model`。对 `POST /v1/chat/completions` 而言，后续 `proxy_logic()` 只有在 JSON 可解析且 `model` 为字符串时才能进入 model-based routing；否则候选列表保持为空，最终返回 `no_available_channel`。

## Entry

- **Route:** `POST /v1/chat/completions`（由 fallback 接收）
- **Function:** `proxy_handler()` → `proxy_logic()`
- **Input of interest:** request JSON `model`

## ICFG

```mermaid
flowchart TD
    E["认证与准入已通过<br/>proxy_handler()"]
    BODY["缓冲请求 Body<br/>body.collect().await"]
    BOK{"Body 读取成功?"}
    E400["Early Return 400<br/>body_read_error"]
    BYTES["保留 body_bytes 并尝试 JSON 解析"]
    CALL["创建 UnifiedTokenCounter<br/>调用 proxy_logic()"]
    JSON{"proxy_logic(): JSON 可解析?"}
    MODEL{"body.model 是 string?"}
    ROUTE["按 model 建立 scheduler / routing 输入"]
    NONE["不建立 model candidates"]
    EMPTY{"最终 candidates 为空?"}
    E404["Return 404<br/>no_available_channel"]
    NEXT["进入 Channel Selection"]
    E --> BODY --> BOK
    BOK -->|No| E400
    BOK -->|Yes| BYTES --> CALL --> JSON
    JSON -->|No| NONE --> EMPTY
    JSON -->|Yes| MODEL
    MODEL -->|No| NONE
    MODEL -->|Yes| ROUTE --> NEXT
    EMPTY -->|Yes| E404
    click BODY "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1521" "Open body collection" _blank
    click CALL "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1715" "Open proxy_logic call" _blank
    click ROUTE "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2030" "Open model routing phase" _blank
    click NEXT "/#/api-requests/chat-completion/channel-selection/" "Channel Selection" _self
```

## Decisions

- Body collection failure is an early `400` before `proxy_logic()`.
- `proxy_logic()` only enters model-based route recovery when JSON parses and `model` is a string.
- No model-derived candidates eventually reaches the explicit `candidates.is_empty()` response path.

## State / Side Effects

本阶段只构造 request-local bytes/JSON/model routing input；没有静态确认的 DB write。

## Continue Drilling Down

→ [Channel Selection](/#/api-requests/chat-completion/channel-selection/)

## Source Evidence

- Body buffering and model extraction in handler: [`crates/router/src/lib.rs:L1521-L1627`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1521-L1627)
- `proxy_logic()` JSON/model gate and routing setup: [`crates/router/src/lib.rs:L2011-L2270`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2011-L2270)
- Empty-candidate response: [`crates/router/src/lib.rs:L2272-L2295`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2272-L2295)

**Confidence: HIGH — STATIC CONFIRMED.**
