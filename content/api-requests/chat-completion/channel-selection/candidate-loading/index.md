---
title: "Candidate Loading"
slug: /api-requests/chat-completion/channel-selection/candidate-loading/
type: runtime-flow
flow_id: user.api.chat.channel.candidates
truth: STATIC_CONFIRMED
parent_flow: user.api.chat.channel
entry_points:
  - "ModelRouter::get_candidates"
drill_down:
  - "user.api.chat.channel.filter"
---

# Candidate Loading

← [Channel Selection](/api-requests/chat-completion/channel-selection/) · ← [Chat Completion](/api-requests/chat-completion/)

## What happens here?

`get_candidates(group, model)` 不直接扫描所有 Channel。它先从 `channel_abilities` 找当前 group+model 的**最高 priority**，再读取该 priority 下所有 enabled channel IDs/weights，最后批量从 `channel_providers` 取完整 Channel 配置并恢复 weight。

## ICFG

```mermaid
flowchart TD
    E["进入 get_candidates(group, model)"]
    DB["获取 DB connection / dialect"]
    Q1["SELECT highest priority<br/>FROM channel_abilities"]
    P{"找到 priority?"}
    EMPTY["Return [] — 当前 group/model 无 ability"]
    Q2["SELECT channel_id, weight<br/>同 priority + enabled"]
    CE{"candidate IDs empty?"}
    Q3["SELECT channel details<br/>FROM channel_providers WHERE id IN (...)"]
    MAP["按 channel_id 恢复 ability weight"]
    RET["Return Vec<(Channel, weight)>"]
    E --> DB --> Q1 --> P
    P -->|No| EMPTY
    P -->|Yes| Q2 --> CE
    CE -->|Yes| EMPTY
    CE -->|No| Q3 --> MAP --> RET
    click E "https://github.com/burncloud/burncloud/blob/main/crates/router/src/model_router.rs#L84" "Open get_candidates" _blank
```

## State / Side Effects

- **DB READ:** `channel_abilities`, `channel_providers`.
- No DB writes in this function.

## Continue Drilling Down

→ [Availability + OrderType Filtering](/api-requests/chat-completion/channel-selection/availability-order-filter/)

## Source Evidence

- [`crates/router/src/model_router.rs:L84-L200`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/model_router.rs#L84-L200)

**Confidence: HIGH — STATIC CONFIRMED**
