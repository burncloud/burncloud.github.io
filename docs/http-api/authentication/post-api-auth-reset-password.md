---
title: "POST /api/auth/reset-password"
slug: /http-api/authentication/post-api-auth-reset-password
hide_table_of_contents: true
---

# POST /api/auth/reset-password

**树路径：** `BurnCloud → HTTP / API → Authentication → POST /api/auth/reset-password`

> **中文解释：** 校验 reset token 并修改密码；无效/过期 token 返回错误。 核心调用：reset_password。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方输入
│    ├─ Entry: POST /api/auth/reset-password
│    ├─ Method / Path / Query / Headers / Body
│    └─ DECISION: 请求到达 BurnCloud listener?
│         ├─ NO  → 网络层结束，应用代码不执行 → END
│         └─ YES → Axum Unified App
│
▼
FILE: crates/server/src/lib.rs
│
├─ start_server()（启动时）
│    ├─ create_default_database()
│    ├─ RouterDatabase::init()
│    ├─ UserDatabase::init()
│    ├─ create_app()
│    ├─ TcpListener::bind()
│    └─ axum::serve()
│
├─ create_app()
│    ├─ merge(api::routes(...))
│    ├─ merge(internal_app)
│    ├─ optional merge(liveview_router)
│    ├─ fallback_service(router_app)
│    └─ middleware: CORS / Trace / request-id
│
├─ DECISION: public Authentication route 命中?
│    ├─ NO → protected/other route
│    └─ YES → public_routes（不经过 JWT middleware）
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ public_routes = auth::public_routes()
└─ merge public + protected routers
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ public_routes() matches POST /api/auth/reset-password
├─ reset_password()
├─ Axum Json/State extraction
└─ CALL UserService::reset_password
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ UserService operation: reset_password
├─ password hash/verify, JWT, OAuth/config logic as applicable
└─ persistence calls: PasswordResetDatabase + UserDatabase
│
▼
FILE: crates/database/crates/user/src/password_reset.rs
│
├─ user/password-reset state read/write when this path needs persistence
└─ return database result
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ combine DB result with password/JWT/business rules
└─ DECISION: UserService operation successful?
     ├─ NO → typed UserServiceError
     └─ YES → user/token/reset/OAuth result
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ map success/error via ok(...) / err(...)
└─ return HTTP response
│
▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
POST /api/auth/reset-password HTTP/1.1
Host: api.burncloud.example
Content-Type: application/json

{"token":"reset_token_example","new_password":"New-Password-456!"}
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Password reset successfully"
}
```


## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 Server、Router 合并、Middleware、fallback 入口 | READ runtime composition |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | public auth routes outside JWT middleware | ROUTE |
| 3 | `crates/server/src/api/auth.rs` | `reset_password()` | Auth DTO / Handler / response policy | REQUEST/RESPONSE |
| 4 | `crates/service/crates/user/src/lib.rs` | `UserService::reset_password` | password/JWT/OAuth/user business logic | SERVICE |
| 5 | `crates/database/crates/user/src/password_reset.rs` | `PasswordResetDatabase::*` | reset token persistence | READ/WRITE password reset |
| 6 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::*` | user/role persistence when applicable | READ/WRITE users |

> 这个索引只列入当前执行链中有源码依据的文件；类型定义文件但不执行逻辑的，不为了凑数量加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
