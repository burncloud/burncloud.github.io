---
title: "GET /api/v1/usage/models"
slug: /http-api/billing-usage/get-api-v1-usage-models
hide_table_of_contents: true
---

# GET /api/v1/usage/models

**树路径：** `BurnCloud → HTTP / API → Billing / Usage → GET /api/v1/usage/models`

> **中文解释：** 复用 Data Plane usage_models_handler：按 model 聚合月度用量。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /api/v1/usage/models
│    ├─ Input sources
│    │    ├─ Method + URI path
│    │    ├─ Query string（如有）
│    │    ├─ HTTP headers
│    │    └─ Request body（如有）
│    └─ DECISION: TCP/HTTP 请求能否到达 BurnCloud listener?
│         ├─ NO  → 网络层失败；应用代码未执行 → END
│         └─ YES → 进入 Axum
│
▼
FILE: crates/server/src/lib.rs
│
├─ 统一 HTTP Server
│    ├─ start_server() 已在进程启动时完成
│    │    ├─ database 初始化
│    │    ├─ RouterDatabase::init()
│    │    ├─ UserDatabase::init()
│    │    ├─ create_app(...)
│    │    ├─ TcpListener::bind(...)
│    │    └─ axum::serve(listener, app)
│    ├─ 当前请求进入 Unified Axum App
│    └─ 全局 middleware
│         ├─ CORS
│         ├─ TraceLayer
│         ├─ SetRequestIdLayer
│         └─ PropagateRequestIdLayer
│
├─ 顶层 Route 决策
│    └─ DECISION: Unified App 是否已有显式/合并路由命中当前 Method + Path?
│         ├─ YES（其它顶层 route）→ 对应 handler
│         └─ NO → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ Explicit Data Plane route
│    ├─ Route match: GET /api/v1/usage/models
│    └─ handler = usage_models_handler()
│
├─ Credential extraction
│    ├─ read Authorization header
│    ├─ require Bearer token
│    └─ DECISION: Bearer credential present?
│         ├─ NO  → HTTP 401 → END
│         └─ YES → extract_token_user(...)
│
├─ Multi-generation identity resolution
│    ├─ Try new Router token table
│    │    └─ validate_token_and_get_info(...)
│    ├─ DECISION: new token valid?
│    │    ├─ YES → resolve user_id
│    │    └─ NO  → legacy validation
│    ├─ validate_token_detailed(...)
│    ├─ DECISION: legacy token valid?
│    │    ├─ YES → resolve user_id
│    │    └─ NO  → JWT fallback
│    ├─ JWT decode / Claims.sub
│    └─ DECISION: any identity path resolved?
│         ├─ NO  → 401 / service-unavailable error branch → END
│         └─ YES → user_id
│
▼
FILE: crates/database/crates/router/src/lib.rs
│
├─ Usage aggregation query
│    ├─ CALL get_usage_stats_by_model(user_id, "month")
│    ├─ period = month
│    ├─ scope = resolved user_id
│    └─ DECISION: DB aggregation success?
│         ├─ NO  → HTTP 500 → END
│         └─ YES → usage rows / aggregate
│
▼
FILE: crates/router/src/lib.rs
│
▼
FILE: crates/database/crates/router/src/lib.rs
│
├─ get_usage_stats(...) / get_usage_stats_by_model(...)
└─ delegate to router log aggregation
│
▼
FILE: crates/database/crates/router/src/log.rs
│
├─ build period boundary / aggregation SQL
├─ query router_logs for current user
└─ DECISION: SQL succeeds?
     ├─ NO → DatabaseError → handler error response
     └─ YES → UsageStats / Vec<ModelUsageStats>
│
├─ Response mapping
│    ├─ map DB aggregate → API response object
│    ├─ serialize JSON
│    └─ DECISION: serialization/build success?
│         ├─ NO  → internal response error branch
│         └─ YES → HTTP 200 application/json
│
├─ Side effects
│    ├─ no Provider call
│    ├─ no Scheduler
│    ├─ no inference billing deduction
│    └─ read-only usage query
│
▼
END
     └─ Client receives 按模型聚合的月度 usage
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /api/v1/usage/models HTTP/1.1
Host: api.burncloud.example
Authorization: Bearer bc_live_7d4e...example
Accept: application/json
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



## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 Server、Router 合并、Middleware、fallback 入口 | READ runtime composition |
| 2 | `crates/router/src/lib.rs` | `见上方 E2E 对应函数` | 该页面现有静态调用链中的源码文件 | READ/WRITE depends on entry |
| 3 | `crates/database/crates/router/src/lib.rs` | `见上方 E2E 对应函数` | 该页面现有静态调用链中的源码文件 | READ/WRITE depends on entry |
| 4 | `crates/database/crates/router/src/log.rs` | `get_usage_stats() / get_usage_stats_by_model()` | 执行时间范围与 model 聚合 SQL | READ router_logs |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
