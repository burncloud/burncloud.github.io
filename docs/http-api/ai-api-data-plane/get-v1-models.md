---
title: "GET /v1/models"
slug: /http-api/ai-api-data-plane/get-v1-models
hide_table_of_contents: true
---

# GET /v1/models

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → GET /v1/models`

> **中文解释：** 读取 channel_abilities 中 enabled = 1 的 DISTINCT model；不进入 proxy_handler，也不做用户鉴权、调度或 Provider 调用。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /v1/models
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
│         ├─ YES（其它顶层 route）→ 进入对应 handler；本页路径结束
│         └─ NO（/v1/models）→ fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ Data Plane route match
│    ├─ create_router_app() 已注册显式 GET /v1/models
│    └─ DECISION: Method == GET AND Path == /v1/models ?
│         ├─ NO  → 其它显式 usage route 或 proxy_handler fallback
│         └─ YES → models_handler(State<AppState>)
│
├─ Authentication / authorization boundary
│    ├─ 当前 handler 不读取 Authorization
│    ├─ 不调用 Token/JWT validation
│    ├─ 不解析 user_id / group
│    └─ 因此没有当前用户维度的模型可见性过滤
│
├─ Handler local state
│    ├─ model_entries = []
│    ├─ SystemTime::now()
│    ├─ duration_since(UNIX_EPOCH)
│    └─ DECISION: system time conversion OK?
│         ├─ YES → current_time = duration.as_secs()
│         └─ NO  → unwrap_or_default() → current_time = 0
│
├─ CALL → ChannelAbilityModel::list_distinct_models(&state.db)
│
▼
FILE: crates/database/crates/channel/src/channel_ability.rs
│
├─ Database connection
│    ├─ db.get_connection()
│    └─ DECISION: connection acquired?
│         ├─ NO  → return Err → 回到 handler
│         └─ YES → conn.pool()
│
├─ SQL / state read
│    ├─ SELECT DISTINCT model
│    ├─ FROM channel_abilities
│    ├─ WHERE enabled = 1
│    └─ ORDER BY model
│
├─ sqlx::query_as(sql).fetch_all(pool).await
│    └─ DECISION: SQL success?
│         ├─ NO  → return Err
│         └─ YES → Vec<(String,)> → map → Ok(Vec<String>)
│
├─ Visibility semantics
│    ├─ INCLUDE only ability.enabled = 1
│    ├─ DISTINCT by model
│    ├─ NO user/group filter
│    ├─ NO channel_providers.status join
│    ├─ NO health/circuit/capacity check
│    └─ NO quota/price/billing check
│
▼
FILE: crates/router/src/lib.rs
│
├─ Handler branch merge
│    └─ DECISION: list_distinct_models returned Ok?
│         ├─ NO / Err
│         │    ├─ if let Ok(...) body skipped
│         │    └─ model_entries stays []
│         └─ YES
│              └─ FOR EACH model
│                   ├─ id = model
│                   ├─ object = "model"
│                   ├─ created = current_time
│                   ├─ owned_by = "burncloud"
│                   ├─ permission = []
│                   ├─ root = model
│                   ├─ parent = null
│                   └─ push → model_entries
│
├─ Serialization
│    ├─ response_json = {object:"list", data:model_entries}
│    ├─ serde_json::to_string(...)
│    └─ DECISION: serialization success?
│         ├─ YES → normal JSON body
│         └─ NO  → literal fallback {"object":"list","data":[]}
│
├─ HTTP response construction
│    ├─ build_response_with_header(StatusCode::OK, content-type, application/json, body)
│    ├─ Response::builder().status(200).header(...).body(...)
│    └─ DECISION: response builder success?
│         ├─ YES → HTTP 200 + JSON body
│         └─ NO  → retry status 200 + empty body
│              └─ DECISION: retry success?
│                   ├─ YES → HTTP 200 + empty body
│                   └─ NO  → Response::new(Body::empty())
│
├─ Explicitly NOT executed
│    ├─ proxy_handler
│    ├─ Token/JWT auth
│    ├─ Quota / rate limiter
│    ├─ ModelRouter / Scheduler
│    ├─ Circuit Breaker
│    ├─ Billing
│    └─ Provider / upstream
│
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: crates/router/src/lib.rs
│    │    ├─ create_router_app()
│    │    │    └─ CALL → RoundRobinBalancer::new() @ crates/router/src/balancer/mod.rs
│    │    │    └─ CALL → RateLimiter::new() @ crates/router/src/limiter.rs
│    │    │    └─ CALL → CircuitBreaker::new() @ crates/router/src/circuit_breaker.rs
│    │    │    └─ CALL → ModelRouter::new() @ crates/router/src/model_router.rs
│    │    │    └─ CALL → ChannelStateTracker::new() @ crates/router/src/channel_state.rs
│    │    │    └─ CALL → DynamicAdaptorFactory::new() @ crates/router/src/adaptor/factory.rs
│    │    │    └─ CALL → ApiVersionDetector::new() @ crates/router/src/adaptor/detector.rs
│    │    │    └─ CALL → PriceCache::load() @ crates/service/crates/billing/src/cache.rs
│    │    │    └─ CALL → PriceCache::empty() @ crates/service/crates/billing/src/cache.rs
│    │    │    └─ CALL → CostCalculator::new() @ crates/service/crates/billing/src/calculator.rs
│    │    ├─ models_handler()
│    │    │    └─ CALL → ChannelAbilityModel::list_distinct_models() @ crates/database/crates/channel/src/channel_ability.rs
│    │    │    └─ CALL → build_response_with_header() @ crates/router/src/lib.rs
│    │    ├─ build_response_with_header()
│    │    ├─ EmptyResponseCounter::new()
│    │    ├─ configure_rate_budget_from_db()
│    ├─ FILE: crates/router/src/balancer/mod.rs
│    │    ├─ RoundRobinBalancer::new()
│    ├─ FILE: crates/router/src/limiter.rs
│    │    ├─ RateLimiter::new()
│    ├─ FILE: crates/router/src/circuit_breaker.rs
│    │    ├─ CircuitBreaker::new()
│    ├─ FILE: crates/router/src/model_router.rs
│    │    ├─ ModelRouter::new()
│    ├─ FILE: crates/router/src/channel_state.rs
│    │    ├─ ChannelStateTracker::new()
│    ├─ FILE: crates/router/src/adaptor/factory.rs
│    │    ├─ DynamicAdaptorFactory::new()
│    ├─ FILE: crates/router/src/adaptor/detector.rs
│    │    ├─ ApiVersionDetector::new()
│    ├─ FILE: crates/service/crates/billing/src/cache.rs
│    │    ├─ PriceCache::load()
│    │    │    └─ CALL → PriceCache::empty() @ crates/service/crates/billing/src/cache.rs
│    │    ├─ PriceCache::empty()
│    ├─ FILE: crates/service/crates/billing/src/calculator.rs
│    │    ├─ CostCalculator::new()
│    ├─ FILE: crates/router/src/exchange_rate.rs
│    │    ├─ ExchangeRateService::new()
│    ├─ FILE: crates/router/src/scheduler/mod.rs
│    │    ├─ load_scheduler_config()
│    ├─ FILE: crates/router/src/rate_budget.rs
│    │    ├─ InMemoryBudget::new()
│    ├─ FILE: crates/router/src/price_sync.rs
│    │    ├─ start_price_sync_task()
│    │    │    └─ CALL → PriceSyncService::with_config() @ crates/router/src/price_sync.rs
│    │    │    └─ CALL → PriceSyncService::new() @ crates/router/src/price_sync.rs
│    │    ├─ PriceSyncService::with_config()
│    │    ├─ PriceSyncService::new()
│    ├─ FILE: crates/database/crates/router/src/lib.rs
│    │    ├─ RouterDatabase::insert_log()
│    │    │    └─ CALL → RouterLogModel::insert() @ crates/database/crates/router/src/log.rs
│    │    ├─ RouterDatabase::insert_request_log()
│    │    │    └─ CALL → RouterRequestLogModel::insert() @ crates/database/crates/router/src/log.rs
│    ├─ FILE: crates/router/src/channel_health_manager.rs
│    │    ├─ ChannelHealthManager::new()
│    ├─ FILE: crates/database/crates/channel/src/channel_ability.rs
│    │    ├─ ChannelAbilityModel::list_distinct_models()
│    └─ FILE: crates/database/crates/router/src/log.rs
│    │    ├─ RouterLogModel::insert()
│    │    ├─ RouterRequestLogModel::insert()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
     └─ Client receives model-list response
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /v1/models HTTP/1.1
Host: api.burncloud.example
Accept: application/json
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "object": "list",
  "data": [
    {
      "id": "gpt-5.4",
      "object": "model",
      "created": 1786380000,
      "owned_by": "burncloud",
      "permission": [],
      "root": "gpt-5.4",
      "parent": null
    },
    {
      "id": "claude-sonnet-4-5",
      "object": "model",
      "created": 1786380000,
      "owned_by": "burncloud",
      "permission": [],
      "root": "claude-sonnet-4-5",
      "parent": null
    }
  ]
}
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/router/src/lib.rs` | `create_router_app(), proxy_handler(), proxy_logic()` | Data Plane 主控制流或 Router internal handler | READ/WRITE router runtime |
| 3 | `crates/database/crates/channel/src/channel_ability.rs` | `ChannelAbilityModel::*` | Model/group/channel ability persistence | READ/WRITE channel_abilities |
| 4 | `crates/router/src/balancer/mod.rs` | `RoundRobinBalancer::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 5 | `crates/router/src/limiter.rs` | `RateLimiter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 6 | `crates/router/src/circuit_breaker.rs` | `CircuitBreaker::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 7 | `crates/router/src/model_router.rs` | `ModelRouter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 8 | `crates/router/src/channel_state.rs` | `ChannelStateTracker::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 9 | `crates/router/src/adaptor/factory.rs` | `DynamicAdaptorFactory::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 10 | `crates/router/src/adaptor/detector.rs` | `ApiVersionDetector::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 11 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::empty(), PriceCache::load()` | 由 PriceCache::load() 直接调用；由 create_router_app() 直接调用 | CALL / runtime-specific |
| 12 | `crates/service/crates/billing/src/calculator.rs` | `CostCalculator::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 13 | `crates/router/src/exchange_rate.rs` | `ExchangeRateService::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 14 | `crates/router/src/scheduler/mod.rs` | `load_scheduler_config()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 15 | `crates/router/src/rate_budget.rs` | `InMemoryBudget::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 16 | `crates/router/src/price_sync.rs` | `PriceSyncService::new(), PriceSyncService::with_config(), start_price_sync_task()` | 由 create_router_app() 直接调用；由 start_price_sync_task() 直接调用 | CALL / runtime-specific |
| 17 | `crates/database/crates/router/src/lib.rs` | `RouterDatabase::insert_log(), RouterDatabase::insert_request_log()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 18 | `crates/router/src/channel_health_manager.rs` | `ChannelHealthManager::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 19 | `crates/database/crates/router/src/log.rs` | `RouterLogModel::insert(), RouterRequestLogModel::insert()` | 由 RouterDatabase::insert_log() 直接调用；由 RouterDatabase::insert_request_log() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
