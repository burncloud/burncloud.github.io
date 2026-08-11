---
title: "GET /ws"
slug: /http-api/web-ui-liveview-websocket/get-ws
hide_table_of_contents: true
---

# GET /ws

**树路径：** `BurnCloud → HTTP / API → Web UI / LiveView / WebSocket → GET /ws`

> **中文解释：** HTTP Upgrade 到 WebSocket，承载 LiveView 交互；连接失败/断开由 LiveView/WebSocket 生命周期处理。
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
│    └─ GET /ws
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
├─ enable_liveview == true
├─ LiveView Router matches /ws
├─ HTTP Upgrade → WebSocket
│
▼
FILE: crates/client/src/lib.rs
│
├─ establish LiveView socket session
├─ exchange UI events / render updates
├─ DECISION: connection alive?
│    ├─ YES → continue event loop
│    └─ NO  → close session
│
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
