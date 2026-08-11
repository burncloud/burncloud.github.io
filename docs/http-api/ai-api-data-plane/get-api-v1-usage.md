---
title: "GET /api/v1/usage"
slug: /http-api/ai-api-data-plane/get-api-v1-usage
hide_table_of_contents: true
---

# GET /api/v1/usage

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → GET /api/v1/usage`

> **中文解释：** 提取 Bearer Token，按新 token 表 → legacy token → JWT 的顺序识别用户，然后查询当月总请求、token 与成本。
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
│    └─ GET /api/v1/usage
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
├─ 显式 route → usage_handler()
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
├─ DB CALL: get_usage_stats(user_id, "month")
├─ DECISION: query OK?
│    ├─ NO  → HTTP 500
│    └─ YES → serialize usage JSON
│
└─ HTTP 200 application/json

▼
END
     └─ 返回当前 token holder 的月度用量
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/router/src/lib.rs` |
| 3 | `crates/database/crates/router/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
