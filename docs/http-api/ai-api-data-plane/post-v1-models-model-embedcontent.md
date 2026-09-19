---
title: "POST /v1/models/{model}:embedContent"
slug: /http-api/ai-api-data-plane/post-v1-models-model-embedcontent
hide_table_of_contents: true
---

# POST /v1/models/&#123;model&#125;:embedContent

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → POST /v1/models/{model}:embedContent`

> **中文解释：** Gemini v1 embedContent；进入原生 passthrough。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: POST /v1/models/{model}:embedContent
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
│         ├─ YES（Management/Internal/LiveView 等）→ 对应 handler
│         └─ NO → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ Data Plane route selection
│    ├─ explicit /v1/models or usage routes checked first
│    └─ DECISION: explicit route matched?
│         ├─ YES → corresponding explicit handler
│         └─ NO  → proxy_handler()
│
├─ Path normalization + request identity
│    ├─ normalize_doubled_path()
│    ├─ preserve Method / URI / headers
│    ├─ request-id already attached by server middleware
│    └─ prepare AppState/runtime services
│
├─ Credential source selection
│    ├─ Candidate 1: Authorization: Bearer ...
│    ├─ Candidate 2: x-api-key
│    ├─ Candidate 3: x-goog-api-key
│    └─ DECISION: any supported credential exists?
│         ├─ NO  → HTTP 401 → END
│         └─ YES → token validation chain
│
├─ Token / user / group resolution
│    ├─ RouterDatabase new-token validation
│    ├─ DECISION: new token valid?
│    │    ├─ YES → token metadata / user_id / group / quota / policy
│    │    └─ NO  → legacy token validation
│    ├─ DECISION: legacy token valid?
│    │    ├─ YES → legacy metadata / user_id
│    │    └─ NO  → JWT fallback where supported
│    └─ DECISION: identity ultimately valid?
│         ├─ NO  → authorization error → END
│         └─ YES → continue
│

▼
FILE: crates/database/crates/router/src/token.rs
│
├─ Router token persistence backing validation/quota metadata
├─ validate current/legacy token state as invoked from RouterDatabase
└─ return token/user/group/quota/order metadata
│
▼
FILE: crates/router/src/lib.rs
│
├─ Account / quota guard
│    ├─ inspect quota/order metadata
│    └─ DECISION: quota exhausted / account cannot spend?
│         ├─ YES → HTTP 402 Payment Required → END
│         └─ NO  → continue
│
├─ Local request rate limiting
│    ├─ limiter key derived from authenticated request context
│    └─ DECISION: limiter allows request?
│         ├─ NO  → HTTP 429 Too Many Requests → END
│         └─ YES → continue
│
├─ Request-body acquisition
│    ├─ collect Axum body bytes
│    └─ DECISION: body read/size/parse boundary succeeds?
│         ├─ NO  → client/request error → END
│         └─ YES → immutable request payload for routing/adaptor
│
├─ Model + protocol context extraction
│    ├─ OpenAI/Anthropic: model usually from JSON body
│    ├─ Gemini: model may come from URL path
│    ├─ detect streaming / batch / priority hints
│    ├─ detect API protocol family
│    ├─ model 可能从 Gemini URL path 提取，而不是 JSON body
│    └─ DECISION: required model/context resolved?
│         ├─ NO  → invalid request / model resolution error → END
│         └─ YES → proxy_logic(...)
│
├─ Enter proxy_logic(...)
│    ├─ load scheduling policy for resolved user group
│    ├─ resolve requested model / model mapping
│    ├─ load candidate channel abilities
│    ├─ apply user/order/price constraints
│    └─ produce ordered/weighted candidate set
│

▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ UserService::resolve_traffic_class()
├─ TTL cache lookup
└─ cache miss → UserDatabase::get_user_roles()
│
▼
FILE: crates/database/crates/user/src/lib.rs
│
├─ read user roles used for TrafficColor classification
└─ return roles → UserService → proxy_logic
│
▼
FILE: crates/router/src/model_router.rs
│
├─ ModelRouter::route_with_scheduler()
├─ evaluate group/model/scheduler/request classification
├─ consult affinity / health / pricing inputs
└─ return ordered channel candidates（DYNAMIC result）
│
▼
FILE: crates/router/src/lib.rs
│
├─ Candidate eligibility filtering
│    ├─ ability enabled?
│    ├─ channel state allows traffic?
│    ├─ circuit breaker allows attempt?
│    ├─ rate budget / shaper allows attempt?
│    ├─ price/order constraints satisfied?
│    └─ DECISION: any candidate remains?
│         ├─ NO  → no-upstream / routing error → END
│         └─ YES → candidate attempt loop
│

▼
FILE: crates/service/crates/billing/src/cache.rs
│
├─ PriceCache supplies model/region pricing used by routing/billing
│
▼
FILE: crates/service/crates/billing/src/calculator.rs
│
├─ CostCalculator::preflight()
└─ DECISION: strict pricing requirement satisfied?
     ├─ NO → reject before upstream
     └─ YES → return to candidate execution
│
▼
FILE: crates/router/src/lib.rs
│
├─ Candidate attempt loop
│    ├─ select next candidate
│    ├─ acquire rate budget / shaping permission
│    ├─ consult circuit breaker
│    ├─ resolve protocol / API version
│    ├─ construct upstream URL + headers + credentials
│    └─ hand request to passthrough/adaptor boundary
│
▼
FILE: crates/router/src/passthrough.rs
│
├─ Protocol transformation boundary
│    ├─ inspect source protocol + target Channel protocol
│    └─ DECISION: native passthrough possible?
│         ├─ YES
│         │    ├─ preserve compatible body/headers semantics
│         │    └─ avoid unnecessary transform
│         └─ NO
│              └─ DynamicAdaptorFactory / adaptor conversion path
│                   └─ DYNAMIC: exact transformation depends on Provider adaptor
│
├─ Upstream network I/O
│    ├─ send HTTP request through shared client
│    ├─ wait for headers/body or stream
│    └─ DECISION: upstream attempt succeeds?
│         ├─ NO
│         │    ├─ classify failure
│         │    ├─ update channel/circuit feedback
│         │    ├─ optional API-version detect/update
│         │    └─ DECISION: another eligible candidate?
│         │         ├─ YES → 返回 Candidate attempt loop
│         │         └─ NO  → final upstream/routing error → END
│         └─ YES → response handling
│
▼
FILE: crates/router/src/lib.rs
│
├─ Response mode split
│    └─ DECISION: streaming response?
│         ├─ YES
│         │    ├─ stream chunks to client
│         │    ├─ collect/derive usage while stream progresses
│         │    └─ handle stream completion/disconnect
│         └─ NO
│              ├─ collect upstream body
│              └─ parse/derive usage metadata
│

▼
FILE: crates/service/crates/billing/src/usage/*
│
├─ provider-specific UsageParser extracts/normalizes usage
└─ return UnifiedUsage
│
▼
FILE: crates/service/crates/billing/src/calculator.rs
│
├─ CostCalculator::calculate()
├─ PriceCache + RequestOptions + UnifiedUsage
└─ return cost breakdown
│
▼
FILE: crates/database/crates/router/src/log.rs
│
├─ persistence backing RouterLog / RequestLog aggregation/writes
└─ async writers persist request accounting state
│
▼
FILE: crates/router/src/lib.rs
│
├─ Unified usage + cost
│    ├─ normalize prompt/input tokens
│    ├─ normalize completion/output tokens
│    ├─ endpoint-specific usage augmentation when needed
│    ├─ PriceCache / CostCalculator lookup
│    └─ CostCalculator::calculate()
│
├─ Accounting / persistence side effects
│    ├─ enqueue RouterLog
│    ├─ enqueue RequestLog according to storage policy
│    ├─ send AIMD/rate-budget feedback
│    ├─ update circuit/channel state feedback
│    ├─ async token accessed_time update where applicable
│    └─ DECISION: calculated cost > 0?
│         ├─ YES → async quota deduction
│         └─ NO  → no quota deduction task
│
├─ Endpoint-specific async side effects
│    ├─ none beyond common request side effects
│
├─ Final response construction
│    ├─ preserve/normalize upstream-compatible status + body
│    ├─ attach resolved channel/model diagnostic headers where configured
│    └─ return Axum Response
│
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: crates/router/src/lib.rs
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
│    │    ├─ normalize_doubled_path()
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
│    │    ├─ build_response_with_header()
│    │    ├─ inject_video_tokens_if_empty()
│    │    ├─ sanitize_request_body()
│    │    │    └─ CALL → redact_sensitive_fields() @ crates/router/src/lib.rs
│    │    │    └─ CALL → safe_cut() @ crates/router/src/lib.rs
│    │    ├─ sanitize_request_headers()
│    │    ├─ record_failover_attempt()
│    │    ├─ apply_header_override()
│    │    ├─ record_upstream_failure()
│    ├─ FILE: crates/service/crates/user/src/lib.rs
│    │    ├─ UserService::resolve_traffic_class()
│    │    │    └─ CALL → UserDatabase::get_user_roles() @ crates/database/crates/user/src/lib.rs
│    │    ├─ UserService::get_user_roles()
│    ├─ FILE: crates/router/src/model_router.rs
│    │    ├─ ModelRouter::route_with_scheduler()
│    │    │    └─ CALL → pick_hrw() @ crates/router/src/affinity.rs
│    │    │    └─ CALL → CombinedScheduler::new() @ crates/router/src/scheduler/combined.rs
│    │    │    └─ CALL → build_context() @ crates/router/src/scheduler/mod.rs
│    │    │    └─ CALL → rank_candidates() @ crates/router/src/scheduler/mod.rs
│    │    │    └─ CALL → rank_passthrough() @ crates/router/src/scheduler/mod.rs
│    ├─ FILE: crates/service/crates/billing/src/calculator.rs
│    │    ├─ CostCalculator::preflight()
│    │    ├─ CostCalculator::calculate()
│    ├─ FILE: crates/database/crates/router/src/lib.rs
│    │    ├─ RouterDatabase::validate_token_and_get_info()
│    │    ├─ RouterDatabase::update_token_accessed_time()
│    │    │    └─ CALL → RouterTokenModel::update_accessed_time() @ crates/database/crates/router/src/token.rs
│    │    ├─ RouterDatabase::validate_token_detailed()
│    │    │    └─ CALL → RouterTokenModel::validate_detailed() @ crates/database/crates/router/src/token.rs
│    │    ├─ RouterDatabase::deduct_quota()
│    ├─ FILE: crates/router/src/passthrough.rs
│    │    ├─ extract_model_from_gemini_path()
│    │    ├─ should_passthrough()
│    │    │    └─ CALL → is_gemini_native_path() @ crates/router/src/passthrough.rs
│    │    │    └─ CALL → is_gemini_native_content() @ crates/router/src/passthrough.rs
│    │    ├─ build_gemini_passthrough_url()
│    │    │    └─ CALL → is_gemini_native_path() @ crates/router/src/passthrough.rs
│    ├─ FILE: crates/database/crates/router/src/router_video_task.rs
│    │    ├─ RouterVideoTaskModel::get_by_task_id()
│    │    ├─ RouterVideoTaskModel::save()
│    ├─ FILE: crates/database/crates/channel/src/channel_provider.rs
│    │    ├─ ChannelProviderModel::get_by_id()
│    │    │    └─ CALL → ph() @ crates/database/src/placeholder.rs
│    ├─ FILE: crates/service/crates/billing/src/counter.rs
│    │    ├─ UnifiedTokenCounter::new()
│    ├─ FILE: crates/router/src/order_type.rs
│    │    ├─ OrderType::from_db_row()
│    └─ FILE: crates/router/src/rate_budget.rs
│    │    ├─ BudgetGuard::new()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
     └─ Client receives successful upstream-compatible response OR a terminal error from an earlier branch
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
POST /v1/models/gemini-embedding-example:embedContent HTTP/1.1
Host: api.burncloud.example
x-goog-api-key: bc_live_7d4e...example
Content-Type: application/json

{"content":{"parts":[{"text":"BurnCloud embedding"}]}}
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "embedding": {
    "values": [
      0.0182,
      -0.0711,
      0.0043,
      0.1128
    ]
  }
}
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/router/src/lib.rs` | `create_router_app(), proxy_handler(), proxy_logic()` | Data Plane 主控制流或 Router internal handler | READ/WRITE router runtime |
| 3 | `crates/database/crates/router/src/token.rs` | `RouterTokenModel::*` | Router token/quota/key persistence | READ/WRITE router token state |
| 4 | `crates/service/crates/user/src/lib.rs` | `UserService::*` | User/auth business service | SERVICE |
| 5 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::*` | User/role/recharge persistence | READ/WRITE user state |
| 6 | `crates/router/src/model_router.rs` | `model_router` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 7 | `crates/router/src/affinity.rs` | `affinity` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 8 | `crates/router/src/channel_state.rs` | `channel_state` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 9 | `crates/router/src/circuit_breaker.rs` | `circuit_breaker` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 10 | `crates/router/src/aimd_limiter.rs` | `aimd_limiter` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 11 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::*` | pricing lookup | READ price cache |
| 12 | `crates/service/crates/billing/src/calculator.rs` | `CostCalculator::preflight(), calculate()` | billing admission and settlement | READ price / compute cost |
| 13 | `crates/router/src/passthrough.rs` | `passthrough` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 14 | `crates/router/src/adaptor/*` | `DynamicAdaptorFactory / provider adaptor` | Cross-protocol request/response transformation | DYNAMIC Provider transform |
| 15 | `crates/service/crates/billing/src/usage/*` | `UsageParser::*` | Provider response usage normalization | READ response body/stream |
| 16 | `crates/database/crates/router/src/log.rs` | `RouterLogModel::* / usage & billing queries` | Request accounting / usage / billing persistence | READ/WRITE router_logs |
| 17 | `crates/database/crates/router/src/lib.rs` | `RouterDatabase::deduct_quota(), RouterDatabase::update_token_accessed_time(), RouterDatabase::validate_token_and_get_info(), RouterDatabase::validate_token_detailed()` | 由 proxy_handler() 直接调用 | CALL / runtime-specific |
| 18 | `crates/database/crates/router/src/router_video_task.rs` | `RouterVideoTaskModel::get_by_task_id(), RouterVideoTaskModel::save()` | 由 proxy_handler() 直接调用 | CALL / runtime-specific |
| 19 | `crates/database/crates/channel/src/channel_provider.rs` | `ChannelProviderModel::get_by_id()` | 由 proxy_handler() 直接调用 | CALL / runtime-specific |
| 20 | `crates/service/crates/billing/src/counter.rs` | `UnifiedTokenCounter::new()` | 由 proxy_handler() 直接调用 | CALL / runtime-specific |
| 21 | `crates/router/src/order_type.rs` | `OrderType::from_db_row()` | 由 proxy_logic() 直接调用 | CALL / runtime-specific |
| 22 | `crates/router/src/rate_budget.rs` | `BudgetGuard::new()` | 由 proxy_logic() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
