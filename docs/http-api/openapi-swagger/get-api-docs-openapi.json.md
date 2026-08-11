---
title: "GET /api-docs/openapi.json"
slug: /http-api/openapi-swagger/get-api-docs-openapi.json
hide_table_of_contents: true
---

# GET /api-docs/openapi.json

**树路径：** `BurnCloud → HTTP / API → OpenAPI / Swagger → GET /api-docs/openapi.json`

> **中文解释：** 运行时构造 OpenAPI 3.0.3 spec 并以 JSON 返回。
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
│    └─ GET /api-docs/openapi.json
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
├─ api::routes() places openapi::routes() inside protected_routes
├─ auth_middleware()
├─ DECISION: JWT valid?
│    ├─ NO  → HTTP 401
│    └─ YES → openapi_json()
│
▼
FILE: crates/server/src/api/openapi.rs
│
├─ build OpenAPI JSON or Swagger HTML
└─ return response

▼
END
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/server/src/api/mod.rs` |
| 3 | `crates/server/src/api/auth.rs` |
| 4 | `crates/server/src/api/openapi.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
