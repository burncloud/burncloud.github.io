---
title: "GET /console/api/{*path} → protected 404 catch-all"
slug: /http-api/admin-internal/get-console-api-path-protected-404-catch-all
hide_table_of_contents: true
---

# GET /console/api/&#123;*path&#125; → protected 404 catch-all

**树路径：** `BurnCloud → HTTP / API → Admin / Internal → GET /console/api/{*path} → protected 404 catch-all`

&gt; **中文解释：** Management API 未匹配的 /console/api/* 在 JWT 后进入 404，避免被 LiveView 返回 HTML。
&gt;
&gt; **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 发起者
│    └─ User / SDK / Browser / Operator
│
├─ 入口
│    └─ GET /console/api/{*path} → protected 404 catch-all
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
├─ api::routes() protected router
├─ auth_middleware()
├─ DECISION: JWT valid?
│    ├─ NO  → HTTP 401
│    └─ YES → continue
├─ No concrete /console/api/* route matched
└─ api_not_found() → HTTP 404 "API endpoint not found"

▼
END
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/server/src/api/mod.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
