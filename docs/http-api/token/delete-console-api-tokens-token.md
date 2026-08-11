---
title: "DELETE /console/api/tokens/{token}"
slug: /http-api/token/delete-console-api-tokens-token
hide_table_of_contents: true
---

# DELETE /console/api/tokens/&#123;token&#125;

**树路径：** `BurnCloud → HTTP / API → Token → DELETE /console/api/tokens/{token}`

> **中文解释：** 删除 token。 核心调用：TokenService::delete。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方输入
│    ├─ Entry: DELETE /console/api/tokens/{token}
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
├─ routes() matches DELETE /console/api/tokens/{token}
├─ delete_token()
├─ parse Path / Query / Json according to method
├─ validate token-specific fields / rotation / whitelist parameters
└─ CALL TokenService::delete(...)
│
▼
FILE: crates/service/crates/token/src/lib.rs
│
├─ TokenService::delete()
└─ CALL RouterTokenModel::delete(...)
│
▼
FILE: crates/database/crates/router/src/token.rs
│
├─ RouterTokenModel::delete()
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
DELETE /console/api/tokens/bc_live_7d4e...example HTTP/1.1
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
  "message": "Token deleted"
}
```



## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | Public/Protected Management route composition | ROUTE composition |
| 3 | `crates/server/src/api/auth.rs` | `auth_middleware(), verify_jwt(), public_routes()` | JWT middleware 与 public authentication routes | READ Authorization / Claims |
| 4 | `crates/server/src/api/token.rs` | `delete_token()` | Token Handler / request validation / response mapping | READ/WRITE token request |
| 5 | `crates/service/crates/token/src/lib.rs` | `TokenService::*` | Token service boundary | SERVICE |
| 6 | `crates/database/crates/router/src/token.rs` | `RouterTokenModel::*` | Router token/quota/key persistence | READ/WRITE router token state |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
