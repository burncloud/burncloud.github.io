---
title: "GET /console/api/channel"
slug: /http-api/channel-management/get-console-api-channel
hide_table_of_contents: true
---

# GET /console/api/channel

**树路径：** `BurnCloud → HTTP / API → Channel Management → GET /console/api/channel`

> **中文解释：** 管理员分页列出 Channel；limit 被限制在 1..100，offset 不小于 0。 核心调用：ChannelService::list。
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
│    └─ GET /console/api/channel
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
├─ create_app() → api::routes()
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ protected_routes
├─ auth_middleware()
│    ├─ DECISION: Authorization starts with Bearer?
│    │    ├─ NO  → HTTP 401
│    │    └─ YES → verify_jwt()
│    └─ valid Claims inserted into request extensions
│
▼
FILE: crates/server/src/api/channel.rs
│
├─ Route match → list_channels()
│
├─ DECISION: user has admin role?
│    ├─ NO  → Admin access required
│    └─ YES → continue
│
├─ Execute service/database operation
├─ DECISION: operation successful?
│    ├─ NO  → error response
│    └─ YES → serialize success payload
│
└─ return HTTP response

▼
END
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/server/src/api/mod.rs` |
| 3 | `crates/server/src/api/auth.rs` |
| 4 | `crates/server/src/api/channel.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
