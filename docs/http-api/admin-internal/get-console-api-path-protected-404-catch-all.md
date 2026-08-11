---
title: "GET /console/api/{*path} → protected 404 catch-all"
slug: /http-api/admin-internal/get-console-api-path-protected-404-catch-all
hide_table_of_contents: true
---

# GET /console/api/&#123;*path&#125; → protected 404 catch-all

**树路径：** `BurnCloud → HTTP / API → Admin / Internal → GET /console/api/{*path} → protected 404 catch-all`

> **中文解释：** Management API 未匹配的 /console/api/* 在 JWT 后进入 404，避免被 LiveView 返回 HTML。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /console/api/{*path} → protected 404 catch-all
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
│         ├─ YES → Management API protected router
│         └─ NO → other router
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ JWT middleware executes before protected catch-all
│    ├─ DECISION: Bearer JWT valid?
│    │    ├─ NO → HTTP 401 → END
│    │    └─ YES → Claims inserted
│    └─ continue route matching
│
├─ Concrete /console/api/* routes checked
│    └─ DECISION: any concrete protected route matched?
│         ├─ YES → that handler executes
│         └─ NO → api_not_found()
│
├─ Catch-all purpose
│    ├─ prevents unknown API path from being served as LiveView HTML
│    └─ returns explicit API 404
│
▼
END
     └─ HTTP 404 "API endpoint not found"
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /console/api/unknown → protected 404 catch-all HTTP/1.1
Host: api.burncloud.example
Authorization: Bearer eyJhbGciOi...admin-jwt
Accept: application/json
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "API endpoint not found"
}
```


## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 Server、Router 合并、Middleware、fallback 入口 | READ runtime composition |
| 2 | `crates/server/src/api/mod.rs` | `见上方 E2E 对应函数` | 该页面现有静态调用链中的源码文件 | READ/WRITE depends on entry |

> 这个索引只列入当前执行链中有源码依据的文件；类型定义文件但不执行逻辑的，不为了凑数量加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
