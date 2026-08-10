---
title: "Streaming Response"
slug: /api-requests/chat-completion/streaming-response/
type: runtime-flow
flow_id: user.api.chat.streaming
truth: STATIC_CONFIRMED
parent_flow: user.api.chat
entry_points:
  - "successful upstream streaming response"
drill_down:
  - "user.api.chat.billing"
---

# Streaming Response

← [Chat Completion](/#/api-requests/chat-completion/) · ← [Provider Execution](/#/api-requests/chat-completion/provider-execution/)

## What happens here?

Streaming 成功状态不会立即视为最终 success。代码先 peek 第一块，若首块直接暴露 SSE error、空响应或读取错误，则在 HTTP response 交给 client 前把当前候选标成失败并 failover。通过 peek 后，流一边转发给 client，一边解析 usage/content；结束时再决定是否记录 success 或 empty-response penalty。

## ICFG

```mermaid
flowchart TD
    E["收到 upstream streaming 2xx response"]
    P["peek_first_chunk(stream, timeout)"]
    PR{"PeekResult"}
    FC["HasFirstChunk → 检查 SSE error"]
    SSE{"首块是 SSE error?"}
    FAIL["记录 failure / affinity eviction<br/>continue next candidate"]
    EMPTY["Empty / Error → 记录 failure<br/>continue next candidate"]
    TIME["Timeout → 不判失败，继续原 stream"]
    CHAIN["无错误 → first_chunk + remaining_stream"]
    PARSER["按 ChannelType 选择 parser<br/>parse_chunk_or_default()"]
    USAGE["更新 UnifiedTokenCounter"]
    FWD["Body::from_stream(...) 转发客户端"]
    DONE["stream done callback / state update"]
    E --> P --> PR
    PR -->|HasFirstChunk| FC --> SSE
    SSE -->|Yes| FAIL
    SSE -->|No| CHAIN
    PR -->|Empty / Error| EMPTY
    PR -->|Timeout| TIME --> CHAIN
    CHAIN --> PARSER --> USAGE --> FWD --> DONE
    click P "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L3293" "Open stream peek" _blank
    click PARSER "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L3362" "Open stream parser" _blank
    click FAIL "/#/api-requests/chat-completion/provider-execution/failure-retry/" "Failure / retry" _self
```

## Dynamic Boundary

具体 stream parser 由 `channel_type` 决定。**⚠ Dynamic**，本页只确认 parser selection + shared token counter behavior。

## State / Side Effects

- `UnifiedTokenCounter` accumulates/set usage.
- Circuit breaker/channel state/affinity can mutate on stream failure/success.
- Response body is streamed to client instead of fully buffered.

## Continue Drilling Down

→ [Billing & Logging](/#/api-requests/chat-completion/billing-settlement/)

## Source Evidence

- OpenAI converted streaming branch: [`crates/router/src/lib.rs:L3287-L3420`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L3287-L3420)
- Passthrough streaming branch: [`crates/router/src/lib.rs:L2606-L2785`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2606-L2785)

**Confidence: HIGH for shared control flow; DYNAMIC for concrete parser.**
