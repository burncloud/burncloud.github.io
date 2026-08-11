---
title: "POST /console/api/tokens/{token}/rotate"
slug: /http-api/token/post-console-api-tokens-token-rotate
hide_table_of_contents: true
---

# POST /console/api/tokens/&#123;token&#125;/rotate

**树路径：** `BurnCloud → HTTP / API → Token → POST /console/api/tokens/{token}/rotate`

> **中文解释：** 轮换 key，可设置旧 key 过渡时间或立即撤销。 核心调用：TokenService::rotate。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方输入
│    ├─ Entry: POST /console/api/tokens/{token}/rotate
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
├─ routes() matches POST /console/api/tokens/{token}/rotate
├─ rotate_token()
├─ parse Path / Query / Json according to method
├─ validate token-specific fields / rotation / whitelist parameters
└─ CALL TokenService::rotate(...)
│
▼
FILE: crates/service/crates/token/src/lib.rs
│
├─ TokenService::rotate()
└─ CALL RouterTokenModel::rotate(...)
│
▼
FILE: crates/database/crates/router/src/token.rs
│
├─ RouterTokenModel::rotate()
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
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → verify_jwt() @ crates/server/src/api/auth.rs
│    │    ├─ verify_jwt()
│    │    │    └─ CALL → get_jwt_secret() @ crates/server/src/api/auth.rs
│    │    ├─ get_jwt_secret()
│    │    │    └─ CALL → jwt_secret() @ crates/common/src/constants.rs
│    ├─ FILE: crates/server/src/api/token.rs
│    │    ├─ rotate_token()
│    │    │    └─ CALL → TokenService::rotate() @ crates/service/crates/token/src/lib.rs
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → err() @ crates/server/src/api/response.rs
│    ├─ FILE: crates/service/crates/token/src/lib.rs
│    │    ├─ TokenService::rotate()
│    ├─ FILE: crates/database/crates/router/src/token.rs
│    │    ├─ RouterTokenModel::rotate()
│    │    │    └─ CALL → Database::kind() @ crates/database/src/database.rs
│    │    │    └─ CALL → RouterTokenModel::find_by_token() @ crates/database/crates/router/src/token.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    │    │    └─ CALL → adapt_sql() @ crates/database/src/placeholder.rs
│    │    │    └─ CALL → Database::query() @ crates/database/src/database.rs
│    │    │    └─ CALL → BudgetGuard::commit() @ crates/router/src/rate_budget.rs
│    │    ├─ RouterTokenModel::find_by_token()
│    │    │    └─ CALL → adapt_sql() @ crates/database/src/placeholder.rs
│    │    │    └─ CALL → Database::kind() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::fetch_optional() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    ├─ FILE: crates/server/src/api/response.rs
│    │    ├─ ok()
│    │    ├─ err()
│    ├─ FILE: crates/database/src/database.rs
│    │    ├─ Database::kind()
│    │    ├─ DatabaseConnection::pool()
│    │    ├─ Database::query()
│    │    │    └─ CALL → Database::fetch_all() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    │    ├─ Database::fetch_optional()
│    │    ├─ Database::fetch_all()
│    ├─ FILE: crates/database/src/placeholder.rs
│    │    ├─ adapt_sql()
│    ├─ FILE: crates/router/src/rate_budget.rs
│    │    ├─ BudgetGuard::commit()
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
POST /console/api/tokens/bc_live_7d4e...example/rotate HTTP/1.1
Host: api.burncloud.example
Authorization: Bearer eyJhbGciOi...admin-jwt
Accept: application/json
Content-Type: application/json

{"name":"production","status":1,"quota":100000000,"ip_whitelist":["203.0.113.10"]}
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "new_token": "bc_live_9af2...example",
    "old_token_valid_until": "2026-08-11T15:30:00+08:00"
  }
}
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | Public/Protected Management route composition | ROUTE composition |
| 3 | `crates/server/src/api/auth.rs` | `auth_middleware(), verify_jwt(), public_routes()` | JWT middleware 与 public authentication routes | READ Authorization / Claims |
| 4 | `crates/server/src/api/token.rs` | `rotate_token()` | Token Handler / request validation / response mapping | READ/WRITE token request |
| 5 | `crates/service/crates/token/src/lib.rs` | `TokenService::*` | Token service boundary | SERVICE |
| 6 | `crates/database/crates/router/src/token.rs` | `RouterTokenModel::*` | Router token/quota/key persistence | READ/WRITE router token state |
| 7 | `crates/server/src/api/response.rs` | `err(), ok()` | 由 auth_middleware() 直接调用；由 rotate_token() 直接调用 | CALL / runtime-specific |
| 8 | `crates/database/src/database.rs` | `Database::fetch_all(), Database::fetch_optional(), Database::kind(), Database::query(), DatabaseConnection::pool()` | 由 Database::query() 直接调用；由 RouterTokenModel::find_by_token() 直接调用；由 RouterTokenModel::rotate() 直接调用 | CALL / runtime-specific |
| 9 | `crates/database/src/placeholder.rs` | `adapt_sql()` | 由 RouterTokenModel::find_by_token() 直接调用；由 RouterTokenModel::rotate() 直接调用 | CALL / runtime-specific |
| 10 | `crates/router/src/rate_budget.rs` | `BudgetGuard::commit()` | 由 RouterTokenModel::rotate() 直接调用 | CALL / runtime-specific |
| 11 | `crates/common/src/constants.rs` | `jwt_secret()` | 由 get_jwt_secret() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
