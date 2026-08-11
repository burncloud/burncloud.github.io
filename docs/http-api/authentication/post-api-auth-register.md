---
title: "POST /api/auth/register"
slug: /http-api/authentication/post-api-auth-register
hide_table_of_contents: true
---

# POST /api/auth/register

**树路径：** `BurnCloud → HTTP / API → Authentication → POST /api/auth/register`

> **中文解释：** 注册用户；用户名冲突返回错误，注册成功后生成 JWT。 核心调用：register_user → get_user_roles → generate_token。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方输入
│    ├─ Entry: POST /api/auth/register
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
├─ public_routes() matches POST /api/auth/register
├─ create_user()
├─ Axum Json/State extraction
└─ CALL UserService::register_user → get_user_roles → generate_token
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ UserService operation: register_user → get_user_roles → generate_token
├─ password hash/verify, JWT, OAuth/config logic as applicable
└─ persistence calls: UserDatabase::get_user_by_username / count_users / create_user / assign_role / get_user_roles
│
▼
FILE: crates/database/crates/user/src/lib.rs
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
POST /api/auth/register HTTP/1.1
Host: api.burncloud.example
Content-Type: application/json

{"username":"demo_user","email":"demo@example.com","password":"Example-Password-123!"}
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "token": "eyJhbGciOi...example",
    "user": {
      "id": 10001,
      "username": "demo_user",
      "roles": [
        "user"
      ]
    }
  }
}
```



## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | Public/Protected Management route composition | ROUTE composition |
| 3 | `crates/server/src/api/auth.rs` | `auth_middleware(), verify_jwt(), public_routes()` | JWT middleware 与 public authentication routes | READ Authorization / Claims |
| 4 | `crates/service/crates/user/src/lib.rs` | `UserService::*` | User/auth business service | SERVICE |
| 5 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::*` | User/role/recharge persistence | READ/WRITE user state |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
