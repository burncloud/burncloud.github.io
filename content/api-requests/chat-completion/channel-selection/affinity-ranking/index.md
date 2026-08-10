---
title: "Affinity & Ranking"
slug: /api-requests/chat-completion/channel-selection/affinity-ranking/
type: runtime-flow
flow_id: user.api.chat.channel.rank
truth: STATIC_CONFIRMED
parent_flow: user.api.chat.channel
entry_points:
  - "route_with_scheduler L3/L4"
drill_down:
  - "user.api.chat.provider"
---

# Affinity & Ranking

← [Channel Selection](/api-requests/chat-completion/channel-selection/)

## What happens here?

过滤后的候选先尝试获取 affinity preference：有 cache hit 就使用；cache miss 时可用 HRW 依据 health score 产生 pick。候选仍然会被 scheduler 排名，最后如果 affinity pick 仍在 ranked 集合中，把它提升到首位并刷新 cache，然后只保留 top-5。

## ICFG

```mermaid
flowchart TD
    E["收到 filtered candidates"]
    KEY{"存在 affinity_cache + affinity_key?"}
    LOOK["cache.lookup(key, model)"]
    HIT{"cache hit?"}
    HRW["cache miss → affinity::pick_hrw(...health_score)"]
    PICK["得到 optional affinity_pick"]
    SK{"配置 Combined scheduler?"}
    CTX["build_context() + CombinedScheduler rank"]
    PASS["rank_passthrough(filtered)"]
    POS{"affinity_pick 在 ranked 中?"}
    HOIST["移到 rank-0 + cache.insert()"]
    TOP["take(5)"]
    DEC["RoutingDecision = AffinityHit 或 ScorerPicked"]
    RET["Return ranked channels + decision"]
    E --> KEY
    KEY -->|No| PICK
    KEY -->|Yes| LOOK --> HIT
    HIT -->|Yes| PICK
    HIT -->|No| HRW --> PICK
    PICK --> SK
    SK -->|Yes| CTX --> POS
    SK -->|No| PASS --> POS
    POS -->|Yes| HOIST --> TOP
    POS -->|No| TOP
    TOP --> DEC --> RET
    click E "https://github.com/burncloud/burncloud/blob/main/crates/router/src/model_router.rs#L306" "Open affinity/ranking code" _blank
    click RET "/api-requests/chat-completion/provider-execution/" "Continue to Provider Execution" _self
```

## State / Side Effects

- **READ/WRITE local cache:** Affinity cache lookup and refresh.
- Scheduler may read price/health context built from existing services; this page does not assume one concrete scheduler beyond the explicit `Combined` branch or passthrough rank branch.

## Continue Drilling Down

→ [Provider Execution](/api-requests/chat-completion/provider-execution/)

## Source Evidence

- [`crates/router/src/model_router.rs:L306-L368`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/model_router.rs#L306-L368)

**Confidence: HIGH — STATIC CONFIRMED**
