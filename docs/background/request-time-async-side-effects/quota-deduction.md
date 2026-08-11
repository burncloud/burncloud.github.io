---
title: "Quota deduction"
slug: /background/request-time-async-side-effects/quota-deduction
hide_table_of_contents: true
---

# Quota deduction

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Request-time Async Side Effects → Quota deduction`

> **中文解释：** 请求完成并计算 cost 后异步扣减 quota；属于请求结束后的副作用。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START / TRIGGER
│
├─ Trigger source
│    ├─ startup spawn / request-time tokio::spawn / manager restoration / channel message
│    └─ task: Quota deduction
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
│    ├─ execute Quota deduction
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
END / NEXT ITERATION
```


## 输入示例

> 后台任务通常没有 HTTP 请求体；这里把触发事件、队列/定时器和共享状态视为它的输入。

```text
trigger=Request-time Async Side Effects
job=Quota deduction
runtime=running
shared_state=available
# 该类页面的“输入”不是 HTTP body，而是启动事件、定时器、队列消息或请求侧异步事件。
```

## 返回结果示例

> 后台任务通常不会直接向 HTTP 调用方返回 JSON；这里用一条构造的状态/日志结果表示一次成功执行后的可观测结果。

```text
user_id=10001 cost=0.00042 quota_before=100.00000 quota_after=99.99958 status=success
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/router/src/lib.rs` | `create_router_app(), proxy_handler(), proxy_logic()` | Data Plane 主控制流或 Router internal handler | READ/WRITE router runtime |
| 2 | `crates/database/crates/router/src/token.rs` | `RouterTokenModel::*` | Router token/quota/key persistence | READ/WRITE router token state |
| 3 | `crates/router/src/balancer/mod.rs` | `RoundRobinBalancer::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 4 | `crates/router/src/limiter.rs` | `RateLimiter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 5 | `crates/router/src/circuit_breaker.rs` | `CircuitBreaker::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 6 | `crates/router/src/model_router.rs` | `ModelRouter::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 7 | `crates/router/src/channel_state.rs` | `ChannelStateTracker::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 8 | `crates/router/src/adaptor/factory.rs` | `DynamicAdaptorFactory::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 9 | `crates/router/src/adaptor/detector.rs` | `ApiVersionDetector::is_deprecation_error(), ApiVersionDetector::new()` | 由 create_router_app() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 10 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::empty(), PriceCache::load()` | 由 PriceCache::load() 直接调用；由 create_router_app() 直接调用 | CALL / runtime-specific |
| 11 | `crates/service/crates/billing/src/calculator.rs` | `CostCalculator::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 12 | `crates/router/src/exchange_rate.rs` | `ExchangeRateService::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 13 | `crates/router/src/scheduler/mod.rs` | `load_scheduler_config()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 14 | `crates/router/src/rate_budget.rs` | `BudgetGuard::new(), InMemoryBudget::new()` | 由 create_router_app() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 15 | `crates/router/src/price_sync.rs` | `PriceSyncService::new(), PriceSyncService::with_config(), start_price_sync_task()` | 由 create_router_app() 直接调用；由 start_price_sync_task() 直接调用 | CALL / runtime-specific |
| 16 | `crates/database/crates/router/src/lib.rs` | `RouterDatabase::deduct_quota(), RouterDatabase::insert_log(), RouterDatabase::insert_request_log(), RouterDatabase::update_token_accessed_time(), RouterDatabase::validate_token_and_get_info(), RouterDatabase::validate_token_detailed()` | 由 create_router_app() 直接调用；由 proxy_handler() 直接调用 | CALL / runtime-specific |
| 17 | `crates/router/src/channel_health_manager.rs` | `ChannelHealthManager::new()` | 由 create_router_app() 直接调用 | CALL / runtime-specific |
| 18 | `crates/router/src/passthrough.rs` | `build_gemini_passthrough_url(), extract_model_from_gemini_path(), should_passthrough()` | 由 proxy_handler() 直接调用；由 proxy_logic() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
