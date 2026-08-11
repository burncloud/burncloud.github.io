---
title: "System Monitor Auto Update"
slug: /background/long-running-jobs/system-monitor-auto-update
hide_table_of_contents: true
---

# System Monitor Auto Update

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Long-running Jobs → System Monitor Auto Update`

> **中文解释：** create_app() 启动 start_auto_update；周期采集 CPU、内存、磁盘并刷新内存缓存。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START / TRIGGER
│
├─ Trigger source
│    ├─ startup spawn / request-time tokio::spawn / manager restoration / channel message
│    └─ task: System Monitor Auto Update
│
├─ Spawn / registration
│    ├─ parent runtime creates async task/thread/loop
│    └─ DECISION: spawn/runtime handle available?
│         ├─ NO → task never starts; parent may log error
│         └─ YES → task owns/borrows required shared state
│
├─ Wait boundary
│    ├─ timer sleep / mpsc receive / polling interval / restored work item
│    └─ DECISION: trigger/event available?
│         ├─ NO → continue waiting
│         └─ YES → one iteration begins
│
├─ Input snapshot
│    ├─ read latest runtime/DB/request-derived state needed by job
│    └─ freeze iteration context
│
├─ Core job operation
│    ├─ execute System Monitor Auto Update
│    └─ may call DB / HTTP / filesystem / runtime service depending on task
│
├─ Operation result
│    └─ DECISION: iteration succeeds?
│         ├─ NO
│         │    ├─ log/record failure
│         │    ├─ preserve parent request availability when task is fail-open
│         │    └─ decide retry on next event/interval
│         └─ YES
│              ├─ update in-memory state and/or persistent state
│              └─ emit success telemetry/log
│
├─ Cancellation / lifetime
│    └─ DECISION: parent runtime still alive AND task should continue?
│         ├─ YES → 返回等待边界
│         └─ NO → release task resources
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
END / NEXT ITERATION
```


## 输入示例

> 后台任务通常没有 HTTP 请求体；这里把触发事件、队列/定时器和共享状态视为它的输入。

```text
trigger=Long-running Jobs
job=System Monitor Auto Update
runtime=running
shared_state=available
# 该类页面的“输入”不是 HTTP body，而是启动事件、定时器、队列消息或请求侧异步事件。
```

## 返回结果示例

> 后台任务通常不会直接向 HTTP 调用方返回 JSON；这里用一条构造的状态/日志结果表示一次成功执行后的可观测结果。

```text
2026-08-11T14:45:10+08:00 monitor_update cpu=31.7% memory=62.4% disk=48.9% status=ok
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/service/crates/monitor/src/lib.rs` | `entry-specific function(s) shown in E2E` | 当前入口在该文件执行的直接调用点 | runtime-specific |
| 3 | `crates/service/crates/monitor/src/service.rs` | `SystemMonitorService::*` | metrics cache + collector coordination | READ OS / WRITE memory cache |
| 4 | `crates/service/crates/monitor/src/collectors/cpu.rs` | `Collector::collect*()` | OS metric collector | READ operating-system metrics |
| 5 | `crates/service/crates/monitor/src/collectors/memory.rs` | `Collector::collect*()` | OS metric collector | READ operating-system metrics |
| 6 | `crates/service/crates/monitor/src/collectors/disk.rs` | `Collector::collect*()` | OS metric collector | READ operating-system metrics |
| 7 | `crates/database/src/database.rs` | `Database::new(), create_default_database()` | 由 create_default_database() 直接调用；由 start_server() 直接调用 | CALL / runtime-specific |
| 8 | `crates/database/crates/router/src/lib.rs` | `RouterDatabase::init(), RouterDatabase::insert_log(), RouterDatabase::insert_request_log()` | 由 create_router_app() 直接调用；由 start_server() 直接调用 | CALL / runtime-specific |
| 9 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::assign_role(), UserDatabase::init()` | 由 UserDatabase::init() 直接调用；由 start_server() 直接调用 | CALL / runtime-specific |
| 10 | `crates/service/crates/cache/src/service.rs` | `CacheService::new(), CacheService::with_config()` | 由 CacheService::new() 直接调用；由 create_app() 直接调用 | CALL / runtime-specific |
| 11 | `crates/router/src/lib.rs` | `EmptyResponseCounter::new(), configure_rate_budget_from_db(), create_router_app()` | 由 create_app() 直接调用；由 create_router_app() 直接调用 | CALL / runtime-specific |
| 12 | `crates/service/crates/user/src/lib.rs` | `UserService::new()` | 由 create_app() 直接调用 | CALL / runtime-specific |
| 13 | `crates/server/src/api/mod.rs` | `routes()` | 由 create_app() 直接调用 | CALL / runtime-specific |
| 14 | `crates/router/src/balancer/mod.rs` | `RoundRobinBalancer::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 15 | `crates/router/src/limiter.rs` | `RateLimiter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 16 | `crates/router/src/circuit_breaker.rs` | `CircuitBreaker::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 17 | `crates/router/src/model_router.rs` | `ModelRouter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 18 | `crates/router/src/channel_state.rs` | `ChannelStateTracker::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 19 | `crates/router/src/adaptor/factory.rs` | `DynamicAdaptorFactory::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 20 | `crates/router/src/adaptor/detector.rs` | `ApiVersionDetector::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 21 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::empty(), PriceCache::load()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 22 | `crates/service/crates/billing/src/calculator.rs` | `CostCalculator::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 23 | `crates/router/src/exchange_rate.rs` | `ExchangeRateService::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 24 | `crates/router/src/scheduler/mod.rs` | `load_scheduler_config()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 25 | `crates/router/src/rate_budget.rs` | `InMemoryBudget::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 26 | `crates/router/src/price_sync.rs` | `start_price_sync_task()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
