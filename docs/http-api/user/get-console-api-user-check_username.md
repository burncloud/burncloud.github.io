---
title: "GET /console/api/user/check_username"
slug: /http-api/user/get-console-api-user-check_username
hide_table_of_contents: true
---

# GET /console/api/user/check_username

**树路径：** `BurnCloud → HTTP / API → User → GET /console/api/user/check_username`

&gt; **中文解释：** 查询用户名是否可用。 核心调用：UserService::is_username_available。
&gt;
&gt; **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 发起者
│    └─ User / SDK / Browser / Operator
│
├─ 入口
│    └─ GET /console/api/user/check_username
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
├─ Route match → check_username()
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
| 4 | `crates/server/src/api/user.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
