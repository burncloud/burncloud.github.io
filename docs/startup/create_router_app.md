---
title: "create_router_app"
slug: /startup/create_router_app
hide_table_of_contents: true
---

# create_router_app

**树路径：** `BurnCloud → Startup → Startup Chain → create_router_app`

> **中文解释：** 构建 HTTP client、limiter、circuit breaker、ModelRouter、scheduler、PriceCache、CostCalculator、rate budget、后台 writer/task，再注册显式路由和 proxy fallback。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Process/environment input
│    ├─ startup target: create_router_app
│    ├─ environment variables / dotenv
│    ├─ CLI/platform mode
│    └─ filesystem/database availability
│
├─ Enter startup function
│    └─ execute create_router_app
│
├─ Dependency initialization
│    ├─ construct required DB/services/runtime state
│    ├─ register routes/tasks as applicable
│    └─ DECISION: dependency initialization succeeds?
│         ├─ NO → propagate startup error → process/runtime not ready → END
│         └─ YES → next dependency
│
├─ Runtime composition
│    ├─ wire shared Arc/State/services
│    ├─ compose routers/middleware/background jobs
│    └─ make dependencies reachable from runtime entrypoints
│
├─ Readiness boundary
│    └─ DECISION: all required startup stages complete?
│         ├─ NO → startup fails/returns Err
│         └─ YES → expose listener/client/event loop/runtime
│
├─ Steady-state handoff
│    ├─ long-running loops take ownership of runtime
│    └─ requests/events can now enter documented entrypoints
│
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: crates/router/src/lib.rs
│    │    ├─ create_router_app()
│    │    │    └─ CALL → RoundRobinBalancer::new() @ crates/router/src/balancer/mod.rs
│    │    │    └─ CALL → RateLimiter::new() @ crates/router/src/limiter.rs
│    │    │    └─ CALL → CircuitBreaker::new() @ crates/router/src/circuit_breaker.rs
│    │    │    └─ CALL → ChannelStateTracker::new() @ crates/router/src/channel_state.rs
│    │    │    └─ CALL → ApiVersionDetector::new() @ crates/router/src/adaptor/detector.rs
│    │    │    └─ CALL → PriceCache::load() @ crates/service/crates/billing/src/cache.rs
│    │    │    └─ CALL → PriceCache::empty() @ crates/service/crates/billing/src/cache.rs
│    │    │    └─ CALL → CostCalculator::new() @ crates/service/crates/billing/src/calculator.rs
│    │    │    └─ CALL → ExchangeRateService::new() @ crates/router/src/exchange_rate.rs
│    │    │    └─ CALL → ExchangeRateService::load_rates_from_db() @ crates/router/src/exchange_rate.rs
│    │    ├─ proxy_handler()
│    │    │    └─ CALL → normalize_doubled_path() @ crates/router/src/lib.rs
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → build_response_with_header() @ crates/router/src/lib.rs
│    │    │    └─ CALL → RouterDatabase::validate_token_and_get_info() @ crates/database/crates/router/src/lib.rs
│    │    │    └─ CALL → RouterDatabase::update_token_accessed_time() @ crates/database/crates/router/src/lib.rs
│    │    │    └─ CALL → RouterDatabase::validate_token_detailed() @ crates/database/crates/router/src/lib.rs
│    │    │    └─ CALL → extract_model_from_gemini_path() @ crates/router/src/passthrough.rs
│    │    │    └─ CALL → RouterVideoTaskModel::get_by_task_id() @ crates/database/crates/router/src/router_video_task.rs
│    │    │    └─ CALL → ChannelProviderModel::get_by_id() @ crates/database/crates/channel/src/channel_provider.rs
│    │    │    └─ CALL → UnifiedTokenCounter::new() @ crates/service/crates/billing/src/counter.rs
│    │    ├─ proxy_logic()
│    │    │    └─ CALL → sanitize_request_body() @ crates/router/src/lib.rs
│    │    │    └─ CALL → sanitize_request_headers() @ crates/router/src/lib.rs
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → extract_model_from_gemini_path() @ crates/router/src/passthrough.rs
│    │    │    └─ CALL → UserService::resolve_traffic_class() @ crates/service/crates/user/src/lib.rs
│    │    │    └─ CALL → OrderType::from_db_row() @ crates/router/src/order_type.rs
│    │    │    └─ CALL → RoutingDecision::route_with_scheduler() @ crates/router/src/model_router.rs
│    │    │    └─ CALL → PriceCache::empty() @ crates/service/crates/billing/src/cache.rs
│    │    │    └─ CALL → build_response_with_header() @ crates/router/src/lib.rs
│    │    │    └─ CALL → CostCalculator::preflight() @ crates/service/crates/billing/src/calculator.rs
│    │    ├─ configure_rate_budget_from_db()
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::fetch_all() @ crates/database/src/database.rs
│    │    │    └─ CALL → BudgetGuard::configure() @ crates/router/src/rate_budget.rs
│    │    ├─ EmptyResponseCounter::new()
│    │    ├─ normalize_doubled_path()
│    │    ├─ build_response_with_header()
│    │    │    └─ CALL → PriceCache::empty() @ crates/service/crates/billing/src/cache.rs
│    ├─ FILE: crates/router/src/balancer/mod.rs
│    │    ├─ RoundRobinBalancer::new()
│    ├─ FILE: crates/router/src/limiter.rs
│    │    ├─ RateLimiter::new()
│    ├─ FILE: crates/router/src/circuit_breaker.rs
│    │    ├─ CircuitBreaker::new()
│    ├─ FILE: crates/router/src/channel_state.rs
│    │    ├─ ChannelStateTracker::new()
│    ├─ FILE: crates/router/src/adaptor/detector.rs
│    │    ├─ ApiVersionDetector::new()
│    ├─ FILE: crates/service/crates/billing/src/cache.rs
│    │    ├─ PriceCache::load()
│    │    │    └─ CALL → PriceCache::empty() @ crates/service/crates/billing/src/cache.rs
│    │    │    └─ CALL → PriceCache::refresh() @ crates/service/crates/billing/src/cache.rs
│    │    ├─ PriceCache::empty()
│    ├─ FILE: crates/service/crates/billing/src/calculator.rs
│    │    ├─ CostCalculator::new()
│    ├─ FILE: crates/router/src/exchange_rate.rs
│    │    ├─ ExchangeRateService::new()
│    │    ├─ ExchangeRateService::load_rates_from_db()
│    │    │    └─ CALL → Database::fetch_all() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    │    ├─ ExchangeRateService::start_sync_task()
│    │    │    └─ CALL → ExchangeRateService::load_rates_from_db() @ crates/router/src/exchange_rate.rs
│    ├─ FILE: crates/router/src/scheduler/mod.rs
│    │    ├─ load_scheduler_config()
│    ├─ FILE: crates/router/src/rate_budget.rs
│    │    ├─ BudgetGuard::configure()
│    │    │    └─ CALL → ConsumeOutcome::is_valid() @ crates/router/src/rate_budget.rs
│    │    │    └─ CALL → ChannelBuckets::new() @ crates/router/src/rate_budget.rs
│    ├─ FILE: crates/server/src/api/response.rs
│    │    ├─ ok()
│    ├─ FILE: crates/router/src/price_sync.rs
│    │    ├─ start_price_sync_task()
│    │    │    └─ CALL → PriceSyncService::with_config() @ crates/router/src/price_sync.rs
│    │    │    └─ CALL → PriceSyncService::new() @ crates/router/src/price_sync.rs
│    │    │    └─ CALL → PriceSyncService::sync_all() @ crates/router/src/price_sync.rs
│    │    │    └─ CALL → PriceCache::refresh() @ crates/service/crates/billing/src/cache.rs
│    ├─ FILE: crates/database/crates/router/src/lib.rs
│    │    ├─ RouterDatabase::insert_log()
│    │    │    └─ CALL → RouterLogModel::insert() @ crates/database/crates/router/src/log.rs
│    │    ├─ RouterDatabase::insert_request_log()
│    │    ├─ RouterDatabase::validate_token_and_get_info()
│    │    │    └─ CALL → Database::kind() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::fetch_optional() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    │    ├─ RouterDatabase::update_token_accessed_time()
│    │    │    └─ CALL → RouterTokenModel::update_accessed_time() @ crates/database/crates/router/src/token.rs
│    │    ├─ RouterDatabase::validate_token_detailed()
│    │    │    └─ CALL → RouterTokenModel::validate_detailed() @ crates/database/crates/router/src/token.rs
│    └─ FILE: crates/router/src/channel_health_manager.rs
│    │    ├─ ChannelHealthManager::new()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
     └─ component is READY / RUNNING
```


## 输入示例

> Startup 的输入是进程模式、环境变量、配置和外部资源可用性，而不是 API Request。

```text
process_target=create_router_app
BURNCLOUD_MASTER_KEY=<configured-or-generated>
RUST_LOG=info
database_path=<runtime database>
enable_liveview=true
# 真实环境变量/参数以部署配置为准。
```

## 返回结果示例

> Startup 页面没有传统 API response；这里用构造的启动结果/运行态日志表示该阶段成功完成后系统应进入的状态。

```text
http_client=ready
model_router=ready
circuit_breaker=ready
price_cache=ready
exchange_rates=ready
background_writers=running
router=ready
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/router/src/lib.rs` | `create_router_app(), proxy_handler(), proxy_logic()` | Data Plane 主控制流或 Router internal handler | READ/WRITE router runtime |
| 2 | `crates/router/src/model_router.rs` | `model_router` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 3 | `crates/router/src/circuit_breaker.rs` | `circuit_breaker` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 4 | `crates/router/src/affinity.rs` | `affinity` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 5 | `crates/router/src/channel_state.rs` | `channel_state` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 6 | `crates/router/src/aimd_limiter.rs` | `aimd_limiter` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 7 | `crates/router/src/price_sync.rs` | `price_sync` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 8 | `crates/router/src/exchange_rate.rs` | `exchange_rate` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 9 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::*` | pricing cache | INIT/read |
| 10 | `crates/service/crates/billing/src/calculator.rs` | `CostCalculator::*` | billing calculation engine | INIT/use |
| 11 | `crates/router/src/balancer/mod.rs` | `RoundRobinBalancer::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 12 | `crates/router/src/limiter.rs` | `RateLimiter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 13 | `crates/router/src/adaptor/detector.rs` | `ApiVersionDetector::new(), detect_and_update(), is_deprecation_error()` | 由 create_router_app() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 14 | `crates/router/src/scheduler/mod.rs` | `load_scheduler_config()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 15 | `crates/router/src/rate_budget.rs` | `BudgetGuard::commit(), BudgetGuard::configure(), ChannelBuckets::new(), ConsumeOutcome::is_valid()` | 由 BudgetGuard::configure() 直接调用；由 configure_rate_budget_from_db() 直接调用；由 create_router_app() 直接调用 | CALL / runtime-specific |
| 16 | `crates/server/src/api/response.rs` | `ok()` | 由 create_router_app() 直接调用；由 proxy_handler() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 17 | `crates/database/crates/router/src/lib.rs` | `RouterDatabase::deduct_quota(), RouterDatabase::insert_log(), RouterDatabase::insert_request_log(), RouterDatabase::update_token_accessed_time(), RouterDatabase::validate_token_and_get_info(), RouterDatabase::validate_token_detailed()` | 由 create_router_app() 直接调用；由 proxy_handler() 直接调用 | CALL / runtime-specific |
| 18 | `crates/router/src/channel_health_manager.rs` | `ChannelHealthManager::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
