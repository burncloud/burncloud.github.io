---
title: "GET /v1/videos/{task_id}"
slug: /http-api/ai-api-data-plane/get-v1-videos-task_id
hide_table_of_contents: true
---

# GET /v1/videos/&#123;task_id&#125;

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → GET /v1/videos/{task_id}`

> **中文解释：** 先鉴权，再从 task_id 查原始 channel_id；按该 Channel 的 base_url/key 直接轮询上游，不重新走模型调度。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /v1/videos/{task_id}
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
│         ├─ YES（其它 route）→ corresponding handler
│         └─ NO → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ proxy_handler entry
│    ├─ normalize path
│    ├─ extract supported credential
│    ├─ validate token/user
│    ├─ quota guard
│    └─ local rate limiter
│
├─ Video polling special-case detection
│    └─ DECISION: Method == GET AND Path starts with /v1/videos/ ?
│         ├─ NO  → normal inference proxy_logic
│         └─ YES → polling branch
│
├─ Task identity
│    ├─ task_id = URL suffix
│    └─ DECISION: task_id non-empty/valid enough for lookup?
│         ├─ NO  → client/not-found error → END
│         └─ YES → DB lookup
│
▼
FILE: crates/database/crates/router/src/video_task.rs
│
├─ Read persisted task mapping
│    ├─ RouterVideoTaskModel::get_by_task_id(task_id)
│    └─ DECISION: mapping exists?
│         ├─ NO  → HTTP 404 task_not_found → END
│         └─ YES → channel_id + stored task metadata
│
▼
FILE: crates/database/crates/channel/src/lib.rs
│
├─ Load original Channel
│    ├─ ChannelProviderModel::get_by_id(channel_id)
│    └─ DECISION: Channel record available/configured?
│         ├─ NO  → HTTP 502 → END
│         └─ YES → base_url + credential
│
▼
FILE: crates/router/src/lib.rs
│
├─ Direct upstream polling request
│    ├─ construct {base_url}/v1/videos/{task_id}
│    ├─ apply original Channel authentication
│    ├─ IMPORTANT: no new scheduler/model selection
│    └─ send GET through shared HTTP client
│
├─ Upstream polling result
│    └─ DECISION: network/upstream request succeeds?
│         ├─ NO  → HTTP 502 → END
│         └─ YES
│              ├─ preserve upstream status
│              ├─ collect upstream body
│              └─ return polling response
│
├─ Side effects
│    ├─ task mapping is read-only in this request
│    ├─ no fresh task mapping created
│    └─ no model scheduler selection
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
│    │    ├─ proxy_handler()
│    │    │    └─ CALL → normalize_doubled_path() @ crates/router/src/lib.rs
│    │    │    └─ CALL → build_response_with_header() @ crates/router/src/lib.rs
│    │    │    └─ CALL → RouterDatabase::validate_token_and_get_info() @ crates/database/crates/router/src/lib.rs
│    │    │    └─ CALL → RouterDatabase::update_token_accessed_time() @ crates/database/crates/router/src/lib.rs
│    │    │    └─ CALL → RouterDatabase::validate_token_detailed() @ crates/database/crates/router/src/lib.rs
│    │    │    └─ CALL → extract_model_from_gemini_path() @ crates/router/src/passthrough.rs
│    │    │    └─ CALL → RouterVideoTaskModel::get_by_task_id() @ crates/database/crates/router/src/router_video_task.rs
│    │    │    └─ CALL → ChannelProviderModel::get_by_id() @ crates/database/crates/channel/src/channel_provider.rs
│    │    │    └─ CALL → UnifiedTokenCounter::new() @ crates/service/crates/billing/src/counter.rs
│    │    │    └─ CALL → proxy_logic() @ crates/router/src/lib.rs
│    │    ├─ proxy_logic()
│    │    │    └─ CALL → sanitize_request_body() @ crates/router/src/lib.rs
│    │    │    └─ CALL → sanitize_request_headers() @ crates/router/src/lib.rs
│    │    │    └─ CALL → extract_model_from_gemini_path() @ crates/router/src/passthrough.rs
│    │    │    └─ CALL → UserService::resolve_traffic_class() @ crates/service/crates/user/src/lib.rs
│    │    │    └─ CALL → OrderType::from_db_row() @ crates/router/src/order_type.rs
│    │    │    └─ CALL → build_response_with_header() @ crates/router/src/lib.rs
│    │    │    └─ CALL → record_failover_attempt() @ crates/router/src/lib.rs
│    │    │    └─ CALL → BudgetGuard::new() @ crates/router/src/rate_budget.rs
│    │    │    └─ CALL → should_passthrough() @ crates/router/src/passthrough.rs
│    │    │    └─ CALL → build_gemini_passthrough_url() @ crates/router/src/passthrough.rs
│    │    ├─ configure_rate_budget_from_db()
│    │    ├─ EmptyResponseCounter::new()
│    │    ├─ normalize_doubled_path()
│    │    ├─ build_response_with_header()
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
│    ├─ FILE: crates/database/crates/router/src/lib.rs
│    │    ├─ RouterDatabase::insert_log()
│    │    │    └─ CALL → RouterLogModel::insert() @ crates/database/crates/router/src/log.rs
│    │    ├─ RouterDatabase::insert_request_log()
│    │    │    └─ CALL → RouterRequestLogModel::insert() @ crates/database/crates/router/src/log.rs
│    │    ├─ RouterDatabase::validate_token_and_get_info()
│    │    ├─ RouterDatabase::update_token_accessed_time()
│    │    │    └─ CALL → RouterTokenModel::update_accessed_time() @ crates/database/crates/router/src/token.rs
│    │    ├─ RouterDatabase::validate_token_detailed()
│    │    │    └─ CALL → RouterTokenModel::validate_detailed() @ crates/database/crates/router/src/token.rs
│    ├─ FILE: crates/router/src/channel_health_manager.rs
│    │    ├─ ChannelHealthManager::new()
│    └─ FILE: crates/router/src/passthrough.rs
│    │    ├─ extract_model_from_gemini_path()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
     └─ Client receives current video task state
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /v1/videos/video_task_bc_01JXYZ HTTP/1.1
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
  "id": "video_task_bc_01JXYZ",
  "object": "video.generation",
  "status": "completed",
  "model": "video-model-pro",
  "output": [
    {
      "url": "https://example.invalid/videos/video_task_bc_01JXYZ.mp4"
    }
  ],
  "duration": 5,
  "resolution": "1080p"
}
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/router/src/lib.rs` | `create_router_app(), proxy_handler(), proxy_logic()` | Data Plane 主控制流或 Router internal handler | READ/WRITE router runtime |
| 3 | `crates/database/crates/channel/src/lib.rs` | `entry-specific function(s) shown in E2E` | 当前入口在该文件执行的直接调用点 | runtime-specific |
| 4 | `crates/database/crates/router/src/router_video_task.rs` | `RouterVideoTaskModel::*` | Video task → channel mapping persistence | READ/WRITE video task mapping |
| 5 | `crates/database/crates/channel/src/channel_provider.rs` | `ChannelProviderModel::*` | Channel provider persistence | READ/WRITE channel_providers |
| 6 | `crates/router/src/balancer/mod.rs` | `RoundRobinBalancer::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 7 | `crates/router/src/limiter.rs` | `RateLimiter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 8 | `crates/router/src/circuit_breaker.rs` | `CircuitBreaker::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 9 | `crates/router/src/model_router.rs` | `ModelRouter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 10 | `crates/router/src/channel_state.rs` | `ChannelStateTracker::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 11 | `crates/router/src/adaptor/factory.rs` | `DynamicAdaptorFactory::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 12 | `crates/router/src/adaptor/detector.rs` | `ApiVersionDetector::is_deprecation_error(), ApiVersionDetector::new()` | 由 create_router_app() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 13 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::empty(), PriceCache::load()` | 由 PriceCache::load() 直接调用；由 create_router_app() 直接调用 | CALL / runtime-specific |
| 14 | `crates/service/crates/billing/src/calculator.rs` | `CostCalculator::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 15 | `crates/router/src/exchange_rate.rs` | `ExchangeRateService::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 16 | `crates/router/src/scheduler/mod.rs` | `load_scheduler_config()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 17 | `crates/router/src/rate_budget.rs` | `BudgetGuard::new(), InMemoryBudget::new()` | 由 create_router_app() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 18 | `crates/router/src/price_sync.rs` | `PriceSyncService::new(), PriceSyncService::with_config(), start_price_sync_task()` | 由 create_router_app() 直接调用；由 start_price_sync_task() 直接调用 | CALL / runtime-specific |
| 19 | `crates/database/crates/router/src/lib.rs` | `RouterDatabase::deduct_quota(), RouterDatabase::insert_log(), RouterDatabase::insert_request_log(), RouterDatabase::update_token_accessed_time(), RouterDatabase::validate_token_and_get_info(), RouterDatabase::validate_token_detailed()` | 由 create_router_app() 直接调用；由 proxy_handler() 直接调用 | CALL / runtime-specific |
| 20 | `crates/router/src/channel_health_manager.rs` | `ChannelHealthManager::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 21 | `crates/router/src/passthrough.rs` | `build_gemini_passthrough_url(), extract_model_from_gemini_path(), should_passthrough()` | 由 proxy_handler() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
