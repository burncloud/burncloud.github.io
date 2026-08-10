---
title: "Availability & OrderType Filtering"
slug: /api-requests/chat-completion/channel-selection/availability-order-filter/
type: runtime-flow
flow_id: user.api.chat.channel.filter
truth: STATIC_CONFIRMED
parent_flow: user.api.chat.channel
entry_points:
  - "route_with_scheduler L0/L1.5"
drill_down:
  - "user.api.chat.channel.rank"
---

# Availability & OrderType Filtering

← [Channel Selection](/#/api-requests/chat-completion/channel-selection/)

## What happens here?

DB 候选先通过 `ChannelStateTracker::is_available()` 删除当前因 rate limit、auth failure 或 exhaustion 等状态不可用的 Channel。随后代码为剩余 Channel 读取 model/region price（非 USD 时尝试换算），再让 `OrderType::filter_candidates()` 应用预算/价格约束。

## ICFG

```mermaid
flowchart TD
    E["route_with_scheduler() 收到 DB candidates"]
    AV["逐候选检查当前可用性<br/>state_tracker.is_available(channel, model)"]
    AE{"available 为空?"}
    ERR1["Return Err<br/>all channels unavailable"]
    LOOP["逐 available channel 查询 model/region price"]
    FX{"价格币种 != USD?"}
    CONV["尝试 ExchangeRateService::convert()"]
    RAW["保留原 price / USD price"]
    MAP["建立 channel_id → USD nano price_map"]
    OF["OrderType::filter_candidates(available, price_of)"]
    OE{"filtered 为空?"}
    ERR2["Return Err<br/>OrderType filtered all"]
    NEXT["进入 Affinity + Ranking"]
    E --> AV --> AE
    AE -->|Yes| ERR1
    AE -->|No| LOOP --> FX
    FX -->|Yes| CONV --> MAP
    FX -->|No| RAW --> MAP
    MAP --> OF --> OE
    OE -->|Yes| ERR2
    OE -->|No| NEXT
    click E "https://github.com/burncloud/burncloud/blob/main/crates/router/src/model_router.rs#L220" "Open route_with_scheduler" _blank
```

## Decisions

- Availability filtering occurs **before** price / OrderType filtering.
- Currency conversion failure logs a warning and falls back to raw amount; it does not abort selection.

## Continue Drilling Down

→ [Affinity + Ranking](/#/api-requests/chat-completion/channel-selection/affinity-ranking/)

## Source Evidence

- [`crates/router/src/model_router.rs:L248-L304`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/model_router.rs#L248-L304)

**Confidence: HIGH — STATIC CONFIRMED**
