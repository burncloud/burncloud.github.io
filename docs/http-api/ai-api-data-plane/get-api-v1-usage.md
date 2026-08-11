---
title: "GET /api/v1/usage"
slug: /http-api/ai-api-data-plane/get-api-v1-usage
hide_table_of_contents: true
---

# GET /api/v1/usage

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → GET /api/v1/usage`

> **中文解释：** 提取 Bearer Token，按新 token 表 → legacy token → JWT 的顺序识别用户，然后查询当月总请求、token 与成本。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /api/v1/usage
│    ├─ Input sources
│    │    ├─ Method + URI path
│    │    ├─ Query string（如有）
│    │    ├─ HTTP headers
│    │    └─ Request body（如有）
│    └─ DECISION: TCP/HTTP 请求能否到达 BurnCloud listener?
│         ├─ NO  → 网络层失败；应用代码未执行 → END
│         └─ YES → 进入 Axum
│
▼
FILE: crates/server/src/lib.rs
│
├─ 统一 HTTP Server
│    ├─ start_server() 已在进程启动时完成
│    │    ├─ database 初始化
│    │    ├─ RouterDatabase::init()
│    │    ├─ UserDatabase::init()
│    │    ├─ create_app(...)
│    │    ├─ TcpListener::bind(...)
│    │    └─ axum::serve(listener, app)
│    ├─ 当前请求进入 Unified Axum App
│    └─ 全局 middleware
│         ├─ CORS
│         ├─ TraceLayer
│         ├─ SetRequestIdLayer
│         └─ PropagateRequestIdLayer
│
├─ 顶层 Route 决策
│    └─ DECISION: Unified App 是否已有显式/合并路由命中当前 Method + Path?
│         ├─ YES（其它顶层 route）→ 对应 handler
│         └─ NO → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ Explicit Data Plane route
│    ├─ Route match: GET /api/v1/usage
│    └─ handler = usage_handler()
│
├─ Credential extraction
│    ├─ read Authorization header
│    ├─ require Bearer token
│    └─ DECISION: Bearer credential present?
│         ├─ NO  → HTTP 401 → END
│         └─ YES → extract_token_user(...)
│
├─ Multi-generation identity resolution
│    ├─ Try new Router token table
│    │    └─ validate_token_and_get_info(...)
│    ├─ DECISION: new token valid?
│    │    ├─ YES → resolve user_id
│    │    └─ NO  → legacy validation
│    ├─ validate_token_detailed(...)
│    ├─ DECISION: legacy token valid?
│    │    ├─ YES → resolve user_id
│    │    └─ NO  → JWT fallback
│    ├─ JWT decode / Claims.sub
│    └─ DECISION: any identity path resolved?
│         ├─ NO  → 401 / service-unavailable error branch → END
│         └─ YES → user_id
│
▼
FILE: crates/database/crates/router/src/lib.rs
│
├─ Usage aggregation query
│    ├─ CALL get_usage_stats(user_id, "month")
│    ├─ period = month
│    ├─ scope = resolved user_id
│    └─ DECISION: DB aggregation success?
│         ├─ NO  → HTTP 500 → END
│         └─ YES → usage rows / aggregate
│
▼
FILE: crates/router/src/lib.rs
│
├─ Response mapping
│    ├─ map DB aggregate → API response object
│    ├─ serialize JSON
│    └─ DECISION: serialization/build success?
│         ├─ NO  → internal response error branch
│         └─ YES → HTTP 200 application/json
│
├─ Side effects
│    ├─ no Provider call
│    ├─ no Scheduler
│    ├─ no inference billing deduction
│    └─ read-only usage query
│
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: crates/router/src/lib.rs
│    │    ├─ usage_handler()
│    │    │    └─ CALL → extract_token_user() @ crates/router/src/lib.rs
│    │    │    └─ CALL → get_usage_stats() @ crates/database/crates/router/src/log.rs
│    │    │    └─ CALL → build_response_with_header() @ crates/router/src/lib.rs
│    │    │    └─ CALL → build_response() @ crates/router/src/lib.rs
│    │    │    └─ CALL → json_error_body() @ crates/router/src/lib.rs
│    │    ├─ extract_token_user()
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → build_response() @ crates/router/src/lib.rs
│    │    │    └─ CALL → RouterDatabase::validate_token_and_get_info() @ crates/database/crates/router/src/lib.rs
│    │    │    └─ CALL → RouterDatabase::validate_token_detailed() @ crates/database/crates/router/src/lib.rs
│    │    ├─ build_response_with_header()
│    │    │    └─ CALL → PriceCache::empty() @ crates/service/crates/billing/src/cache.rs
│    │    ├─ build_response()
│    │    │    └─ CALL → PriceCache::empty() @ crates/service/crates/billing/src/cache.rs
│    │    ├─ json_error_body()
│    ├─ FILE: crates/database/crates/router/src/log.rs
│    │    ├─ get_usage_stats()
│    │    │    └─ CALL → Database::kind() @ crates/database/src/database.rs
│    │    │    └─ CALL → ph() @ crates/database/src/placeholder.rs
│    │    │    └─ CALL → Database::fetch_one() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    ├─ FILE: crates/server/src/api/response.rs
│    │    ├─ ok()
│    ├─ FILE: crates/database/crates/router/src/lib.rs
│    │    ├─ RouterDatabase::validate_token_and_get_info()
│    │    │    └─ CALL → Database::kind() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::fetch_optional() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    │    ├─ RouterDatabase::validate_token_detailed()
│    │    │    └─ CALL → RouterTokenModel::validate_detailed() @ crates/database/crates/router/src/token.rs
│    ├─ FILE: crates/database/src/database.rs
│    │    ├─ Database::kind()
│    │    ├─ Database::fetch_one()
│    │    ├─ DatabaseConnection::pool()
│    │    ├─ Database::fetch_optional()
│    ├─ FILE: crates/database/src/placeholder.rs
│    │    ├─ ph()
│    ├─ FILE: crates/service/crates/billing/src/cache.rs
│    │    ├─ PriceCache::empty()
│    └─ FILE: crates/database/crates/router/src/token.rs
│    │    ├─ RouterTokenModel::validate_detailed()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
     └─ Client receives 当前用户月度总 usage
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /api/v1/usage HTTP/1.1
Host: api.burncloud.example
Authorization: Bearer bc_live_7d4e...example
Accept: application/json
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "period": "month",
  "requests": 12842,
  "prompt_tokens": 18420560,
  "completion_tokens": 6912840,
  "total_tokens": 25333400,
  "cost": 126.67
}
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/router/src/lib.rs` | `create_router_app(), proxy_handler(), proxy_logic()` | Data Plane 主控制流或 Router internal handler | READ/WRITE router runtime |
| 3 | `crates/database/crates/router/src/lib.rs` | `entry-specific function(s) shown in E2E` | 当前入口在该文件执行的直接调用点 | runtime-specific |
| 4 | `crates/database/crates/router/src/log.rs` | `RouterLogModel::* / usage & billing queries` | Request accounting / usage / billing persistence | READ/WRITE router_logs |
| 5 | `crates/server/src/api/response.rs` | `ok()` | 由 extract_token_user() 直接调用 | CALL / runtime-specific |
| 6 | `crates/database/src/database.rs` | `Database::fetch_one(), Database::fetch_optional(), Database::kind(), DatabaseConnection::pool()` | 由 RouterDatabase::validate_token_and_get_info() 直接调用；由 get_usage_stats() 直接调用 | CALL / runtime-specific |
| 7 | `crates/database/src/placeholder.rs` | `ph()` | 由 get_usage_stats() 直接调用 | CALL / runtime-specific |
| 8 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::empty()` | 由 build_response() 直接调用；由 build_response_with_header() 直接调用 | CALL / runtime-specific |
| 9 | `crates/database/crates/router/src/token.rs` | `RouterTokenModel::validate_detailed()` | 由 RouterDatabase::validate_token_detailed() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
