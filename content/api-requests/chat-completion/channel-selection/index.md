---
title: "Channel Selection — Overview"
slug: /api-requests/chat-completion/channel-selection/
type: runtime-flow
flow_id: user.api.chat.channel
truth: STATIC_CONFIRMED
parent_flow: user.api.chat
entry_points:
  - "proxy_logic"
  - "ModelRouter::route_with_scheduler"
drill_down:
  - "user.api.chat.channel.candidates"
  - "user.api.chat.channel.filter"
  - "user.api.chat.channel.rank"
---

# Channel Selection — Overview

← [Chat Completion](/api-requests/chat-completion/)

## What happens here?

当请求可以解析出 model 时，`proxy_logic()` 读取 group 对应 scheduler policy、解析用户 traffic color 和 OrderType，然后调用 `ModelRouter::route_with_scheduler()`。后者从 DB 候选开始，依次做可用性、价格/OrderType、Affinity 与 Scheduler 排名，最多返回 5 个 failover 候选。

## ICFG — Selection Pipeline

```mermaid
flowchart TD
    P["proxy_logic() 得到 model + user_group"]
    POLICY["读取 group scheduler policy"]
    COLOR["解析用户 TrafficColor<br/>UserService::resolve_traffic_class()"]
    ORDER["从 token row 建立 OrderType<br/>OrderType::from_db_row()"]
    R["进入 ModelRouter::route_with_scheduler()"]
    C["读取最高优先级候选<br/>get_candidates()"]
    A["过滤当前不可用 Channel"]
    O["按 OrderType / 价格约束过滤"]
    F["Affinity cache / HRW 选择偏好"]
    S["CombinedScheduler 或 passthrough ranking"]
    H["Affinity 命中则提升到 rank-0"]
    T["take(5) → 有序 failover candidates"]
    P --> POLICY --> COLOR --> ORDER --> R --> C --> A --> O --> F --> S --> H --> T
    click C "/api-requests/chat-completion/channel-selection/candidate-loading/" "Candidate Loading" _self
    click A "/api-requests/chat-completion/channel-selection/availability-order-filter/" "Availability / OrderType" _self
    click F "/api-requests/chat-completion/channel-selection/affinity-ranking/" "Affinity / Ranking" _self
    click R "https://github.com/burncloud/burncloud/blob/main/crates/router/src/model_router.rs#L220" "Open route_with_scheduler" _blank
```

## Decisions

- No candidate ability → returns empty vector; caller later returns no matching channel.
- All unavailable or OrderType removes all candidates → `NoAvailableChannelsError` and caller builds `503`.
- Affinity never removes failover alternatives; it only hoists a candidate before top-5.

## Continue Drilling Down

- → [Candidate Loading](/api-requests/chat-completion/channel-selection/candidate-loading/)
- → [Availability + OrderType Filtering](/api-requests/chat-completion/channel-selection/availability-order-filter/)
- → [Affinity + Ranking](/api-requests/chat-completion/channel-selection/affinity-ranking/)

## Source Evidence

- [`crates/router/src/lib.rs:L2077-L2264`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2077-L2264)
- [`crates/router/src/model_router.rs:L202-L369`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/model_router.rs#L202-L369)

**Confidence: HIGH — STATIC CONFIRMED**
