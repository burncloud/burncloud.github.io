---
title: "Query API Usage"
slug: /api-requests/usage/
type: runtime-flow
flow_id: user.api.usage
truth: STATIC_CONFIRMED
parent_flow: user.api
entry_points:
  - "GET /api/v1/usage"
  - "GET /api/v1/usage/models"
---

# Query API Usage

← [API 请求](/#/api-requests/)

## What happens here?

两个 usage endpoint 都是显式数据面 GET routes。它们先通过共享 `extract_token_user()` 从 Bearer token 恢复 user id：新 token/user lookup → legacy token → JWT fallback；认证失败可在 DB 查询前退出。认证成功后，overall path 从 `router_logs` 聚合当前用户最近一个月的 request/token/cost；models path 使用同一时间窗口按 model 分组。

## ICFG

```mermaid
flowchart TD
    E{"用户请求哪一个 usage endpoint?"}
    U["GET /api/v1/usage<br/>usage_handler()"]
    M["GET /api/v1/usage/models<br/>usage_models_handler()"]
    AUTH["恢复 authenticated user_id<br/>extract_token_user()"]
    AOK{"认证成功?"}
    EARLY["No → 返回认证 / DB-validation error"]
    DB1["聚合最近 month 的 router_logs<br/>get_usage_stats()"]
    DB2["按 model 聚合最近 month 的 router_logs<br/>get_usage_stats_by_model()"]
    Q1{"DB aggregate Ok?"}
    Q2{"DB aggregate Ok?"}
    R1["Return 200 overall usage JSON"]
    R2["Return 200 model usage JSON"]
    E500["Return 500 json_error_body(error)"]
    E -->|overall| U --> AUTH
    E -->|models| M --> AUTH
    AUTH --> AOK
    AOK -->|No| EARLY
    AOK -->|Yes, overall| DB1 --> Q1
    AOK -->|Yes, models| DB2 --> Q2
    Q1 -->|Yes| R1
    Q1 -->|No| E500
    Q2 -->|Yes| R2
    Q2 -->|No| E500
    click AUTH "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1084" "Open extract_token_user" _blank
    click DB1 "https://github.com/burncloud/burncloud/blob/main/crates/database/crates/router/src/log.rs#L285" "Open overall aggregation" _blank
    click DB2 "https://github.com/burncloud/burncloud/blob/main/crates/database/crates/router/src/log.rs#L343" "Open model aggregation" _blank
```

## State / Side Effects

- **DB READ:** token/user tables during auth; `router_logs` during usage aggregation.
- No usage state mutation is visible in these handlers.

## Source Evidence

- Route registration: [`crates/router/src/lib.rs:L954-L960`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L954-L960)
- Token/JWT recovery helper: [`crates/router/src/lib.rs:L1082-L1136`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1082-L1136)
- Usage handlers: [`crates/router/src/lib.rs:L1138-L1201`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1138-L1201)
- Overall SQL aggregate: [`crates/database/crates/router/src/log.rs:L283-L339`](https://github.com/burncloud/burncloud/blob/main/crates/database/crates/router/src/log.rs#L283-L339)
- By-model SQL aggregate: [`crates/database/crates/router/src/log.rs:L341-L390`](https://github.com/burncloud/burncloud/blob/main/crates/database/crates/router/src/log.rs#L341-L390)

**Confidence: HIGH — STATIC CONFIRMED.**
