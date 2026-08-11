---
title: "GET /register"
slug: /http-api/web-ui-liveview-websocket/get-register
hide_table_of_contents: true
---

# GET /register

**树路径：** `BurnCloud → HTTP / API → Web UI / LiveView / WebSocket → GET /register`

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
│    └─ GET /register
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


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/client/src/lib.rs` |
| 3 | `crates/client/src/app.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
