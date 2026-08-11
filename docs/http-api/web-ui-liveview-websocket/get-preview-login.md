---
title: "GET /preview/login"
slug: /http-api/web-ui-liveview-websocket/get-preview-login
hide_table_of_contents: true
---

# GET /preview/login

**树路径：** `BurnCloud → HTTP / API → Web UI / LiveView / WebSocket → GET /preview/login`

> **中文解释：** 当 enable_liveview = true 时由 LiveView Router 命中，返回页面 shell/静态响应；后续交互通过 Dioxus LiveView 与 WebSocket。
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
│    └─ GET /preview/login
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
├─ DECISION: enable_liveview == true?
│    ├─ NO  → route may fall to data-plane fallback
│    └─ YES → merged LiveView Router
│
▼
FILE: crates/client/src/lib.rs
│
├─ Match shell/static route
├─ Return Dioxus LiveView HTML shell / favicon response
│
▼
FILE: crates/client/src/app.rs
│
├─ Browser loads Dioxus route tree
└─ Subsequent interactive state is driven by LiveView/WebSocket

▼
END
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

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/client/src/lib.rs` |
| 3 | `crates/client/src/app.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
