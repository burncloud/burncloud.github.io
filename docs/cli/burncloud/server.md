---
title: "server"
slug: /cli/burncloud/server
hide_table_of_contents: true
---

# server

**树路径：** `BurnCloud → CLI / Executables → burncloud → server`

> **中文解释：** 显式启动 Server 模式。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Shell / OS 入口
│    └─ burncloud server
│    └─ 显式 Server 模式；当前实现同时 enable_liveview=true
│
▼
FILE: src/main.rs
│
├─ main()
│    ├─ dotenvy::dotenv().ok()
│    ├─ ensure_master_key()
│    │    ├─ is_valid_master_key()
│    │    │    ├─ env::var("MASTER_KEY")
│    │    │    ├─ hex::decode(...)
│    │    │    └─ DECISION: decoded key length == 32 bytes?
│    │    │         ├─ YES → keep existing key
│    │    │         └─ NO  → generate replacement
│    │    ├─ rand::random::<[u8;32]>()
│    │    ├─ hex::encode()
│    │    ├─ resolve .env path from CWD / current_exe()
│    │    ├─ read_to_string() when file exists
│    │    ├─ fs::write(.env)
│    │    └─ env::set_var("MASTER_KEY", ...)
│    ├─ env::args().collect()
│    ├─ is_server = args[1] in [server, router, client]
│    └─ burncloud_server::logging::init_logging()
│
▼
FILE: crates/server/src/logging.rs
│
├─ init_logging()
│    ├─ LOG_DIR / LOG_MAX_FILES / RUST_LOG
│    ├─ fs::create_dir_all(log_dir)
│    ├─ tracing_log::LogTracer::init()
│    ├─ file_appender(server/service/database/router)
│    │    └─ RollingFileAppender::builder() → non_blocking(...)
│    ├─ module_filter(...)
│    └─ tracing::subscriber::set_global_default(...)
│
▼
FILE: src/main.rs
│
├─ match args.as_slice()
│    └─ DECISION: subcommand == "server" OR "router"?
│         ├─ NO  → other direct/CLI branch
│         └─ YES → run_async_server()
│
├─ run_async_server() #[tokio::main]
│    ├─ HOST env or "127.0.0.1"
│    ├─ PORT env or DEFAULT_PORT
│    └─ burncloud_server::start_server(host, port, true)
│
├─ IMPORTANT
│    ├─ 当前源码中 `server` 与 `router` 都走同一个 run_async_server()
│    └─ 此 direct branch 不进入 Clap CLI dispatch
│
▼
FILE: crates/server/src/lib.rs
│
├─ start_server(host, port, enable_liveview=true)
│    ├─ create_default_database().await
│    ├─ RouterDatabase::init(&db).await
│    ├─ UserDatabase::init(&db).await
│    ├─ create_app(db, true).await
│    ├─ SocketAddr::parse()
│    ├─ TcpListener::bind(addr).await
│    └─ axum::serve(listener, app).await
│
▼
FILE: crates/database/src/database.rs
│
├─ create_default_database() → Database::new()
├─ Database::new()
│    ├─ DECISION: BURNCLOUD_DATABASE_URL exists?
│    │    ├─ YES → use configured URL
│    │    └─ NO
│    │         ├─ get_default_database_path()
│    │         ├─ create_directory_if_not_exists()
│    │         ├─ DECISION: BURNCLOUD_FRESH_DB == "1" and DB exists?
│    │         │    ├─ YES → fs::remove_file(default DB)
│    │         │    └─ NO  → preserve DB
│    │         └─ build sqlite://...?...mode=rwc
│    └─ Database::initialize().await
│
├─ Database::initialize()
│    ├─ sqlx::any::install_default_drivers()
│    ├─ DatabaseConnection::new(database_url)
│    │    ├─ AnyConnectOptions::from_str()
│    │    └─ AnyPoolOptions::new().max_connections(10).connect_with(...)
│    ├─ DECISION: db.kind() == sqlite?
│    │    └─ YES → PRAGMA journal_mode=WAL
│    ├─ MigrationRunner::run(self)
│    └─ Schema::init(self)
│
▼
FILE: crates/database/src/migration/mod.rs
│
├─ MigrationRunner::run()
│    ├─ ensure _schema_migrations table
│    ├─ choose SQLite / PostgreSQL migration catalogue
│    ├─ inspect already-applied versions
│    └─ execute pending versioned DDL migrations
│
▼
FILE: crates/database/src/schema/mod.rs
│
├─ Schema::init()
│    ├─ rename::migrate_table_renames()
│    ├─ router::migrate_router_logs()
│    ├─ price::migrate_prices()
│    └─ user::migrate_users_and_seed()
│
▼
FILE: crates/server/src/lib.rs
│
└─ start_server() continues → RouterDatabase::init(&db)
│
▼
FILE: crates/database/crates/router/src/lib.rs
│
├─ RouterDatabase::init()
│    ├─ db.get_connection()
│    ├─ db.kind()
│    ├─ CREATE TABLE IF NOT EXISTS router_tokens
│    └─ SQLite-only compatibility ALTER TABLE statements
│
▼
FILE: crates/server/src/lib.rs
│
└─ start_server() continues → UserDatabase::init(&db)
│
▼
FILE: crates/database/crates/user/src/lib.rs
│
├─ UserDatabase::init()
│    ├─ CREATE / verify user_roles
│    ├─ CREATE / verify user_role_bindings
│    ├─ CREATE / verify user_recharges
│    ├─ SQLite/PostgreSQL compatibility migrations
│    ├─ SELECT COUNT(*) FROM user_roles
│    ├─ DECISION: no roles exist?
│    │    └─ YES → seed admin/user roles
│    ├─ query users without role bindings
│    └─ assign_role(...) for orphan users when required
│
▼
FILE: crates/server/src/lib.rs
│
├─ create_app(db, enable_liveview=true)
│    ├─ SystemMonitorService::new()
│    ├─ monitor.start_auto_update().await
│    ├─ CacheService::new().await
│    ├─ cache.is_available().await
│    ├─ create_router_app(db.clone()).await
│    ├─ UserService::new()
│    ├─ api::routes(state.clone())
│    ├─ build /health + merge Management/Internal routers
│    ├─ DECISION: enable_liveview?
│    │    └─ YES → burncloud_client::liveview_router(db.clone()) → merge
│    ├─ fallback_service(router_app)
│    └─ SetRequestId / PropagateRequestId / Trace / CORS layers
│
▼
FILE: crates/service/crates/monitor/src/service.rs
│
├─ SystemMonitorService::new()
├─ start_auto_update()
│    └─ tokio::spawn
│         └─ LOOP interval(1s)
│              └─ collect_metrics_internal()
│                   ├─ CpuCollector::collect()
│                   ├─ MemoryCollector::collect()
│                   └─ DiskCollector::collect_all()
│
▼
FILE: crates/service/crates/cache/src/service.rs
│
├─ CacheService::new() → with_config(CacheConfig::default())
├─ DECISION: CACHE_ENABLED?
│    ├─ NO  → return disabled cache
│    └─ YES
│         ├─ require REDIS_URL
│         ├─ redis::Client::open()
│         ├─ get_connection_manager().await
│         └─ PING
│
▼
FILE: crates/router/src/lib.rs
│
├─ create_router_app(db)
│    ├─ reqwest::Client::builder() + timeouts/pool settings
│    ├─ RoundRobinBalancer::new()
│    ├─ RateLimiter::new(100, 10)
│    ├─ CircuitBreaker::new(...)
│    ├─ ModelRouter::new(db.clone())
│    ├─ ChannelStateTracker::new()
│    ├─ DynamicAdaptorFactory::new(db.clone())
│    ├─ ApiVersionDetector::new(db.clone())
│    ├─ PriceCache::load(&db).await
│    │    └─ DECISION: load fails? → PriceCache::empty()
│    ├─ CostCalculator::new(price_cache.clone())
│    ├─ ExchangeRateService::new(db.clone())
│    ├─ load_rates_from_db().await
│    ├─ tokio::spawn → ExchangeRateService::start_sync_task()
│    ├─ scheduler::load_scheduler_config()
│    ├─ AffinityCache::default()
│    ├─ InMemoryBudget::new()
│    ├─ configure_rate_budget_from_db(...).await
│    ├─ read BILLING_STRICT_MODE
│    ├─ read REQUEST_LOG_STORAGE_POLICY
│    ├─ tokio::spawn → AIMD budget-update consumer
│    ├─ price_sync::start_price_sync_task(...)
│    ├─ tokio::spawn → RouterLog writer → RouterDatabase::insert_log()
│    ├─ tokio::spawn → RequestLog writer → RouterDatabase::insert_request_log()
│    ├─ ChannelHealthManager::new()
│    ├─ build internal_app routes
│    │    ├─ /console/internal/health
│    │    ├─ /console/internal/prices/sync
│    │    ├─ /console/internal/circuit-breaker/trip-all
│    │    └─ /console/internal/metrics
│    └─ build data-plane app
│         ├─ GET /v1/models → models_handler [REGISTER ONLY]
│         ├─ GET /api/v1/usage → usage_handler [REGISTER ONLY]
│         ├─ GET /api/v1/usage/models → usage_models_handler [REGISTER ONLY]
│         └─ fallback(proxy_handler) [REGISTER ONLY]
│
├─ IMPORTANT: 上述 Handler 在启动时只被注册；收到对应 HTTP 请求后才执行
│
▼
FILE: crates/service/crates/billing/src/cache.rs
│
├─ PriceCache::load(db)
│    ├─ PriceCache::empty()
│    └─ refresh(db)
│         └─ BillingPriceModel::list(...)
│
▼
FILE: crates/router/src/exchange_rate.rs
│
├─ ExchangeRateService::new()
├─ load_rates_from_db()
└─ start_sync_task()
     └─ tokio::spawn hourly loop
│
▼
FILE: crates/router/src/price_sync.rs
│
├─ start_price_sync_task(...)
│    └─ tokio::spawn
│         ├─ PriceSyncService::new()/with_config()
│         ├─ startup sync_all(false) unless SKIP_INITIAL_PRICE_SYNC
│         └─ LOOP select(periodic tick, force-sync receiver)
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ api::routes(state)
│    ├─ auth::public_routes() [REGISTER]
│    ├─ auth::protected_routes() [REGISTER]
│    ├─ billing::routes() [REGISTER]
│    ├─ channel::routes() [REGISTER]
│    ├─ token::routes() [REGISTER]
│    ├─ log::routes() [REGISTER]
│    ├─ monitor::routes() [REGISTER]
│    ├─ user::routes() [REGISTER]
│    ├─ security::security_routes() [REGISTER]
│    ├─ openapi::routes() [REGISTER]
│    ├─ cache::routes() [REGISTER]
│    └─ auth_middleware layered over protected router [REGISTER]
│
├─ IMPORTANT: routes() 函数在启动期执行；具体 HTTP Handler 此刻不执行
│
▼
FILE: crates/client/src/lib.rs
│
├─ liveview_router(db)
│    ├─ LiveViewPool::new()
│    ├─ register HTML shell routes /, /home, /login, /register, ...
│    ├─ register /console and /console/*
│    ├─ register /favicon.ico
│    └─ register WS_PATH
│         └─ app::App is passed as future WebSocket-session callback [REGISTER ONLY]
│
▼
FILE: crates/server/src/lib.rs
│
├─ create_app() returns Unified Router
├─ SocketAddr::parse(host:port)
├─ TcpListener::bind(addr).await
├─ axum::serve(listener, app).await
│
└─ LONG-RUNNING STATE
     ├─ HTTP listener waits for Management / Internal / Data Plane / LiveView traffic
     ├─ monitor updater keeps running
     ├─ exchange-rate task keeps running
     ├─ price-sync task keeps running
     ├─ AIMD feedback consumer keeps running
     ├─ RouterLog writer keeps running
     └─ RequestLog writer keeps running
│
▼
END = server shutdown or fatal serve error
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ burncloud server
```

## 返回结果示例

> 以下采用源码真实 tracing 文案；示例按未设置 HOST/PORT 时的默认值 `127.0.0.1:3000` 展示。时间戳、日志级别和 target 由 tracing formatter 决定。

```text
Unified Gateway listening on 127.0.0.1:3000
- Dashboard: http://127.0.0.1:3000/
- LLM API:   http://127.0.0.1:3000/v1/...

# 随后 axum::serve 持续运行，命令不会立即返回到 Shell。
```


## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `main(), is_valid_master_key(), ensure_master_key(), run_async_server()` | 真实 direct-mode 分发；server/router 不经过 Clap | PROCESS / ENV / filesystem |
| 2 | `crates/server/src/logging.rs` | `init_logging(), file_appender(), module_filter()` | main() 在 direct mode 分发前初始化 tracing | INIT logs/files |
| 3 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 Server 启动与 Axum App composition | INIT DB/router/listener |
| 4 | `crates/database/src/database.rs` | `create_default_database(), Database::new(), Database::initialize(), DatabaseConnection::new(), get_default_database_path()` | start_server() 的数据库创建与连接主链 | READ ENV / WRITE DB file / CONNECT |
| 5 | `crates/database/src/migration/mod.rs` | `MigrationRunner::run()` | Database::initialize() 执行版本化 DDL migration | READ/WRITE schema |
| 6 | `crates/database/src/schema/mod.rs` | `Schema::init(), rename/router/price/user migration calls` | MigrationRunner 后执行数据修复和 seed | READ/WRITE database |
| 7 | `crates/database/crates/router/src/lib.rs` | `RouterDatabase::init(), RouterDatabase::insert_log(), RouterDatabase::insert_request_log()` | 启动建表兼容 + 后台日志 writer 的 DB facade | READ/WRITE router state |
| 8 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::init(), assign_role()` | 启动用户/角色表初始化及 orphan role 修复 | READ/WRITE user state |
| 9 | `crates/service/crates/monitor/src/service.rs` | `SystemMonitorService::new(), start_auto_update(), collect_metrics_internal()` | create_app() 初始化并启动系统指标后台采集 | SPAWN / READ OS / WRITE cache |
| 10 | `crates/service/crates/cache/src/service.rs` | `CacheService::new(), with_config(), is_available()` | create_app() 初始化可选 Redis cache | NETWORK Redis / cache state |
| 11 | `crates/router/src/lib.rs` | `create_router_app(), configure_rate_budget_from_db()` | 构造 Data Plane runtime、internal routes 和多条后台任务 | INIT/SPAWN router runtime |
| 12 | `crates/router/src/balancer/mod.rs` | `RoundRobinBalancer::new()` | create_router_app() 构造 balancer | INIT memory state |
| 13 | `crates/router/src/limiter.rs` | `RateLimiter::new()` | create_router_app() 构造本地 token-bucket limiter | INIT memory state |
| 14 | `crates/router/src/circuit_breaker.rs` | `CircuitBreaker::new()` | create_router_app() 构造 circuit breaker | INIT breaker state |
| 15 | `crates/router/src/model_router.rs` | `ModelRouter::new()` | create_router_app() 构造模型/渠道路由器 | INIT router DB handle |
| 16 | `crates/router/src/channel_state.rs` | `ChannelStateTracker::new()` | create_router_app() 构造运行态 Channel state tracker | INIT memory state |
| 17 | `crates/router/src/adaptor/factory.rs` | `DynamicAdaptorFactory::new()` | create_router_app() 构造动态协议 adaptor factory | INIT adaptor cache/DB |
| 18 | `crates/router/src/adaptor/detector.rs` | `ApiVersionDetector::new()` | create_router_app() 构造 API version detector | INIT DB handle |
| 19 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::load(), refresh(), empty()` | Router 启动加载模型价格 cache | READ billing_prices / WRITE memory cache |
| 20 | `crates/service/crates/billing/src/calculator.rs` | `CostCalculator::new()` | Router 启动构造计费计算器 | INIT billing runtime |
| 21 | `crates/router/src/exchange_rate.rs` | `ExchangeRateService::new(), load_rates_from_db(), start_sync_task()` | Router 启动加载汇率并启动 hourly task | READ DB / SPAWN |
| 22 | `crates/router/src/scheduler/mod.rs` | `load_scheduler_config()` | Router 启动读取 SCHEDULER_POLICIES | READ ENV / INIT policy map |
| 23 | `crates/router/src/affinity.rs` | `AffinityCache::default()` | Router 启动构造 L3 affinity cache | INIT memory cache |
| 24 | `crates/router/src/rate_budget.rs` | `InMemoryBudget::new(), configure()` | Router 启动构造 L2 Shaper budget | INIT/WRITE memory budget |
| 25 | `crates/router/src/price_sync.rs` | `start_price_sync_task(), PriceSyncService::new(), sync_all()` | Router 启动 price-sync background worker | SPAWN / NETWORK / WRITE price DB/cache |
| 26 | `crates/router/src/channel_health_manager.rs` | `ChannelHealthManager::new()` | Router AppState 构造健康管理器 | INIT health state |
| 27 | `crates/service/crates/user/src/lib.rs` | `UserService::new()` | create_app() 构造 Management user service | INIT auth/user service |
| 28 | `crates/server/src/api/mod.rs` | `routes()` | create_app() 构造 Public/Protected Management Router | REGISTER routes only |
| 29 | `crates/server/src/api/auth.rs` | `public_routes(), protected_routes()` | api::routes() 启动期注册 auth routes | REGISTER handlers only |
| 30 | `crates/server/src/api/billing.rs` | `routes()` | api::routes() 启动期注册 billing route | REGISTER handler only |
| 31 | `crates/server/src/api/channel.rs` | `routes()` | api::routes() 启动期注册 channel routes | REGISTER handlers only |
| 32 | `crates/server/src/api/token.rs` | `routes()` | api::routes() 启动期注册 token routes | REGISTER handlers only |
| 33 | `crates/server/src/api/log.rs` | `routes()` | api::routes() 启动期注册 log/usage routes | REGISTER handlers only |
| 34 | `crates/server/src/api/monitor.rs` | `routes()` | api::routes() 启动期注册 monitor route | REGISTER handler only |
| 35 | `crates/server/src/api/user.rs` | `routes()` | api::routes() 启动期注册 user routes | REGISTER handlers only |
| 36 | `crates/server/src/api/security.rs` | `security_routes()` | api::routes() 启动期注册 security routes | REGISTER handlers only |
| 37 | `crates/server/src/api/openapi.rs` | `routes()` | api::routes() 启动期注册 OpenAPI/Swagger routes | REGISTER handlers only |
| 38 | `crates/server/src/api/cache.rs` | `routes()` | api::routes() 启动期注册 cache routes | REGISTER handlers only |
| 39 | `crates/client/src/lib.rs` | `liveview_router()` | enable_liveview=true 时构造 HTML shell/WebSocket Router；App callback 仅注册 | REGISTER LiveView routes |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + BRANCH-SENSITIVE DIRECT MODE** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
