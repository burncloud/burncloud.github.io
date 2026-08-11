---
title: "GET /console/internal/metrics"
slug: /http-api/admin-internal/get-console-internal-metrics
hide_table_of_contents: true
---

# GET /console/internal/metrics

**树路径：** `BurnCloud → HTTP / API → Admin / Internal → GET /console/internal/metrics`

> **中文解释：** 返回 Router 内部 metrics。
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
│    └─ GET /console/internal/metrics
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
├─ explicit internal route → metrics_handler()
├─ IMPORTANT: current internal_app itself has no JWT middleware
├─ Execute internal runtime operation
├─ DECISION: operation succeeds?
│    ├─ NO  → route-specific 5xx/timeout response
│    └─ YES → JSON response
│
▼
END
```


## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "requests_total": 3482211,
  "requests_inflight": 37,
  "upstream_failures_total": 14203,
  "rate_limited_total": 8231,
  "channels_healthy": 19
}
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/router/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
