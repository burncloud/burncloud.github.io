---
title: "GET /api/v1/usage/models"
slug: /http-api/ai-api-data-plane/get-api-v1-usage-models
hide_table_of_contents: true
---

# GET /api/v1/usage/models

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → GET /api/v1/usage/models`

> **中文解释：** 与 usage 接口共用鉴权链，但数据库聚合维度改为 model，返回每个模型的请求量、token 与 cost。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 发起者
│    └─ User / SDK / Browser / Operator
│
├─ 入口
│    └─ GET /api/v1/usage/models
│
▼
FILE: crates/server/src/lib.rs
│
├─ axum::serve(listener, app)
├─ 全局 Middleware
│    ├─ CORS
│    ├─ TraceLayer
│    └─ x-request-id
│
├─ 顶层未命中 → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ 显式 route → usage_models_handler()
├─ extract_token_user()
│    ├─ DECISION: Authorization Bearer 存在?
│    │    ├─ NO  → HTTP 401
│    │    └─ YES → validate token
│    ├─ validate_token_and_get_info
│    ├─ fallback: validate_token_detailed
│    └─ fallback: JWT decode
│
├─ DECISION: token/user 可解析?
│    ├─ NO  → 401 / 503
│    └─ YES → user_id
│
├─ DB CALL: get_usage_stats_by_model(user_id, "month")
├─ DECISION: query OK?
│    ├─ NO  → HTTP 500
│    └─ YES → serialize usage JSON
│
└─ HTTP 200 application/json

▼
END
     └─ 返回当前 token holder 的月度用量
```


## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "period": "month",
  "models": [
    {
      "model": "gpt-5.4",
      "requests": 8021,
      "total_tokens": 16600420,
      "cost": 81.24
    },
    {
      "model": "claude-sonnet-4-5",
      "requests": 4821,
      "total_tokens": 8732980,
      "cost": 45.43
    }
  ]
}
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/router/src/lib.rs` |
| 3 | `crates/database/crates/router/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
