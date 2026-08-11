---
title: "GET /v1/models"
slug: /http-api/ai-api-data-plane/get-v1-models
hide_table_of_contents: true
---

# GET /v1/models

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → GET /v1/models`

> 单页只保留一张完整文本 E2E 图。排版只依赖左侧 `│ / ├─ / └─ / ▼`，不依赖中文宽度、右侧边框或空格对齐。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Actor
│    └─ User / OpenAI SDK / curl / AI Client
│
├─ HTTP Request
│    ├─ Method: GET
│    └─ Path: /v1/models
│
▼
FILE: crates/server/src/lib.rs
│
├─ start_server()
│    ├─ create_default_database()
│    ├─ RouterDatabase::init()
│    ├─ UserDatabase::init()
│    ├─ create_app(db, enable_liveview)
│    ├─ TcpListener::bind(host:port)
│    └─ axum::serve(listener, app)
│
├─ create_app()
│    │
│    ├─ Server startup state
│    │    ├─ SystemMonitorService::new()
│    │    ├─ start_auto_update()
│    │    ├─ CacheService::new()
│    │    └─ create_router_app(db)
│    │
│    ├─ Build Unified Axum App
│    │    ├─ GET /health
│    │    ├─ merge Management API
│    │    ├─ merge Router Internal API
│    │    ├─ merge LiveView Router (optional)
│    │    └─ fallback_service(router_app)
│    │
│    └─ Global middleware
│         ├─ CORS
│         ├─ TraceLayer
│         ├─ SetRequestIdLayer
│         └─ PropagateRequestIdLayer
│
├─ DECISION: Unified App already has a higher-priority route match?
│    │
│    ├─ YES
│    │    └─ Enter matched /health / Management / Internal / LiveView handler
│    │         └─ END for that other request path
│    │
│    └─ NO
│         └─ GET /v1/models falls through to fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ create_router_app()
│    │
│    └─ Data Plane routes
│         ├─ GET /v1/models
│         │    └─ models_handler
│         ├─ GET /api/v1/usage
│         ├─ GET /api/v1/usage/models
│         └─ fallback
│              └─ proxy_handler
│
├─ DECISION: Method + Path == GET /v1/models ?
│    │
│    ├─ YES
│    │    └─ models_handler(State<AppState>)
│    │
│    └─ NO
│         ├─ Match another explicit Data Plane route
│         └─ Or enter proxy_handler fallback
│
├─ IMPORTANT: this request does NOT enter proxy_handler
│
├─ NOT EXECUTED on this endpoint
│    ├─ Authorization Header parsing
│    ├─ API Token validation
│    ├─ JWT validation
│    ├─ User resolution
│    ├─ Group resolution
│    ├─ Quota check
│    ├─ Local rate limiter
│    ├─ ModelRouter
│    ├─ Scheduler
│    ├─ Affinity
│    ├─ Rate Budget / Shaper
│    ├─ Circuit Breaker
│    ├─ Billing preflight
│    ├─ Provider adaptor
│    └─ Upstream AI Provider
│
├─ models_handler()
│    │
│    ├─ model_entries = []
│    │
│    ├─ current_time
│    │    ├─ SystemTime::now()
│    │    └─ duration_since(UNIX_EPOCH)
│    │
│    ├─ DECISION: UNIX time conversion successful?
│    │    │
│    │    ├─ YES
│    │    │    └─ current_time = duration.as_secs()
│    │    │
│    │    └─ NO
│    │         └─ unwrap_or_default()
│    │              └─ current_time = 0
│    │
│    └─ CALL
│         └─ ChannelAbilityModel::list_distinct_models(&state.db)
│
▼
FILE: crates/database/crates/channel/src/channel_ability.rs
│
├─ ChannelAbilityModel::list_distinct_models(db)
│    │
│    ├─ db.get_connection()
│    │
│    ├─ DECISION: database connection acquired?
│    │    │
│    │    ├─ NO
│    │    │    └─ return Err
│    │    │
│    │    └─ YES
│    │         └─ conn.pool()
│    │
│    ├─ SQL
│    │
│    │    SELECT DISTINCT model
│    │    FROM channel_abilities
│    │    WHERE enabled = 1
│    │    ORDER BY model;
│    │
│    ├─ sqlx::query_as(sql)
│    │    └─ fetch_all(pool).await
│    │
│    ├─ DECISION: SQL query successful?
│    │    │
│    │    ├─ NO
│    │    │    └─ return Err
│    │    │
│    │    └─ YES
│    │         ├─ receive Vec<(String,)>
│    │         ├─ map tuple → model String
│    │         └─ return Ok(Vec<String>)
│    │
│    └─ CURRENT MODEL VISIBILITY LOGIC
│         ├─ checks: enabled = 1
│         ├─ applies: DISTINCT model
│         ├─ applies: ORDER BY model
│         ├─ does NOT filter current user
│         ├─ does NOT filter current group
│         ├─ does NOT JOIN channel_providers
│         ├─ does NOT check channel status
│         ├─ does NOT check channel health
│         ├─ does NOT check circuit breaker
│         ├─ does NOT check RPM / TPM capacity
│         ├─ does NOT check quota
│         └─ does NOT check price / price cap
│
▼
FILE: crates/router/src/lib.rs
│
├─ Back to models_handler()
│
├─ DECISION: list_distinct_models() returned Ok?
│    │
│    ├─ NO / Err
│    │    ├─ error is not returned to HTTP layer
│    │    ├─ if let Ok(...) body is skipped
│    │    └─ model_entries remains []
│    │
│    └─ YES
│         └─ models = Vec<String>
│
├─ DECISION: models is empty?
│    │
│    ├─ YES
│    │    └─ model_entries remains []
│    │
│    └─ NO
│         └─ FOR EACH model
│              │
│              ├─ Build model JSON object
│              │    ├─ id         = model
│              │    ├─ object     = "model"
│              │    ├─ created    = current_time
│              │    ├─ owned_by   = "burncloud"
│              │    ├─ permission = []
│              │    ├─ root       = model
│              │    └─ parent     = null
│              │
│              ├─ push into model_entries
│              │
│              └─ DECISION: another model remains?
│                   ├─ YES → continue loop
│                   └─ NO  → exit loop
│
├─ Build response_json
│
│    {
│      "object": "list",
│      "data": model_entries
│    }
│
├─ serde_json::to_string(response_json)
│
├─ DECISION: JSON serialization successful?
│    │
│    ├─ YES
│    │    └─ use serialized JSON body
│    │
│    └─ NO
│         └─ fallback body
│
│              {"object":"list","data":[]}
│
├─ build_response_with_header()
│    ├─ StatusCode::OK
│    ├─ content-type = application/json
│    └─ Body::from(json)
│
├─ Response::builder()
│    ├─ status(200)
│    ├─ header(content-type)
│    └─ body(body)
│
├─ DECISION: first Response builder successful?
│    │
│    ├─ YES
│    │    └─ return HTTP 200 + JSON body
│    │
│    └─ NO
│         └─ retry Response::builder()
│              ├─ status(200)
│              └─ empty body
│
├─ DECISION: second Response builder successful?
│    │
│    ├─ YES
│    │    └─ return HTTP 200 + empty body
│    │
│    └─ NO
│         └─ Response::new(Body::empty())
│
▼
END
│
├─ HTTP Response returned to User / SDK
│
└─ Final business meaning
     │
     ├─ Normal case
     │    └─ Return DISTINCT model names from channel_abilities
     │         where enabled = 1
     │
     ├─ Important semantic limitation
     │    └─ "enabled ability exists"
     │         ├─ does NOT mean current user can use it
     │         ├─ does NOT mean provider is healthy
     │         └─ does NOT mean routing will succeed now
     │
     └─ Important failure behavior
          ├─ database connection failure
          ├─ SQL query failure
          └─ truly no enabled models
               │
               └─ may all appear to client as

                    HTTP 200
                    {"object":"list","data":[]}
```

## 穿过的源码文件

| 顺序 | 文件 | 关键执行点 |
|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server()` → `create_app()` → `fallback_service(router_app)` |
| 2 | `crates/router/src/lib.rs` | `create_router_app()` → `GET /v1/models` → `models_handler()` → `build_response_with_header()` |
| 3 | `crates/database/crates/channel/src/channel_ability.rs` | `ChannelAbilityModel::list_distinct_models()` → SQL → `channel_abilities` |

**Execution classification: STATIC CONFIRMED** — 上面的入口、文件、函数、SQL 和判断均由当前 BurnCloud 源码直接确认。
