---
title: "Query Models"
slug: /api-requests/models/
type: runtime-flow
flow_id: user.api.models
truth: STATIC_CONFIRMED
parent_flow: user.api
entry_points:
  - "GET /v1/models"
---

# Query Models

← [API 请求](/#/api-requests/)

## What happens here?

`GET /v1/models` 是数据面 Router 的显式 route，不进入 `proxy_handler()`。`models_handler()` 调用 `ChannelAbilityModel::list_distinct_models()`，从 `channel_abilities` 查询 `enabled = 1` 的 distinct model；查询成功时把每个 model 转成 OpenAI-style model object。需要注意：当前 handler 对 DB 查询失败使用 `if let Ok(...)`，因此失败不会返回 5xx，而是继续返回空 `data` 列表。

## ICFG

```mermaid
flowchart TD
    E["用户查询可用模型<br/>GET /v1/models"]
    H["进入显式 handler<br/>models_handler()"]
    DB["查询 enabled ability 中的 distinct model<br/>ChannelAbilityModel::list_distinct_models()"]
    Q{"DB query Ok?"}
    LOOP["逐 model 构造 OpenAI-style model object"]
    EMPTY["Err → model_entries 保持为空"]
    JSON["构造 {object:list, data:model_entries}"]
    SER{"JSON serialization Ok?"}
    FALL["序列化失败 → fallback 空 list JSON"]
    OUT["Return 200 application/json"]
    E --> H --> DB --> Q
    Q -->|Yes| LOOP --> JSON
    Q -->|No| EMPTY --> JSON
    JSON --> SER
    SER -->|Yes| OUT
    SER -->|No| FALL --> OUT
    click H "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1041" "Open models_handler" _blank
    click DB "https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_ability.rs#L120" "Open DB query" _blank
```

## State / Side Effects

- **DB READ:** `channel_abilities.model` where `enabled = 1`.
- No DB/cache mutation is visible on this path.

## Source Evidence

- Route registration: [`crates/router/src/lib.rs:L954-L960`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L954-L960)
- Handler: [`crates/router/src/lib.rs:L1041-L1080`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1041-L1080)
- DB query: [`crates/database/crates/channel/src/channel_ability.rs:L116-L128`](https://github.com/burncloud/burncloud/blob/main/crates/database/crates/channel/src/channel_ability.rs#L116-L128)

**Confidence: HIGH — STATIC CONFIRMED.**
