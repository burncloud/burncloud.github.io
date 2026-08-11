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
| 1 | `crates/router/src/lib.rs` | `见上方 E2E 对应函数/入口` | 该 CLI/UI/Background/Startup 页面真实执行文件 | runtime-specific |
| 2 | `crates/router/src/model_router.rs` | `ModelRouter::*` | scheduler/model route engine | INIT routing |
| 3 | `crates/router/src/circuit_breaker.rs` | `CircuitBreaker::*` | breaker state | INIT runtime state |
| 4 | `crates/router/src/affinity.rs` | `affinity cache` | session/channel affinity | INIT cache |
| 5 | `crates/router/src/channel_state.rs` | `channel state` | channel runtime state | INIT state |
| 6 | `crates/router/src/aimd_limiter.rs` | `AIMD limiter` | rate budget state | INIT state |
| 7 | `crates/router/src/price_sync.rs` | `start_price_sync_task()` | price sync background task | SPAWN |
| 8 | `crates/router/src/exchange_rate.rs` | `start_sync_task()` | exchange-rate background task | SPAWN |
| 9 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::*` | pricing cache | INIT/read |
| 10 | `crates/service/crates/billing/src/calculator.rs` | `CostCalculator::*` | billing calculation engine | INIT/use |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
