---
title: "GET /health"
slug: /http-api/admin-internal/get-health
hide_table_of_contents: true
---

# GET /health

**树路径：** `BurnCloud → HTTP / API → Admin / Internal → GET /health`

> **中文解释：** 顶层 liveness probe，不需要 JWT，直接返回 ok。
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
│    └─ GET /health
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
├─ create_app() has explicit GET /health
├─ DECISION: path == /health?
│    ├─ NO  → continue router matching
│    └─ YES → inline handler returns "ok"
└─ No JWT required

▼
END
```


## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: text/plain; charset=utf-8

ok
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
