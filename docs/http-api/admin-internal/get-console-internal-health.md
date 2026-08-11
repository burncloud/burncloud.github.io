---
title: "GET /console/internal/health"
slug: /http-api/admin-internal/get-console-internal-health
hide_table_of_contents: true
---

# GET /console/internal/health

**树路径：** `BurnCloud → HTTP / API → Admin / Internal → GET /console/internal/health`

&gt; **中文解释：** 返回 scheduler policy、circuit breaker、channel state、rate budget 等运行态健康信息。
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
│    └─ GET /console/internal/health
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
├─ create_app() merges internal_app before LiveView
│
▼
FILE: crates/router/src/lib.rs
│
├─ explicit internal route → health_status_handler()
├─ IMPORTANT: current internal_app itself has no JWT middleware
├─ Execute internal runtime operation
├─ DECISION: operation succeeds?
│    ├─ NO  → route-specific 5xx/timeout response
│    └─ YES → JSON response
│
▼
END
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/router/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
