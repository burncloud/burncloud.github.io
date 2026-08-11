---
title: "POST /console/api/user/register"
slug: /http-api/user/post-console-api-user-register
hide_table_of_contents: true
---

# POST /console/api/user/register

**树路径：** `BurnCloud → HTTP / API → User → POST /console/api/user/register`

> **中文解释：** 注意：虽然名字像注册接口，但它位于 protected router，当前先经过 JWT middleware。 核心调用：UserService::register_user。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方输入
│    ├─ Entry: POST /console/api/user/register
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
├─ DECISION: protected User route 命中?
│    ├─ NO → other route
│    └─ YES → protected_routes
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ merge(user::routes())
└─ auth_middleware wraps protected router
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ auth_middleware() → verify_jwt()
└─ DECISION: JWT valid?
     ├─ NO → HTTP 401 → END
     └─ YES → Claims inserted
│
▼
FILE: crates/server/src/api/user.rs
│
├─ routes() matches POST /console/api/user/register
├─ register()
├─ Path/Query/Json/Claims extraction
└─ CALL UserService::register_user(...)
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ UserService::register_user()
├─ password/JWT/balance/recharge logic as applicable
└─ DB calls: UserDatabase::get_user_by_username / count_users / create_user / assign_role
│
▼
FILE: crates/database/crates/user/src/lib.rs
│
├─ UserDatabase read/write
├─ db.get_connection() / SQL execution / row mapping
└─ DECISION: persistence operation successful?
     ├─ NO → DatabaseError → UserServiceError
     └─ YES → user/balance/roles/recharge result
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
└─ return domain result
│
▼
FILE: crates/server/src/api/user.rs
│
├─ map domain result to API response
└─ return HTTP JSON
│
▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
POST /console/api/user/register HTTP/1.1
Host: api.burncloud.example
Authorization: Bearer eyJhbGciOi...admin-jwt
Accept: application/json
Content-Type: application/json

{"example":"request body"}
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "id": 10001,
    "username": "demo_user",
    "roles": [
      "user"
    ]
  }
}
```



## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | Public/Protected Management route composition | ROUTE composition |
| 3 | `crates/server/src/api/auth.rs` | `auth_middleware(), verify_jwt(), public_routes()` | JWT middleware 与 public authentication routes | READ Authorization / Claims |
| 4 | `crates/server/src/api/user.rs` | `register()` | User Handler / Claims / DTO | READ/WRITE request |
| 5 | `crates/service/crates/user/src/lib.rs` | `UserService::*` | User/auth business service | SERVICE |
| 6 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::*` | User/role/recharge persistence | READ/WRITE user state |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
