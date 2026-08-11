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
├─ [PHASE 00] 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /console/internal/metrics
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
├─ [PHASE 01] 统一 HTTP Server
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
├─ [PHASE 02] 顶层 Route 决策
│    └─ DECISION: Unified App 是否已有显式/合并路由命中当前 Method + Path?
│         ├─ YES → merged Router Internal route
│         └─ NO  → continue to other routes/fallback
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 03] Internal route match
│    └─ metrics_handler()
│
├─ [PHASE 04] Authentication boundary
│    ├─ Router internal_app itself is not wrapped by Management JWT middleware
│    └─ network exposure therefore depends on server deployment/binding/firewall
│
├─ [PHASE 05] Runtime-state operation
│    ├─ read/mutate in-memory Router runtime services
│    └─ DECISION: required runtime service/channel available?
│         ├─ NO  → route-specific 5xx/timeout/error response
│         └─ YES → perform operation
│
├─ [PHASE 06] Route-specific state
│    ├─ health: scheduler/circuit/channel/rate-budget snapshot
│    ├─ price sync: force_sync_tx + oneshot result
│    ├─ trip-all: circuit_breaker.trip_all()
│    └─ metrics: Router runtime counters
│
├─ [PHASE 07] Serialize result
│    └─ DECISION: operation/result successful?
│         ├─ NO  → error HTTP response
│         └─ YES → JSON success response
│
▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /console/internal/metrics HTTP/1.1
Host: api.burncloud.example
Accept: application/json
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
