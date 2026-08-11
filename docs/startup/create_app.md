---
title: "create_app"
slug: /startup/create_app
hide_table_of_contents: true
---

# create_app

**树路径：** `BurnCloud → Startup → Startup Chain → create_app`

> **中文解释：** 初始化 monitor/cache/data-plane router，组合 Management/Internal/LiveView，并挂载全局 middleware 和 data-plane fallback。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Process/environment input
│    ├─ startup target: create_app
│    ├─ environment variables / dotenv
│    ├─ CLI/platform mode
│    └─ filesystem/database availability
│
├─ Enter startup function
│    └─ execute create_app
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
│    ├─ FILE: crates/server/src/lib.rs
│    │    ├─ start_server()
│    │    │    └─ CALL → create_default_database() @ crates/database/src/database.rs
│    │    │    └─ CALL → RouterDatabase::init() @ crates/database/crates/router/src/lib.rs
│    │    │    └─ CALL → UserDatabase::init() @ crates/database/crates/user/src/lib.rs
│    │    │    └─ CALL → create_app() @ crates/server/src/lib.rs
│    │    ├─ create_app()
│    │    │    └─ CALL → SystemMonitorService::new() @ crates/service/crates/monitor/src/service.rs
│    │    │    └─ CALL → SystemMonitorService::start_auto_update() @ crates/service/crates/monitor/src/service.rs
│    │    │    └─ CALL → CacheService::new() @ crates/service/crates/cache/src/service.rs
│    │    │    └─ CALL → create_router_app() @ crates/router/src/lib.rs
│    │    │    └─ CALL → UserService::new() @ crates/service/crates/user/src/lib.rs
│    │    │    └─ CALL → liveview_router() @ crates/client/src/lib.rs
│    ├─ FILE: crates/server/src/api/mod.rs
│    │    ├─ routes()
│    │    │    └─ CALL → public_routes() @ crates/server/src/api/auth.rs
│    │    │    └─ CALL → protected_routes() @ crates/server/src/api/auth.rs
│    │    │    └─ CALL → security_routes() @ crates/server/src/api/security.rs
│    ├─ FILE: crates/client/src/lib.rs
│    │    ├─ liveview_router()
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → liveview_style_tags() @ crates/client/crates/client-shared/src/app_styles.rs
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
│    ├─ FILE: crates/database/src/database.rs
│    │    ├─ create_default_database()
│    │    │    └─ CALL → Database::new() @ crates/database/src/database.rs
│    ├─ FILE: crates/database/crates/router/src/lib.rs
│    │    ├─ RouterDatabase::init()
│    │    │    └─ CALL → Database::kind() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::query() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    ├─ FILE: crates/database/crates/user/src/lib.rs
│    │    ├─ UserDatabase::init()
│    │    │    └─ CALL → Database::kind() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::query() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::fetch_one() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::fetch_all() @ crates/database/src/database.rs
│    │    │    └─ CALL → UserDatabase::assign_role() @ crates/database/crates/user/src/lib.rs
│    ├─ FILE: crates/service/crates/monitor/src/service.rs
│    │    ├─ SystemMonitorService::new()
│    │    ├─ SystemMonitorService::start_auto_update()
│    │    │    └─ CALL → SystemMonitorService::collect_metrics_internal() @ crates/service/crates/monitor/src/service.rs
│    ├─ FILE: crates/service/crates/cache/src/service.rs
│    │    ├─ CacheService::new()
│    ├─ FILE: crates/service/crates/user/src/lib.rs
│    │    ├─ UserService::new()
│    ├─ FILE: crates/server/src/api/auth.rs
│    │    ├─ public_routes()
│    │    ├─ protected_routes()
│    ├─ FILE: crates/server/src/api/security.rs
│    │    ├─ security_routes()
│    ├─ FILE: crates/server/src/api/response.rs
│    │    ├─ ok()
│    ├─ FILE: crates/client/crates/client-shared/src/app_styles.rs
│    │    ├─ liveview_style_tags()
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
│    └─ FILE: crates/router/src/exchange_rate.rs
│    │    ├─ ExchangeRateService::new()
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
process_target=create_app
BURNCLOUD_MASTER_KEY=<configured-or-generated>
RUST_LOG=info
database_path=<runtime database>
enable_liveview=true
# 真实环境变量/参数以部署配置为准。
```

## 返回结果示例

> Startup 页面没有传统 API response；这里用构造的启动结果/运行态日志表示该阶段成功完成后系统应进入的状态。

```text
monitor=started
cache=ready
management_routes=mounted
internal_routes=mounted
liveview=enabled
data_plane_fallback=mounted
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | Public/Protected Management route composition | ROUTE composition |
| 3 | `crates/client/src/lib.rs` | `liveview_router(), LiveViewPool::launch()` | LiveView HTTP shell / WebSocket router | NETWORK/UI runtime |
| 4 | `crates/service/crates/monitor/src/service.rs` | `SystemMonitorService::*` | metrics cache + collector coordination | READ OS / WRITE memory cache |
| 5 | `crates/service/crates/cache/src/service.rs` | `CacheService::*` | Redis-backed cache implementation | READ/WRITE Redis |
| 6 | `crates/router/src/lib.rs` | `create_router_app(), proxy_handler(), proxy_logic()` | Data Plane 主控制流或 Router internal handler | READ/WRITE router runtime |
| 7 | `crates/database/src/database.rs` | `Database::fetch_all(), Database::fetch_one(), Database::kind(), Database::new(), Database::query(), DatabaseConnection::pool(), create_default_database()` | 由 RouterDatabase::init() 直接调用；由 UserDatabase::init() 直接调用；由 create_default_database() 直接调用 | CALL / runtime-specific |
| 8 | `crates/database/crates/router/src/lib.rs` | `RouterDatabase::deduct_quota(), RouterDatabase::init(), RouterDatabase::insert_log(), RouterDatabase::insert_request_log(), RouterDatabase::update_token_accessed_time(), RouterDatabase::validate_token_and_get_info(), RouterDatabase::validate_token_detailed()` | 由 create_router_app() 直接调用；由 proxy_handler() 直接调用；由 start_server() 直接调用 | CALL / runtime-specific |
| 9 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::assign_role(), UserDatabase::init()` | 由 UserDatabase::init() 直接调用；由 start_server() 直接调用 | CALL / runtime-specific |
| 10 | `crates/service/crates/user/src/lib.rs` | `UserService::new(), UserService::resolve_traffic_class()` | 由 create_app() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 11 | `crates/server/src/api/auth.rs` | `protected_routes(), public_routes()` | 由 routes() 直接调用 | CALL / runtime-specific |
| 12 | `crates/server/src/api/security.rs` | `security_routes()` | 由 routes() 直接调用 | CALL / runtime-specific |
| 13 | `crates/server/src/api/response.rs` | `ok()` | 由 create_router_app() 直接调用；由 liveview_router() 直接调用；由 proxy_handler() 直接调用 | CALL / runtime-specific |
| 14 | `crates/client/crates/client-shared/src/app_styles.rs` | `liveview_style_tags()` | 由 liveview_router() 直接调用 | CALL / runtime-specific |
| 15 | `crates/router/src/balancer/mod.rs` | `RoundRobinBalancer::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 16 | `crates/router/src/limiter.rs` | `RateLimiter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 17 | `crates/router/src/circuit_breaker.rs` | `CircuitBreaker::new(), CircuitBreaker::record_failure_with_type()` | 由 create_router_app() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 18 | `crates/router/src/channel_state.rs` | `ChannelStateTracker::new(), ChannelStateTracker::record_error()` | 由 create_router_app() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 19 | `crates/router/src/adaptor/detector.rs` | `ApiVersionDetector::new(), detect_and_update(), is_deprecation_error()` | 由 create_router_app() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 20 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::empty(), PriceCache::load(), PriceCache::refresh()` | 由 PriceCache::load() 直接调用；由 create_router_app() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 21 | `crates/service/crates/billing/src/calculator.rs` | `CostCalculator::calculate(), CostCalculator::new(), CostCalculator::preflight()` | 由 create_router_app() 直接调用；由 proxy_handler() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 22 | `crates/router/src/exchange_rate.rs` | `ExchangeRateService::load_rates_from_db(), ExchangeRateService::new(), ExchangeRateService::start_sync_task()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
