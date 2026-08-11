---
title: "GET /console/api/tokens/{token}"
slug: /http-api/token/get-console-api-tokens-token
hide_table_of_contents: true
---

# GET /console/api/tokens/&#123;token&#125;

**树路径：** `BurnCloud → HTTP / API → Token → GET /console/api/tokens/{token}`

> **中文解释：** 按 token 查询并返回 token 详情；不存在则报错。 核心调用：TokenService::validate。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方输入
│    ├─ Entry: GET /console/api/tokens/{token}
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
├─ DECISION: Management API route 命中?
│    ├─ NO → other route
│    └─ YES → protected_routes
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ merge(token::routes())
└─ auth_middleware wraps protected router
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ auth_middleware() → verify_jwt()
└─ DECISION: JWT valid?
     ├─ NO → HTTP 401 → END
     └─ YES → Claims → next
│
▼
FILE: crates/server/src/api/token.rs
│
├─ routes() matches GET /console/api/tokens/{token}
├─ get_token()
├─ parse Path / Query / Json according to method
├─ validate token-specific fields / rotation / whitelist parameters
└─ CALL TokenService::validate(...)
│
▼
FILE: crates/service/crates/token/src/lib.rs
│
├─ TokenService::validate()
└─ CALL RouterTokenModel::validate(...)
│
▼
FILE: crates/database/crates/router/src/token.rs
│
├─ RouterTokenModel::validate()
├─ DB read/write + token state/rotation/quota fields
└─ DECISION: DB/token operation successful?
     ├─ NO → DatabaseError / not found / validation result
     └─ YES → RouterToken / bool / TokenRotationResult / ()
│
▼
FILE: crates/service/crates/token/src/lib.rs
│
└─ return Result to API handler
│
▼
FILE: crates/server/src/api/token.rs
│
├─ map result to ok(...) / err(...)
└─ return HTTP JSON response
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
│    ├─ FILE: crates/server/src/api/token.rs
│    │    ├─ get_token()
│    │    │    └─ CALL → TokenService::validate() @ crates/service/crates/token/src/lib.rs
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → err() @ crates/server/src/api/response.rs
│    ├─ FILE: crates/service/crates/token/src/lib.rs
│    │    ├─ TokenService::validate()
│    ├─ FILE: crates/database/crates/router/src/token.rs
│    │    ├─ RouterTokenModel::validate()
│    │    │    └─ CALL → RouterTokenModel::current_timestamp() @ crates/database/crates/router/src/token.rs
│    │    │    └─ CALL → adapt_sql() @ crates/database/src/placeholder.rs
│    │    ├─ RouterTokenModel::current_timestamp()
│    ├─ FILE: crates/server/src/api/response.rs
│    │    ├─ ok()
│    │    ├─ err()
│    ├─ FILE: crates/database/src/placeholder.rs
│    │    ├─ adapt_sql()
│    └─ FILE: crates/common/src/constants.rs
│    │    ├─ jwt_secret()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /console/api/tokens/bc_live_7d4e...example HTTP/1.1
Host: api.burncloud.example
Authorization: Bearer eyJhbGciOi...admin-jwt
Accept: application/json
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "token": "bc_live_7d4e...example",
    "user_id": 10001,
    "name": "production",
    "status": 1,
    "quota": 100000000,
    "ip_whitelist": [
      "203.0.113.10"
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
| 4 | `crates/server/src/api/token.rs` | `get_token()` | Token Handler / request validation / response mapping | READ/WRITE token request |
| 5 | `crates/service/crates/token/src/lib.rs` | `TokenService::*` | Token service boundary | SERVICE |
| 6 | `crates/database/crates/router/src/token.rs` | `RouterTokenModel::*` | Router token/quota/key persistence | READ/WRITE router token state |
| 7 | `crates/server/src/api/response.rs` | `err(), ok()` | 由 get_token() 直接调用 | CALL / runtime-specific |
| 8 | `crates/database/src/placeholder.rs` | `adapt_sql()` | 由 RouterTokenModel::validate() 直接调用 | CALL / runtime-specific |
| 9 | `crates/common/src/constants.rs` | `jwt_secret()` | 由 get_jwt_secret() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
