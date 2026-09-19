---
title: "POST /api/auth/login"
slug: /http-api/authentication/post-api-auth-login
hide_table_of_contents: true
---

# POST /api/auth/login

**树路径：** `BurnCloud → HTTP / API → Authentication → POST /api/auth/login`

> **中文解释：** 校验用户名密码；成功后返回 JWT 与角色。 核心调用：login_user → get_user_roles。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方输入
│    ├─ Entry: POST /api/auth/login
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
├─ public_routes() matches POST /api/auth/login
├─ login()
├─ Axum Json/State extraction
└─ CALL UserService::login_user → get_user_roles
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ UserService operation: login_user → get_user_roles
├─ password hash/verify, JWT, OAuth/config logic as applicable
└─ persistence calls: UserDatabase::get_user_by_username / get_user_roles
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
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: crates/server/src/api/auth.rs
│    │    ├─ login()
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → err() @ crates/server/src/api/response.rs
│    └─ FILE: crates/server/src/api/response.rs
│    │    ├─ ok()
│    │    ├─ err()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
POST /api/auth/login HTTP/1.1
Host: api.burncloud.example
Content-Type: application/json

{"username":"demo_user","password":"Example-Password-123!"}
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
| 6 | `crates/server/src/api/response.rs` | `err(), ok()` | 由 login() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
