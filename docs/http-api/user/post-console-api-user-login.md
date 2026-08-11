---
title: "POST /console/api/user/login"
slug: /http-api/user/post-console-api-user-login
hide_table_of_contents: true
---

# POST /console/api/user/login

**树路径：** `BurnCloud → HTTP / API → User → POST /console/api/user/login`

> **中文解释：** 当前位于 protected router；成功登录后还把 username/token 写入 ~/.burncloud/client_state.json。 核心调用：UserService::login_user。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方输入
│    ├─ Entry: POST /console/api/user/login
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
├─ routes() matches POST /console/api/user/login
├─ login()
├─ Path/Query/Json/Claims extraction
└─ CALL UserService::login_user(...)
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ UserService::login_user()
├─ password/JWT/balance/recharge logic as applicable
└─ DB calls: UserDatabase::get_user_by_username
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
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: crates/server/src/api/auth.rs
│    │    ├─ auth_middleware()
│    │    │    └─ CALL → verify_jwt() @ crates/server/src/api/auth.rs
│    │    ├─ verify_jwt()
│    │    │    └─ CALL → get_jwt_secret() @ crates/server/src/api/auth.rs
│    │    ├─ get_jwt_secret()
│    │    │    └─ CALL → jwt_secret() @ crates/common/src/constants.rs
│    ├─ FILE: crates/server/src/api/user.rs
│    │    ├─ login()
│    │    │    └─ CALL → persist_client_state() @ crates/server/src/api/user.rs
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → err() @ crates/server/src/api/response.rs
│    │    ├─ persist_client_state()
│    ├─ FILE: crates/service/crates/user/src/lib.rs
│    │    ├─ UserService::login_user()
│    │    │    └─ CALL → UserDatabase::get_user_by_username() @ crates/database/crates/user/src/lib.rs
│    │    │    └─ CALL → BundleVerifier::verify() @ crates/installer/src/bundle.rs
│    ├─ FILE: crates/server/src/api/response.rs
│    │    ├─ ok()
│    │    ├─ err()
│    ├─ FILE: crates/database/crates/user/src/lib.rs
│    │    ├─ UserDatabase::get_user_by_username()
│    ├─ FILE: crates/installer/src/bundle.rs
│    │    ├─ BundleVerifier::verify()
│    │    │    └─ CALL → BundleManifest::load() @ crates/installer/src/bundle.rs
│    │    │    └─ CALL → Platform::current() @ crates/installer/src/platform.rs
│    │    │    └─ CALL → BundleVerifier::verify_checksums() @ crates/installer/src/bundle.rs
│    │    ├─ BundleManifest::load()
│    │    ├─ BundleVerifier::verify_checksums()
│    ├─ FILE: crates/common/src/constants.rs
│    │    ├─ jwt_secret()
│    └─ FILE: crates/installer/src/platform.rs
│    │    ├─ Platform::current()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
POST /console/api/user/login HTTP/1.1
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
    "token": "eyJhbGciOi...example",
    "username": "demo_user"
  }
}
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | Public/Protected Management route composition | ROUTE composition |
| 3 | `crates/server/src/api/auth.rs` | `auth_middleware(), verify_jwt(), public_routes()` | JWT middleware 与 public authentication routes | READ Authorization / Claims |
| 4 | `crates/server/src/api/user.rs` | `login()` | User Handler / Claims / DTO | READ/WRITE request |
| 5 | `crates/service/crates/user/src/lib.rs` | `UserService::*` | User/auth business service | SERVICE |
| 6 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::*` | User/role/recharge persistence | READ/WRITE user state |
| 7 | `crates/server/src/api/response.rs` | `err(), ok()` | 由 login() 直接调用 | CALL / runtime-specific |
| 8 | `crates/installer/src/bundle.rs` | `BundleManifest::load(), BundleVerifier::verify(), BundleVerifier::verify_checksums()` | 由 BundleVerifier::verify() 直接调用；由 UserService::login_user() 直接调用 | CALL / runtime-specific |
| 9 | `crates/common/src/constants.rs` | `jwt_secret()` | 由 get_jwt_secret() 直接调用 | CALL / runtime-specific |
| 10 | `crates/installer/src/platform.rs` | `Platform::current()` | 由 BundleVerifier::verify() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
