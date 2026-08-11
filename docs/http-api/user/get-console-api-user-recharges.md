---
title: "GET /console/api/user/recharges"
slug: /http-api/user/get-console-api-user-recharges
hide_table_of_contents: true
---

# GET /console/api/user/recharges

**树路径：** `BurnCloud → HTTP / API → User → GET /console/api/user/recharges`

> **中文解释：** 从 JWT Claims.sub 得到当前用户，只查询自己的充值记录。 核心调用：UserService::list_recharges。
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
│    └─ GET /console/api/user/recharges
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
FILE: crates/server/src/api/user.rs
│
├─ Route match → list_recharges()
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
  "data": [
    {
      "id": 9001,
      "amount": 100.0,
      "currency": "USD",
      "created_at": "2026-08-11T14:30:00+08:00"
    }
  ]
}
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/server/src/api/mod.rs` |
| 3 | `crates/server/src/api/auth.rs` |
| 4 | `crates/server/src/api/user.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
