---
title: "POST /console/api/tokens"
slug: /http-api/token/post-console-api-tokens
hide_table_of_contents: true
---

# POST /console/api/tokens

**树路径：** `BurnCloud → HTTP / API → Token → POST /console/api/tokens`

> **中文解释：** 生成 bc_live_&lt;uuid&gt;，构造 RouterToken 后写入数据库。 核心调用：TokenService::create。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方输入
│    ├─ Entry: POST /console/api/tokens
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
├─ routes() matches POST /console/api/tokens
├─ create_token()
├─ parse Path / Query / Json according to method
├─ validate token-specific fields / rotation / whitelist parameters
└─ CALL TokenService::create(...)
│
▼
FILE: crates/service/crates/token/src/lib.rs
│
├─ TokenService::create()
└─ CALL RouterTokenModel::create(...)
│
▼
FILE: crates/database/crates/router/src/token.rs
│
├─ RouterTokenModel::create()
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
▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
POST /console/api/tokens HTTP/1.1
Host: api.burncloud.example
Authorization: Bearer eyJhbGciOi...admin-jwt
Accept: application/json
Content-Type: application/json

{"name":"production","status":1,"quota":100000000,"ip_whitelist":["203.0.113.10"]}
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 201 Created
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
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 Server、Router 合并、Middleware、fallback 入口 | READ runtime composition |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | protected route composition | ROUTE |
| 3 | `crates/server/src/api/auth.rs` | `auth_middleware(), verify_jwt()` | JWT authentication | READ auth |
| 4 | `crates/server/src/api/token.rs` | `create_token()` | Token Handler / request validation / response mapping | READ/WRITE token request |
| 5 | `crates/service/crates/token/src/lib.rs` | `TokenService::create()` | Token business service | SERVICE |
| 6 | `crates/database/crates/router/src/token.rs` | `RouterTokenModel::create()` | Router token persistence | READ/WRITE router_tokens |

> 这个索引只列入当前执行链中有源码依据的文件；类型定义文件但不执行逻辑的，不为了凑数量加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
