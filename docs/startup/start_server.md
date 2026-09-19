---
title: "start_server"
slug: /startup/start_server
hide_table_of_contents: true
---

# start_server

**树路径：** `BurnCloud → Startup → Startup Chain → start_server`

> **中文解释：** 创建默认数据库 → RouterDatabase::init → UserDatabase::init → create_app → bind → axum::serve。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Process/environment input
│    ├─ startup target: start_server
│    ├─ environment variables / dotenv
│    ├─ CLI/platform mode
│    └─ filesystem/database availability
│
├─ Enter startup function
│    └─ execute start_server
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
│    │    │    └─ CALL → CacheService::new() @ crates/service/crates/cache/src/service.rs
│    │    │    └─ CALL → create_router_app() @ crates/router/src/lib.rs
│    │    │    └─ CALL → UserService::new() @ crates/service/crates/user/src/lib.rs
│    │    │    └─ CALL → routes() @ crates/server/src/api/mod.rs
│    ├─ FILE: crates/database/src/database.rs
│    │    ├─ create_default_database()
│    │    │    └─ CALL → Database::new() @ crates/database/src/database.rs
│    │    ├─ Database::new()
│    ├─ FILE: crates/database/crates/router/src/lib.rs
│    │    ├─ RouterDatabase::init()
│    ├─ FILE: crates/database/crates/user/src/lib.rs
│    │    ├─ UserDatabase::init()
│    │    │    └─ CALL → UserDatabase::assign_role() @ crates/database/crates/user/src/lib.rs
│    │    ├─ UserDatabase::assign_role()
│    ├─ FILE: crates/service/crates/monitor/src/service.rs
│    │    ├─ SystemMonitorService::new()
│    ├─ FILE: crates/service/crates/cache/src/service.rs
│    │    ├─ CacheService::new()
│    │    │    └─ CALL → CacheService::with_config() @ crates/service/crates/cache/src/service.rs
│    │    ├─ CacheService::with_config()
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
│    │    ├─ configure_rate_budget_from_db()
│    ├─ FILE: crates/service/crates/user/src/lib.rs
│    │    ├─ UserService::new()
│    ├─ FILE: crates/server/src/api/mod.rs
│    │    ├─ routes()
│    │    │    └─ CALL → public_routes() @ crates/server/src/api/auth.rs
│    │    │    └─ CALL → protected_routes() @ crates/server/src/api/auth.rs
│    │    │    └─ CALL → security_routes() @ crates/server/src/api/security.rs
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
│    │    ├─ PriceCache::empty()
│    ├─ FILE: crates/service/crates/billing/src/calculator.rs
│    │    ├─ CostCalculator::new()
│    ├─ FILE: crates/router/src/exchange_rate.rs
│    │    ├─ ExchangeRateService::new()
│    ├─ FILE: crates/router/src/scheduler/mod.rs
│    │    ├─ load_scheduler_config()
│    ├─ FILE: crates/router/src/rate_budget.rs
│    │    ├─ InMemoryBudget::new()
│    └─ FILE: crates/router/src/price_sync.rs
│    │    ├─ start_price_sync_task()
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
process_target=start_server
BURNCLOUD_MASTER_KEY=<configured-or-generated>
RUST_LOG=info
database_path=<runtime database>
enable_liveview=true
# 真实环境变量/参数以部署配置为准。
```

## 返回结果示例

> Startup 页面没有传统 API response；这里用构造的启动结果/运行态日志表示该阶段成功完成后系统应进入的状态。

```text
database=connected
router_db=initialized
user_db=initialized
listener=0.0.0.0:3000
server=running
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/database/src/database.rs` | `Database::new(), create_default_database()` | 由 create_default_database() 直接调用；由 start_server() 直接调用 | CALL / runtime-specific |
| 3 | `crates/database/crates/router/src/lib.rs` | `RouterDatabase::init(), RouterDatabase::insert_log(), RouterDatabase::insert_request_log()` | 由 create_router_app() 直接调用；由 start_server() 直接调用 | CALL / runtime-specific |
| 4 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::assign_role(), UserDatabase::init()` | 由 UserDatabase::init() 直接调用；由 start_server() 直接调用 | CALL / runtime-specific |
| 5 | `crates/service/crates/monitor/src/service.rs` | `SystemMonitorService::new()` | 由 create_app() 直接调用 | CALL / runtime-specific |
| 6 | `crates/service/crates/cache/src/service.rs` | `CacheService::new(), CacheService::with_config()` | 由 CacheService::new() 直接调用；由 create_app() 直接调用 | CALL / runtime-specific |
| 7 | `crates/router/src/lib.rs` | `EmptyResponseCounter::new(), configure_rate_budget_from_db(), create_router_app()` | 由 create_app() 直接调用；由 create_router_app() 直接调用 | CALL / runtime-specific |
| 8 | `crates/service/crates/user/src/lib.rs` | `UserService::new()` | 由 create_app() 直接调用 | CALL / runtime-specific |
| 9 | `crates/server/src/api/mod.rs` | `routes()` | 由 create_app() 直接调用 | CALL / runtime-specific |
| 10 | `crates/router/src/balancer/mod.rs` | `RoundRobinBalancer::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 11 | `crates/router/src/limiter.rs` | `RateLimiter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 12 | `crates/router/src/circuit_breaker.rs` | `CircuitBreaker::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 13 | `crates/router/src/model_router.rs` | `ModelRouter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 14 | `crates/router/src/channel_state.rs` | `ChannelStateTracker::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 15 | `crates/router/src/adaptor/factory.rs` | `DynamicAdaptorFactory::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 16 | `crates/router/src/adaptor/detector.rs` | `ApiVersionDetector::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 17 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::empty(), PriceCache::load()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 18 | `crates/service/crates/billing/src/calculator.rs` | `CostCalculator::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 19 | `crates/router/src/exchange_rate.rs` | `ExchangeRateService::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 20 | `crates/router/src/scheduler/mod.rs` | `load_scheduler_config()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 21 | `crates/router/src/rate_budget.rs` | `InMemoryBudget::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 22 | `crates/router/src/price_sync.rs` | `start_price_sync_task()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
