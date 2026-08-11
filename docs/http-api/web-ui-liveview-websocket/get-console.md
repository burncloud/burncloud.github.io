---
title: "GET /console"
slug: /http-api/web-ui-liveview-websocket/get-console
hide_table_of_contents: true
---

# GET /console

**树路径：** `BurnCloud → HTTP / API → Web UI / LiveView / WebSocket → GET /console`

> **中文解释：** 当 enable_liveview = true 时由 LiveView Router 命中，返回页面 shell/静态响应；后续交互通过 Dioxus LiveView 与 WebSocket。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /console
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
│         ├─ YES → merged LiveView/static route candidate
│         └─ NO → other route/fallback
│
├─ LiveView feature gate
│    └─ DECISION: enable_liveview == true?
│         ├─ NO → LiveView route unavailable; routing continues/falls back
│         └─ YES → match LiveView Router
│
▼
FILE: crates/client/src/lib.rs
│
├─ HTTP shell/static handler
│    ├─ route shell / preview / favicon according to path
│    └─ DECISION: requested LiveView/static route recognized?
│         ├─ NO → route miss
│         └─ YES → construct HTML/static response
│
▼
FILE: crates/client/src/app.rs
│
├─ Client route model
│    ├─ Dioxus Route enum represents browser-side view
│    ├─ App contexts: auth/theme/i18n/toast
│    └─ page-specific component selected after client session establishes
│
├─ Follow-up interactive transport
│    ├─ initial HTTP response delivers shell
│    └─ interactive events move to /ws LiveView session
│
▼
END
     └─ Browser receives HTML/static shell; UI lifecycle continues separately
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /console HTTP/1.1
Host: api.burncloud.example
Accept: text/html
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!doctype html>
<html lang="zh-CN">
  <head><meta charset="utf-8"><title>BurnCloud</title></head>
  <body><div id="main">Dioxus LiveView shell</div></body>
</html>
```



## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 Server、Router 合并、Middleware、fallback 入口 | READ runtime composition |
| 2 | `crates/client/src/lib.rs` | `见上方 E2E 对应函数` | 该页面现有静态调用链中的源码文件 | READ/WRITE depends on entry |
| 3 | `crates/client/src/app.rs` | `见上方 E2E 对应函数` | 该页面现有静态调用链中的源码文件 | READ/WRITE depends on entry |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
