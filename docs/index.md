---
title: "BurnCloud"
slug: /
hide_table_of_contents: true
---

# 0. 一张图先看完整 BurnCloud

```text
BurnCloud
│
├── 1. HTTP / API
│   │
│   ├── AI API / Data Plane
│   │   ├── GET  /v1/models
│   │   ├── GET  /api/v1/usage
│   │   ├── GET  /api/v1/usage/models
│   │   ├── POST /v1/chat/completions
│   │   ├── POST /chat/completions
│   │   ├── POST /v1/completions
│   │   ├── POST /v1/embeddings
│   │   ├── POST /v1/messages
│   │   ├── POST /v1/video/generations
│   │   ├── GET  /v1/videos/{task_id}
│   │   ├── POST /v1beta/models/{model}:generateContent
│   │   ├── POST /v1beta/models/{model}:streamGenerateContent
│   │   ├── POST /v1beta/models/{model}:countTokens
│   │   ├── POST /v1beta/models/{model}:embedContent
│   │   ├── POST /v1/models/{model}:generateContent
│   │   ├── POST /v1/models/{model}:streamGenerateContent
│   │   ├── POST /v1/models/{model}:countTokens
│   │   ├── POST /v1/models/{model}:embedContent
│   │   └── Router fallback → proxy_handler
│   │
│   ├── Authentication
│   │   ├── POST /api/auth/register
│   │   ├── POST /api/auth/login
│   │   ├── POST /api/auth/forgot-password
│   │   ├── POST /api/auth/reset-password
│   │   ├── GET  /api/auth/google
│   │   └── GET  /api/auth/github
│   │
│   ├── Channel Management
│   │   ├── GET    /console/api/channel
│   │   ├── POST   /console/api/channel
│   │   ├── PUT    /console/api/channel
│   │   ├── GET    /console/api/channel/{id}
│   │   └── DELETE /console/api/channel/{id}
│   │
│   ├── Token
│   │   ├── GET    /console/api/tokens
│   │   ├── POST   /console/api/tokens
│   │   ├── GET    /console/api/tokens/{token}
│   │   ├── PUT    /console/api/tokens/{token}
│   │   ├── DELETE /console/api/tokens/{token}
│   │   ├── POST   /console/api/tokens/{token}/rotate
│   │   ├── POST   /console/api/tokens/{token}/revoke-old
│   │   └── POST   /console/api/tokens/{token}/ip-whitelist
│   │
│   ├── User
│   │   ├── POST /console/api/user/register
│   │   ├── POST /console/api/user/login
│   │   ├── POST /console/api/user/topup
│   │   ├── GET  /console/api/user/check_username
│   │   ├── GET  /console/api/user/recharges
│   │   └── GET  /console/api/list_users
│   │
│   ├── Billing / Usage
│   │   ├── GET /api/billing/summary
│   │   ├── GET /api/v1/usage
│   │   ├── GET /api/v1/usage/models
│   │   ├── GET /console/api/usage/{user_id}
│   │   └── GET /console/internal/billing/summary
│   │
│   ├── Logs
│   │   ├── GET /console/api/logs
│   │   ├── GET /console/api/usage/{user_id}
│   │   └── GET /console/internal/billing/summary
│   │
│   ├── Monitoring / Security
│   │   ├── GET  /console/api/monitor
│   │   ├── GET  /console/api/monitor/security
│   │   ├── GET  /console/api/monitor/security/events
│   │   ├── GET  /console/api/monitor/security/filters
│   │   ├── PUT  /console/api/monitor/security/filters
│   │   ├── POST /console/api/monitor/security/emergency-circuit-break
│   │   └── GET  /console/api/monitor/security/circuit-breaker-status
│   │
│   ├── Cache
│   │   ├── GET  /console/api/cache/stats
│   │   └── POST /console/api/cache/clear
│   │
│   ├── Admin / Internal
│   │   ├── GET  /health
│   │   ├── GET  /console/internal/health
│   │   ├── POST /console/internal/prices/sync
│   │   ├── POST /console/internal/circuit-breaker/trip-all
│   │   ├── GET  /console/internal/metrics
│   │   └── GET  /console/api/{*path} → protected 404 catch-all
│   │
│   ├── OpenAPI / Swagger
│   │   ├── GET /api-docs/openapi.json
│   │   ├── GET /swagger-ui
│   │   └── GET /swagger-ui/
│   │
│   └── Web UI / LiveView / WebSocket
│       ├── GET / 
│       ├── GET /home
│       ├── GET /login
│       ├── GET /register
│       ├── GET /forgot-password
│       ├── GET /reset-password
│       ├── GET /console
│       ├── GET /console/
│       ├── GET /console/{*path}
│       ├── GET /favicon.ico
│       ├── GET /preview/home
│       ├── GET /preview/login
│       ├── GET /preview/console
│       ├── GET /preview/console/
│       ├── GET /preview/console/{*path}
│       └── GET /ws
│
├── 2. CLI / Executables
│   │
│   ├── burncloud
│   │   ├── burncloud
│   │   ├── burncloud server
│   │   ├── burncloud router
│   │   ├── burncloud client
│   │   ├── burncloud update
│   │   │   └── --check-only
│   │   ├── burncloud install
│   │   │   ├── [software]
│   │   │   ├── --list
│   │   │   ├── --status
│   │   │   ├── --auto-deps
│   │   │   ├── --local PATH
│   │   │   └── --bundle DIR
│   │   ├── burncloud bundle
│   │   │   ├── create <software>
│   │   │   │   └── -o DIR
│   │   │   └── verify <bundle-dir>
│   │   ├── burncloud channel
│   │   │   ├── add
│   │   │   ├── list
│   │   │   ├── delete <id>
│   │   │   ├── show <id>
│   │   │   └── update <id>
│   │   ├── burncloud price
│   │   │   ├── list
│   │   │   ├── set <model>
│   │   │   ├── get <model>
│   │   │   ├── show <model>
│   │   │   ├── delete <model>
│   │   │   ├── sync-status
│   │   │   ├── import <file>
│   │   │   ├── export <file>
│   │   │   ├── validate <file>
│   │   │   └── sync
│   │   ├── burncloud tiered
│   │   │   ├── list-tiers <model>
│   │   │   ├── add-tier <model>
│   │   │   ├── import-tiered <file>
│   │   │   ├── delete-tiers <model>
│   │   │   └── check-tiered <model>
│   │   ├── burncloud token
│   │   │   ├── list
│   │   │   ├── create
│   │   │   ├── update <key>
│   │   │   └── delete <key>
│   │   ├── burncloud protocol
│   │   │   ├── list
│   │   │   ├── add
│   │   │   ├── delete <id>
│   │   │   ├── show <id>
│   │   │   └── test --channel-id <id>
│   │   ├── burncloud currency
│   │   │   ├── list-rates
│   │   │   ├── set-rate
│   │   │   ├── refresh
│   │   │   └── convert <amount>
│   │   ├── burncloud user
│   │   │   ├── register
│   │   │   ├── login
│   │   │   ├── list
│   │   │   ├── topup
│   │   │   ├── recharges
│   │   │   └── check-username
│   │   ├── burncloud log
│   │   │   ├── list
│   │   │   └── usage
│   │   └── burncloud monitor
│   │       ├── status
│   │       └── server
│   │
│   └── Workspace Binaries
│       ├── burncloud-client
│       ├── screenshot_gen
│       ├── burncloud-download
│       ├── burncloud-loop
│       │   ├── jobs-aesthetic
│       │   ├── css-optimize
│       │   ├── gate <name>
│       │   ├── gates <suite>
│       │   └── list-gates
│       ├── client-api
│       ├── client-shared
│       └── client-tray
│
├── 3. Background Jobs / Async Side Effects
│   │
│   ├── Long-running Jobs
│   │   ├── System Monitor Auto Update
│   │   │   └── periodic CPU / memory / disk refresh
│   │   ├── Price Sync
│   │   │   ├── initial sync
│   │   │   ├── periodic sync
│   │   │   ├── force-sync channel
│   │   │   └── PriceCache refresh
│   │   ├── Exchange Rate Sync
│   │   │   ├── DB reload
│   │   │   └── stale-rate check
│   │   ├── AIMD Budget Feedback
│   │   │   └── adaptive RPM budget feedback
│   │   ├── Async Router Log Writer
│   │   │   └── RouterLog persistence
│   │   └── Async Request Log Writer
│   │       └── detailed request/response persistence
│   │
│   ├── Request-time Async Side Effects
│   │   ├── Token accessed_time update
│   │   ├── Quota deduction
│   │   ├── Video task mapping save
│   │   └── API version detect / update
│   │
│   ├── Download Background Work
│   │   ├── Download progress monitor
│   │   │   └── aria2 status → DB progress
│   │   └── Restore incomplete downloads
│   │       └── active downloads → restart monitor
│   │
│   └── Desktop Background Work
│       ├── Windows tray thread
│       └── Show-window poll loop
│           └── visible / focus window
│
├── 4. Startup
│   │
│   ├── src/main.rs
│   │   ├── dotenv load
│   │   ├── ensure_master_key
│   │   ├── init_logging
│   │   └── command / platform dispatch
│   │       ├── server
│   │       ├── router
│   │       ├── client
│   │       ├── default Windows
│   │       ├── default non-Windows
│   │       └── management CLI
│   │
│   ├── start_server
│   │   ├── Database::new
│   │   ├── RouterDatabase::init
│   │   ├── UserDatabase::init
│   │   ├── create_app
│   │   ├── TcpListener::bind
│   │   └── axum::serve
│   │
│   ├── create_app
│   │   ├── SystemMonitorService
│   │   │   └── start_auto_update
│   │   ├── CacheService
│   │   │   └── optional Redis connection
│   │   ├── create_router_app
│   │   ├── AppState
│   │   ├── management API
│   │   │   ├── public auth routes
│   │   │   └── protected JWT routes
│   │   ├── GET /health
│   │   ├── Router Internal routes
│   │   ├── optional LiveView routes
│   │   └── fallback_service(data-plane router)
│   │
│   └── create_router_app
│       ├── reqwest::Client
│       ├── load balancer
│       ├── local rate limiter
│       ├── circuit breaker
│       ├── ModelRouter
│       ├── ChannelStateTracker
│       ├── DynamicAdaptorFactory
│       ├── API version detector
│       ├── PriceCache
│       ├── CostCalculator
│       ├── ExchangeRateService
│       │   ├── DB rate load
│       │   └── sync task
│       ├── scheduler policies
│       ├── affinity cache
│       ├── rate budget / channel caps
│       ├── billing strict mode
│       ├── request-log storage policy
│       ├── AIMD feedback channel / task
│       ├── Price Sync task
│       ├── RouterLog async writer
│       ├── RequestLog async writer
│       ├── Router Internal endpoints
│       ├── explicit /v1/models route
│       ├── explicit usage routes
│       └── proxy_handler fallback
│
└── 5. UI-only Actions
    │
    ├── Dioxus Route Tree
    │   │
    │   ├── Guest / Public
    │   │   ├── /
    │   │   ├── /home
    │   │   ├── /login
    │   │   ├── /register
    │   │   ├── /forgot-password
    │   │   └── /reset-password?:token
    │   │
    │   ├── Console
    │   │   ├── /console/dashboard
    │   │   ├── /console/deploy
    │   │   ├── /console/monitor
    │   │   ├── /console/access
    │   │   ├── /console/models
    │   │   ├── /console/users
    │   │   ├── /console/settings
    │   │   ├── /console/finance
    │   │   ├── /console/logs
    │   │   ├── /console/connect
    │   │   ├── /console/playground
    │   │   └── /console/:..segments → NotFoundPage
    │   │
    │   └── Debug / e2e-preview
    │       ├── /preview/home
    │       ├── /preview/login
    │       ├── /preview/console/dashboard
    │       ├── /preview/console/models
    │       ├── /preview/console/access
    │       ├── /preview/console/settings
    │       ├── /preview/console/finance
    │       ├── /preview/console/monitor
    │       └── /preview/console/playground
    │
    ├── Local UI State
    │   ├── i18n context
    │   ├── Toast state / ToastContainer
    │   ├── Auth context
    │   └── Theme state
    │
    └── Desktop UI-only Behavior
        ├── window maximize
        ├── Windows tray startup
        ├── show-window polling
        ├── window visible toggle
        └── window focus
```
