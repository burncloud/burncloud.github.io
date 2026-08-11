---
title: "GET /console/api/channel"
slug: /http-api/channel-management/get-console-api-channel
hide_table_of_contents: true
---

# GET /console/api/channel

**树路径：** `BurnCloud → HTTP / API → Channel Management → GET /console/api/channel`

> **中文解释：** 管理员分页列出 Channel；limit 被限制在 1..100，offset 不小于 0。 核心调用：ChannelService::list。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方输入
│    ├─ Entry: GET /console/api/channel
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
├─ routes() matches GET /console/api/channel
├─ list_channels()
│    ├─ request extraction: Query<PaginationParams> → limit.clamp(1,100) / offset.max(0)
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
└─ CALL ChannelService::list(...)
│
▼
FILE: crates/service/crates/channel/src/lib.rs
│
├─ ChannelService::list()
└─ CALL ChannelProviderModel::list(...)
│
▼
FILE: crates/database/crates/channel/src/channel_provider.rs
│
├─ ChannelProviderModel::list()
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
│    ├─ FILE: crates/server/src/api/channel.rs
│    │    ├─ list_channels()
│    │    │    └─ CALL → check_admin() @ crates/server/src/api/channel.rs
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → err() @ crates/server/src/api/response.rs
│    │    ├─ check_admin()
│    │    │    └─ CALL → UserDatabase::get_user_roles() @ crates/database/crates/user/src/lib.rs
│    │    │    └─ CALL → err() @ crates/server/src/api/response.rs
│    ├─ FILE: crates/database/crates/user/src/lib.rs
│    │    ├─ UserDatabase::get_user_roles()
│    │    │    └─ CALL → Database::kind() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::query() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::fetch_all() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    ├─ FILE: crates/service/crates/channel/src/lib.rs
│    │    ├─ ChannelService::list()
│    ├─ FILE: crates/database/crates/channel/src/channel_provider.rs
│    │    ├─ ChannelProviderModel::list()
│    │    │    └─ CALL → Database::kind() @ crates/database/src/database.rs
│    │    │    └─ CALL → ph() @ crates/database/src/placeholder.rs
│    │    │    └─ CALL → Database::fetch_all() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    ├─ FILE: crates/server/src/api/response.rs
│    │    ├─ ok()
│    │    ├─ err()
│    ├─ FILE: crates/database/src/database.rs
│    │    ├─ Database::kind()
│    │    ├─ Database::query()
│    │    │    └─ CALL → Database::fetch_all() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    │    ├─ Database::fetch_all()
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    │    ├─ DatabaseConnection::pool()
│    ├─ FILE: crates/database/src/placeholder.rs
│    │    ├─ ph()
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
GET /console/api/channel HTTP/1.1
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
  "data": [
    {
      "id": 12,
      "name": "openai-primary",
      "channel_type": "openai",
      "base_url": "https://api.openai.com",
      "status": 1,
      "priority": 100,
      "weight": 100
    }
  ],
  "total": 1
}
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | Public/Protected Management route composition | ROUTE composition |
| 3 | `crates/server/src/api/auth.rs` | `auth_middleware(), verify_jwt(), public_routes()` | JWT middleware 与 public authentication routes | READ Authorization / Claims |
| 4 | `crates/server/src/api/channel.rs` | `list_channels(), check_admin()` | 参数、管理员授权、Handler 响应映射 | READ/WRITE request domain |
| 5 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::*` | User/role/recharge persistence | READ/WRITE user state |
| 6 | `crates/service/crates/channel/src/lib.rs` | `ChannelService::*` | Channel service boundary | SERVICE |
| 7 | `crates/database/crates/channel/src/channel_provider.rs` | `ChannelProviderModel::*` | Channel provider persistence | READ/WRITE channel_providers |
| 8 | `crates/server/src/api/response.rs` | `err(), ok()` | 由 auth_middleware() 直接调用；由 check_admin() 直接调用；由 list_channels() 直接调用 | CALL / runtime-specific |
| 9 | `crates/database/src/database.rs` | `Database::fetch_all(), Database::kind(), Database::query(), DatabaseConnection::pool()` | 由 ChannelProviderModel::list() 直接调用；由 Database::fetch_all() 直接调用；由 Database::query() 直接调用 | CALL / runtime-specific |
| 10 | `crates/database/src/placeholder.rs` | `ph()` | 由 ChannelProviderModel::list() 直接调用 | CALL / runtime-specific |
| 11 | `crates/common/src/constants.rs` | `jwt_secret()` | 由 get_jwt_secret() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
