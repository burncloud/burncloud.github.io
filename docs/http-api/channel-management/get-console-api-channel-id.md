---
title: "GET /console/api/channel/{id}"
slug: /http-api/channel-management/get-console-api-channel-id
hide_table_of_contents: true
---

# GET /console/api/channel/&#123;id&#125;

**树路径：** `BurnCloud → HTTP / API → Channel Management → GET /console/api/channel/{id}`

> **中文解释：** 管理员按 ID 查询；不存在时返回 channel not found。 核心调用：ChannelService::get_by_id。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方输入
│    ├─ Entry: GET /console/api/channel/{id}
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
│    ├─ NO  → 其它顶层路由 / fallback
│    └─ YES → api::routes()
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ routes()
│    ├─ merge(channel::routes()) into protected_routes
│    └─ layer(middleware::from_fn(crate::auth_middleware))
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ auth_middleware()
│    ├─ read Authorization
│    ├─ require Bearer prefix
│    ├─ verify_jwt()
│    └─ DECISION: JWT valid?
│         ├─ NO  → HTTP 401 → END
│         └─ YES → Claims inserted into request extensions
│
▼
FILE: crates/server/src/api/channel.rs
│
├─ routes() matches GET /console/api/channel/{id}
├─ get_channel()
│    ├─ request extraction: Path<i32> → channel id
│    ├─ check_admin(&state, &claims)
│    └─ DECISION: admin role present?
│         ├─ NO  → err("Admin access required") → END
│         └─ YES → continue
│
├─ check_admin()
│    └─ CALL UserDatabase::get_user_roles(...)
│
▼
FILE: crates/database/crates/user/src/lib.rs
│
├─ UserDatabase::get_user_roles()
├─ DB connection / SQL role lookup
└─ return roles → channel.rs::check_admin()
│
▼
FILE: crates/server/src/api/channel.rs
│
├─ business invariant: 继续
└─ CALL ChannelService::get_by_id(...)
│
▼
FILE: crates/service/crates/channel/src/lib.rs
│
├─ ChannelService::get_by_id()
└─ CALL ChannelProviderModel::get_by_id(...)
│
▼
FILE: crates/database/crates/channel/src/channel_provider.rs
│
├─ ChannelProviderModel::get_by_id()
├─ db.get_connection() / SQL execution / row mapping
└─ DECISION: database operation successful?
     ├─ NO  → DatabaseError → service → handler → err(...)
     └─ YES → Vec<Channel>
│
▼
FILE: crates/service/crates/channel/src/lib.rs
│
└─ return Result to channel handler
│
▼
FILE: crates/server/src/api/channel.rs
│
├─ DECISION: ChannelService result Ok?
│    ├─ NO  → err(e)
│    └─ YES → ok(domain/DTO)
└─ IntoResponse → HTTP response
│
▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /console/api/channel/12 HTTP/1.1
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
    "id": 12,
    "name": "openai-primary",
    "channel_type": "openai",
    "base_url": "https://api.openai.com",
    "status": 1,
    "priority": 100,
    "weight": 100
  }
}
```


## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 Server、Router 合并、Middleware、fallback 入口 | READ runtime composition |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | 把 channel::routes() 合并进 protected_routes | ROUTE |
| 3 | `crates/server/src/api/auth.rs` | `auth_middleware(), verify_jwt()` | JWT 认证并注入 Claims | READ auth header |
| 4 | `crates/server/src/api/channel.rs` | `get_channel(), check_admin()` | 参数、管理员授权、Handler 响应映射 | READ/WRITE request domain |
| 5 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::get_user_roles()` | check_admin() 的角色查询 | READ user_roles |
| 6 | `crates/service/crates/channel/src/lib.rs` | `ChannelService::get_by_id()` | Channel 业务层 | SERVICE |
| 7 | `crates/database/crates/channel/src/channel_provider.rs` | `ChannelProviderModel::get_by_id()` | Channel 持久化 CRUD | READ/WRITE channel_providers |

> 这个索引只列入当前执行链中有源码依据的文件；类型定义文件但不执行逻辑的，不为了凑数量加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
