---
title: "PUT /console/api/channel"
slug: /http-api/channel-management/put-console-api-channel
hide_table_of_contents: true
---

# PUT /console/api/channel

**树路径：** `BurnCloud → HTTP / API → Channel Management → PUT /console/api/channel`

> **中文解释：** 管理员更新 Channel；id = 0 时直接拒绝。 核心调用：ChannelService::update。
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
│    └─ PUT /console/api/channel
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
├─ Route match → update_channel()
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


## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "id": 12,
    "name": "openai-primary",
    "channel_type": "openai",
    "base_url": "https://api.openai.com",
    "status": 1,
    "priority": 100,
    "weight": 120
  }
}
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/server/src/api/mod.rs` |
| 3 | `crates/server/src/api/auth.rs` |
| 4 | `crates/server/src/api/channel.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
