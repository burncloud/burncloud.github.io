from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MANIFEST = DOCS / "atlas-manifest.json"
FLOW_RE = re.compile(r"(## End-to-End Request Flow \+ ICFG\n\n)```text\n.*?\n```", re.S)
SOURCE_MARKER = "\n## 穿过的源码文件\n"


def block(body: str) -> str:
    return "```text\n" + body.rstrip() + "\n```"


def http_block(body: str) -> str:
    return "```http\n" + body.rstrip() + "\n```"


def json_block(body: str) -> str:
    return "```json\n" + body.rstrip() + "\n```"


def phase(n, name):
    return f"[PHASE {n:02d}] {name}"


def source_file_for_group(group: str, entry: str) -> str:
    if group == "Channel Management": return "crates/server/src/api/channel.rs"
    if group == "Token": return "crates/server/src/api/token.rs"
    if group == "User": return "crates/server/src/api/user.rs"
    if group == "Logs": return "crates/server/src/api/log.rs"
    if group == "Cache": return "crates/server/src/api/cache.rs"
    if group == "Monitoring / Security":
        return "crates/server/src/api/monitor.rs" if entry == "GET /console/api/monitor" else "crates/server/src/api/security.rs"
    if group == "Billing / Usage":
        return "crates/server/src/api/billing.rs" if entry == "GET /api/billing/summary" else "crates/server/src/api/log.rs"
    return "crates/server/src/api/mod.rs"


HANDLERS = {
    "POST /api/auth/register": "create_user",
    "POST /api/auth/login": "login",
    "POST /api/auth/forgot-password": "forgot_password",
    "POST /api/auth/reset-password": "reset_password",
    "GET /api/auth/google": "oauth_google",
    "GET /api/auth/github": "oauth_github",
    "GET /console/api/channel": "list_channels",
    "POST /console/api/channel": "create_channel",
    "PUT /console/api/channel": "update_channel",
    "GET /console/api/channel/{id}": "get_channel",
    "DELETE /console/api/channel/{id}": "delete_channel",
    "GET /console/api/tokens": "list_tokens",
    "POST /console/api/tokens": "create_token",
    "GET /console/api/tokens/{token}": "get_token",
    "PUT /console/api/tokens/{token}": "update_token",
    "DELETE /console/api/tokens/{token}": "delete_token",
    "POST /console/api/tokens/{token}/rotate": "rotate_token",
    "POST /console/api/tokens/{token}/revoke-old": "revoke_old_key",
    "POST /console/api/tokens/{token}/ip-whitelist": "set_ip_whitelist",
    "POST /console/api/user/register": "register",
    "POST /console/api/user/login": "login",
    "POST /console/api/user/topup": "topup",
    "GET /console/api/user/check_username": "check_username",
    "GET /console/api/user/recharges": "list_recharges",
    "GET /console/api/list_users": "list_users",
    "GET /api/billing/summary": "billing_summary_handler",
    "GET /console/api/logs": "list_logs",
    "GET /console/api/usage/{user_id}": "get_user_usage",
    "GET /console/internal/billing/summary": "billing_summary_handler",
    "GET /console/api/monitor": "get_system_metrics",
    "GET /console/api/monitor/security": "security_summary",
    "GET /console/api/monitor/security/events": "security_events",
    "GET /console/api/monitor/security/filters": "security_filters_get",
    "PUT /console/api/monitor/security/filters": "security_filters_put",
    "POST /console/api/monitor/security/emergency-circuit-break": "security_emergency_circuit_break",
    "GET /console/api/monitor/security/circuit-breaker-status": "security_circuit_breaker_status",
    "GET /console/api/cache/stats": "stats",
    "POST /console/api/cache/clear": "clear",
    "GET /console/internal/health": "health_status_handler",
    "POST /console/internal/prices/sync": "price_sync_handler",
    "POST /console/internal/circuit-breaker/trip-all": "circuit_breaker_trip_all_handler",
    "GET /console/internal/metrics": "metrics_handler",
    "GET /api-docs/openapi.json": "openapi_json",
    "GET /swagger-ui": "swagger_ui",
    "GET /swagger-ui/": "swagger_ui",
}


def common_http_prefix(entry: str) -> str:
    return f"""START
│
├─ {phase(0, '调用方与输入边界')}
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: {entry}
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
├─ {phase(1, '统一 HTTP Server')}
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
├─ {phase(2, '顶层 Route 决策')}
│    └─ DECISION: Unified App 是否已有显式/合并路由命中当前 Method + Path?
"""


def flow_models(entry):
    return common_http_prefix(entry) + """│         ├─ YES（其它顶层 route）→ 进入对应 handler；本页路径结束
│         └─ NO（/v1/models）→ fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 03] Data Plane route match
│    ├─ create_router_app() 已注册显式 GET /v1/models
│    └─ DECISION: Method == GET AND Path == /v1/models ?
│         ├─ NO  → 其它显式 usage route 或 proxy_handler fallback
│         └─ YES → models_handler(State<AppState>)
│
├─ [PHASE 04] Authentication / authorization boundary
│    ├─ 当前 handler 不读取 Authorization
│    ├─ 不调用 Token/JWT validation
│    ├─ 不解析 user_id / group
│    └─ 因此没有当前用户维度的模型可见性过滤
│
├─ [PHASE 05] Handler local state
│    ├─ model_entries = []
│    ├─ SystemTime::now()
│    ├─ duration_since(UNIX_EPOCH)
│    └─ DECISION: system time conversion OK?
│         ├─ YES → current_time = duration.as_secs()
│         └─ NO  → unwrap_or_default() → current_time = 0
│
├─ CALL → ChannelAbilityModel::list_distinct_models(&state.db)
│
▼
FILE: crates/database/crates/channel/src/channel_ability.rs
│
├─ [PHASE 06] Database connection
│    ├─ db.get_connection()
│    └─ DECISION: connection acquired?
│         ├─ NO  → return Err → 回到 handler
│         └─ YES → conn.pool()
│
├─ [PHASE 07] SQL / state read
│    ├─ SELECT DISTINCT model
│    ├─ FROM channel_abilities
│    ├─ WHERE enabled = 1
│    └─ ORDER BY model
│
├─ sqlx::query_as(sql).fetch_all(pool).await
│    └─ DECISION: SQL success?
│         ├─ NO  → return Err
│         └─ YES → Vec<(String,)> → map → Ok(Vec<String>)
│
├─ [PHASE 08] Visibility semantics
│    ├─ INCLUDE only ability.enabled = 1
│    ├─ DISTINCT by model
│    ├─ NO user/group filter
│    ├─ NO channel_providers.status join
│    ├─ NO health/circuit/capacity check
│    └─ NO quota/price/billing check
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 09] Handler branch merge
│    └─ DECISION: list_distinct_models returned Ok?
│         ├─ NO / Err
│         │    ├─ if let Ok(...) body skipped
│         │    └─ model_entries stays []
│         └─ YES
│              └─ FOR EACH model
│                   ├─ id = model
│                   ├─ object = "model"
│                   ├─ created = current_time
│                   ├─ owned_by = "burncloud"
│                   ├─ permission = []
│                   ├─ root = model
│                   ├─ parent = null
│                   └─ push → model_entries
│
├─ [PHASE 10] Serialization
│    ├─ response_json = {object:"list", data:model_entries}
│    ├─ serde_json::to_string(...)
│    └─ DECISION: serialization success?
│         ├─ YES → normal JSON body
│         └─ NO  → literal fallback {"object":"list","data":[]}
│
├─ [PHASE 11] HTTP response construction
│    ├─ build_response_with_header(StatusCode::OK, content-type, application/json, body)
│    ├─ Response::builder().status(200).header(...).body(...)
│    └─ DECISION: response builder success?
│         ├─ YES → HTTP 200 + JSON body
│         └─ NO  → retry status 200 + empty body
│              └─ DECISION: retry success?
│                   ├─ YES → HTTP 200 + empty body
│                   └─ NO  → Response::new(Body::empty())
│
├─ [PHASE 12] Explicitly NOT executed
│    ├─ proxy_handler
│    ├─ Token/JWT auth
│    ├─ Quota / rate limiter
│    ├─ ModelRouter / Scheduler
│    ├─ Circuit Breaker
│    ├─ Billing
│    └─ Provider / upstream
│
▼
END
     └─ Client receives model-list response
"""


def flow_usage(entry, models=False):
    call = 'get_usage_stats_by_model(user_id, "month")' if models else 'get_usage_stats(user_id, "month")'
    result = '按模型聚合的月度 usage' if models else '当前用户月度总 usage'
    return common_http_prefix(entry) + f"""│         ├─ YES（其它顶层 route）→ 对应 handler
│         └─ NO → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 03] Explicit Data Plane route
│    ├─ Route match: {entry}
│    └─ handler = {'usage_models_handler' if models else 'usage_handler'}()
│
├─ [PHASE 04] Credential extraction
│    ├─ read Authorization header
│    ├─ require Bearer token
│    └─ DECISION: Bearer credential present?
│         ├─ NO  → HTTP 401 → END
│         └─ YES → extract_token_user(...)
│
├─ [PHASE 05] Multi-generation identity resolution
│    ├─ Try new Router token table
│    │    └─ validate_token_and_get_info(...)
│    ├─ DECISION: new token valid?
│    │    ├─ YES → resolve user_id
│    │    └─ NO  → legacy validation
│    ├─ validate_token_detailed(...)
│    ├─ DECISION: legacy token valid?
│    │    ├─ YES → resolve user_id
│    │    └─ NO  → JWT fallback
│    ├─ JWT decode / Claims.sub
│    └─ DECISION: any identity path resolved?
│         ├─ NO  → 401 / service-unavailable error branch → END
│         └─ YES → user_id
│
▼
FILE: crates/database/crates/router/src/lib.rs
│
├─ [PHASE 06] Usage aggregation query
│    ├─ CALL {call}
│    ├─ period = month
│    ├─ scope = resolved user_id
│    └─ DECISION: DB aggregation success?
│         ├─ NO  → HTTP 500 → END
│         └─ YES → usage rows / aggregate
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 07] Response mapping
│    ├─ map DB aggregate → API response object
│    ├─ serialize JSON
│    └─ DECISION: serialization/build success?
│         ├─ NO  → internal response error branch
│         └─ YES → HTTP 200 application/json
│
├─ [PHASE 08] Side effects
│    ├─ no Provider call
│    ├─ no Scheduler
│    ├─ no inference billing deduction
│    └─ read-only usage query
│
▼
END
     └─ Client receives {result}
"""


def flow_proxy(entry):
    special = []
    if "Gemini" in entry or ":" in entry:
        special.append("model 可能从 Gemini URL path 提取，而不是 JSON body")
    if "video/generations" in entry:
        special.append("解析 duration/resolution；成功后异步保存 task_id → channel_id 映射")
    if "streamGenerateContent" in entry:
        special.append("上游返回流式内容，进入 streaming usage/response path")
    special_text = "\n".join(f"│    ├─ {x}" for x in special) if special else "│    ├─ 无额外 endpoint-specific branch"
    return common_http_prefix(entry) + f"""│         ├─ YES（Management/Internal/LiveView 等）→ 对应 handler
│         └─ NO → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 03] Data Plane route selection
│    ├─ explicit /v1/models or usage routes checked first
│    └─ DECISION: explicit route matched?
│         ├─ YES → corresponding explicit handler
│         └─ NO  → proxy_handler()
│
├─ [PHASE 04] Path normalization + request identity
│    ├─ normalize_doubled_path()
│    ├─ preserve Method / URI / headers
│    ├─ request-id already attached by server middleware
│    └─ prepare AppState/runtime services
│
├─ [PHASE 05] Credential source selection
│    ├─ Candidate 1: Authorization: Bearer ...
│    ├─ Candidate 2: x-api-key
│    ├─ Candidate 3: x-goog-api-key
│    └─ DECISION: any supported credential exists?
│         ├─ NO  → HTTP 401 → END
│         └─ YES → token validation chain
│
├─ [PHASE 06] Token / user / group resolution
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
├─ [PHASE 07] Account / quota guard
│    ├─ inspect quota/order metadata
│    └─ DECISION: quota exhausted / account cannot spend?
│         ├─ YES → HTTP 402 Payment Required → END
│         └─ NO  → continue
│
├─ [PHASE 08] Local request rate limiting
│    ├─ limiter key derived from authenticated request context
│    └─ DECISION: limiter allows request?
│         ├─ NO  → HTTP 429 Too Many Requests → END
│         └─ YES → continue
│
├─ [PHASE 09] Request-body acquisition
│    ├─ collect Axum body bytes
│    └─ DECISION: body read/size/parse boundary succeeds?
│         ├─ NO  → client/request error → END
│         └─ YES → immutable request payload for routing/adaptor
│
├─ [PHASE 10] Model + protocol context extraction
│    ├─ OpenAI/Anthropic: model usually from JSON body
│    ├─ Gemini: model may come from URL path
│    ├─ detect streaming / batch / priority hints
│    ├─ detect API protocol family
{special_text}
│    └─ DECISION: required model/context resolved?
│         ├─ NO  → invalid request / model resolution error → END
│         └─ YES → proxy_logic(...)
│
├─ [PHASE 11] Enter proxy_logic(...)
│    ├─ load scheduling policy for resolved user group
│    ├─ resolve requested model / model mapping
│    ├─ load candidate channel abilities
│    ├─ apply user/order/price constraints
│    └─ produce ordered/weighted candidate set
│
├─ [PHASE 12] Candidate eligibility filtering
│    ├─ ability enabled?
│    ├─ channel state allows traffic?
│    ├─ circuit breaker allows attempt?
│    ├─ rate budget / shaper allows attempt?
│    ├─ price/order constraints satisfied?
│    └─ DECISION: any candidate remains?
│         ├─ NO  → no-upstream / routing error → END
│         └─ YES → candidate attempt loop
│
├─ [PHASE 13] Candidate attempt loop
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
├─ [PHASE 14] Protocol transformation boundary
│    ├─ inspect source protocol + target Channel protocol
│    └─ DECISION: native passthrough possible?
│         ├─ YES
│         │    ├─ preserve compatible body/headers semantics
│         │    └─ avoid unnecessary transform
│         └─ NO
│              └─ DynamicAdaptorFactory / adaptor conversion path
│                   └─ DYNAMIC: exact transformation depends on Provider adaptor
│
├─ [PHASE 15] Upstream network I/O
│    ├─ send HTTP request through shared client
│    ├─ wait for headers/body or stream
│    └─ DECISION: upstream attempt succeeds?
│         ├─ NO
│         │    ├─ classify failure
│         │    ├─ update channel/circuit feedback
│         │    ├─ optional API-version detect/update
│         │    └─ DECISION: another eligible candidate?
│         │         ├─ YES → back to PHASE 13
│         │         └─ NO  → final upstream/routing error → END
│         └─ YES → response handling
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 16] Response mode split
│    └─ DECISION: streaming response?
│         ├─ YES
│         │    ├─ stream chunks to client
│         │    ├─ collect/derive usage while stream progresses
│         │    └─ handle stream completion/disconnect
│         └─ NO
│              ├─ collect upstream body
│              └─ parse/derive usage metadata
│
├─ [PHASE 17] Unified usage + cost
│    ├─ normalize prompt/input tokens
│    ├─ normalize completion/output tokens
│    ├─ endpoint-specific usage augmentation when needed
│    ├─ PriceCache / CostCalculator lookup
│    └─ CostCalculator::calculate()
│
├─ [PHASE 18] Accounting / persistence side effects
│    ├─ enqueue RouterLog
│    ├─ enqueue RequestLog according to storage policy
│    ├─ send AIMD/rate-budget feedback
│    ├─ update circuit/channel state feedback
│    ├─ async token accessed_time update where applicable
│    └─ DECISION: calculated cost > 0?
│         ├─ YES → async quota deduction
│         └─ NO  → no quota deduction task
│
├─ [PHASE 19] Endpoint-specific async side effects
{('│    ├─ save video task mapping asynchronously' if 'video/generations' in entry else '│    ├─ none beyond common request side effects')}
│
├─ [PHASE 20] Final response construction
│    ├─ preserve/normalize upstream-compatible status + body
│    ├─ attach resolved channel/model diagnostic headers where configured
│    └─ return Axum Response
│
▼
END
     └─ Client receives successful upstream-compatible response OR a terminal error from an earlier branch
"""


def flow_video_poll(entry):
    return common_http_prefix(entry) + """│         ├─ YES（其它 route）→ corresponding handler
│         └─ NO → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 03] proxy_handler entry
│    ├─ normalize path
│    ├─ extract supported credential
│    ├─ validate token/user
│    ├─ quota guard
│    └─ local rate limiter
│
├─ [PHASE 04] Video polling special-case detection
│    └─ DECISION: Method == GET AND Path starts with /v1/videos/ ?
│         ├─ NO  → normal inference proxy_logic
│         └─ YES → polling branch
│
├─ [PHASE 05] Task identity
│    ├─ task_id = URL suffix
│    └─ DECISION: task_id non-empty/valid enough for lookup?
│         ├─ NO  → client/not-found error → END
│         └─ YES → DB lookup
│
▼
FILE: crates/database/crates/router/src/video_task.rs
│
├─ [PHASE 06] Read persisted task mapping
│    ├─ RouterVideoTaskModel::get_by_task_id(task_id)
│    └─ DECISION: mapping exists?
│         ├─ NO  → HTTP 404 task_not_found → END
│         └─ YES → channel_id + stored task metadata
│
▼
FILE: crates/database/crates/channel/src/lib.rs
│
├─ [PHASE 07] Load original Channel
│    ├─ ChannelProviderModel::get_by_id(channel_id)
│    └─ DECISION: Channel record available/configured?
│         ├─ NO  → HTTP 502 → END
│         └─ YES → base_url + credential
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 08] Direct upstream polling request
│    ├─ construct {base_url}/v1/videos/{task_id}
│    ├─ apply original Channel authentication
│    ├─ IMPORTANT: no new scheduler/model selection
│    └─ send GET through shared HTTP client
│
├─ [PHASE 09] Upstream polling result
│    └─ DECISION: network/upstream request succeeds?
│         ├─ NO  → HTTP 502 → END
│         └─ YES
│              ├─ preserve upstream status
│              ├─ collect upstream body
│              └─ return polling response
│
├─ [PHASE 10] Side effects
│    ├─ task mapping is read-only in this request
│    ├─ no fresh task mapping created
│    └─ no model scheduler selection
│
▼
END
     └─ Client receives current video task state
"""


def flow_public_auth(entry):
    handler = HANDLERS.get(entry, "auth_handler")
    service_map = {
        "POST /api/auth/register": "register_user → get_user_roles → generate_token",
        "POST /api/auth/login": "login_user → get_user_roles → generate_token/response",
        "POST /api/auth/forgot-password": "request_password_reset",
        "POST /api/auth/reset-password": "reset_password",
        "GET /api/auth/google": 'oauth_url("google")',
        "GET /api/auth/github": 'oauth_url("github")',
    }
    service = service_map.get(entry, "UserService")
    return common_http_prefix(entry) + f"""│         ├─ YES → matched top-level/public route path
│         └─ NO  → other route composition
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ [PHASE 03] Management API composition
│    ├─ public auth routes are mounted outside protected JWT layer
│    └─ DECISION: current path matches public Authentication route?
│         ├─ NO  → protected router / other API
│         └─ YES → no pre-handler JWT requirement
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ [PHASE 04] Handler entry
│    └─ {handler}()
│
├─ [PHASE 05] Input extraction
│    ├─ Axum Query/Json extractor parses request fields
│    └─ DECISION: syntactic extraction succeeds?
│         ├─ NO  → Axum/client error response → END
│         └─ YES → handler validation
│
├─ [PHASE 06] Business validation
│    ├─ validate required username/email/password/token/provider inputs as applicable
│    └─ DECISION: required business input acceptable?
│         ├─ NO  → err(...) response → END
│         └─ YES → service call
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ [PHASE 07] UserService / OAuth operation
│    └─ CALL {service}
│
├─ [PHASE 08] Persistence / identity branch
│    ├─ register/login/reset paths may read/write user state
│    ├─ OAuth URL path is read/config construction only
│    └─ DECISION: service operation succeeds?
│         ├─ NO  → map service error → API error response
│         └─ YES → service result
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ [PHASE 09] Security-sensitive response shaping
│    ├─ login/register success may include JWT + user roles
│    ├─ forgot-password intentionally avoids revealing account existence
│    └─ OAuth endpoints return authorization URL rather than callback completion
│
├─ [PHASE 10] Serialize / return
│    └─ ok(...) / err(...) → HTTP JSON response
│
▼
END
"""


def flow_management(entry, group):
    handler = HANDLERS.get(entry, "route_handler")
    file = source_file_for_group(group, entry)
    admin = group == "Channel Management"
    write = entry.startswith(("POST ", "PUT ", "DELETE "))
    auth_extra = "│    ├─ Admin role required for Channel Management\n" if admin else "│    ├─ Route uses authenticated Claims/user context as implemented\n"
    op = "write/mutate state" if write else "read/query state"
    return common_http_prefix(entry) + f"""│         ├─ YES → Management API / protected route candidate
│         └─ NO  → other top-level/fallback route
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ [PHASE 03] protected_routes composition
│    ├─ route registered under Management API
│    └─ auth_middleware() wraps protected router
│
├─ [PHASE 04] JWT authentication
│    ├─ read Authorization header
│    └─ DECISION: Authorization starts with Bearer?
│         ├─ NO  → HTTP 401 → END
│         └─ YES → verify_jwt(...)
│
├─ DECISION: JWT signature/claims valid?
│    ├─ NO  → HTTP 401 → END
│    └─ YES
│         ├─ Claims inserted into request extensions
│         └─ continue to route handler
│
▼
FILE: {file}
│
├─ [PHASE 05] Handler
│    └─ {handler}()
│
├─ [PHASE 06] Request extraction
│    ├─ Path params / Query params / JSON body as required by Method
│    ├─ authenticated Claims available from extensions
│    └─ DECISION: extraction/required fields valid?
│         ├─ NO  → client/error response → END
│         └─ YES → authorization/business checks
│
├─ [PHASE 07] Authorization + invariants
{auth_extra}│    ├─ validate ID/status/range/reason/etc. according to handler
│    └─ DECISION: authorization/invariants pass?
│         ├─ NO  → 4xx/error payload → END
│         └─ YES → service/database call
│
├─ [PHASE 08] Service / Database boundary
│    ├─ operation type: {op}
│    ├─ invoke route-specific Service / Database method
│    └─ DECISION: operation succeeds?
│         ├─ NO  → map error → HTTP error response
│         └─ YES → domain result
│
├─ [PHASE 09] State effects
│    ├─ READ routes: no intended mutation beyond incidental telemetry
│    ├─ WRITE routes: persist create/update/delete/config action
│    └─ route-specific async/internal calls execute before/around result when implemented
│
├─ [PHASE 10] Response mapping
│    ├─ domain model → DTO/JSON
│    ├─ pagination/summary fields where applicable
│    └─ serialize success payload
│
├─ [PHASE 11] HTTP exit
│    └─ return success or mapped error status/body
│
▼
END
"""


def flow_top_health(entry):
    return common_http_prefix(entry) + """│         ├─ YES → explicit GET /health handler
│         └─ NO  → continue route matching
│
├─ [PHASE 03] Liveness handler
│    ├─ no JWT middleware
│    ├─ no DB query in handler
│    ├─ no Router/Provider call
│    └─ return literal "ok"
│
├─ [PHASE 04] Response
│    └─ HTTP 200 text/plain-ish body
│
▼
END
"""


def flow_internal(entry):
    handler = HANDLERS.get(entry, "internal_handler")
    wait = "│    ├─ force-sync route sends channel message and awaits oneshot/timeout\n" if "prices/sync" in entry else ""
    return common_http_prefix(entry) + f"""│         ├─ YES → merged Router Internal route
│         └─ NO  → continue to other routes/fallback
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 03] Internal route match
│    └─ {handler}()
│
├─ [PHASE 04] Authentication boundary
│    ├─ Router internal_app itself is not wrapped by Management JWT middleware
│    └─ network exposure therefore depends on server deployment/binding/firewall
│
├─ [PHASE 05] Runtime-state operation
│    ├─ read/mutate in-memory Router runtime services
{wait}│    └─ DECISION: required runtime service/channel available?
│         ├─ NO  → route-specific 5xx/timeout/error response
│         └─ YES → perform operation
│
├─ [PHASE 06] Route-specific state
│    ├─ health: scheduler/circuit/channel/rate-budget snapshot
│    ├─ price sync: force_sync_tx + oneshot result
│    ├─ trip-all: circuit_breaker.trip_all()
│    └─ metrics: Router runtime counters
│
├─ [PHASE 07] Serialize result
│    └─ DECISION: operation/result successful?
│         ├─ NO  → error HTTP response
│         └─ YES → JSON success response
│
▼
END
"""


def flow_404(entry):
    return common_http_prefix(entry) + """│         ├─ YES → Management API protected router
│         └─ NO → other router
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ [PHASE 03] JWT middleware executes before protected catch-all
│    ├─ DECISION: Bearer JWT valid?
│    │    ├─ NO → HTTP 401 → END
│    │    └─ YES → Claims inserted
│    └─ continue route matching
│
├─ [PHASE 04] Concrete /console/api/* routes checked
│    └─ DECISION: any concrete protected route matched?
│         ├─ YES → that handler executes
│         └─ NO → api_not_found()
│
├─ [PHASE 05] Catch-all purpose
│    ├─ prevents unknown API path from being served as LiveView HTML
│    └─ returns explicit API 404
│
▼
END
     └─ HTTP 404 "API endpoint not found"
"""


def flow_openapi(entry):
    handler = HANDLERS.get(entry, "swagger_ui")
    return common_http_prefix(entry) + f"""│         ├─ YES → api::routes()
│         └─ NO → other route
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ [PHASE 03] OpenAPI routes are currently inside protected_routes
│    ├─ auth_middleware()
│    └─ DECISION: JWT valid?
│         ├─ NO → HTTP 401 → END
│         └─ YES → route handler
│
▼
FILE: crates/server/src/api/openapi.rs
│
├─ [PHASE 04] Handler
│    └─ {handler}()
│
├─ [PHASE 05] Content construction
│    └─ DECISION: endpoint type?
│         ├─ /api-docs/openapi.json
│         │    ├─ construct OpenAPI 3.0.3 object
│         │    ├─ include documented paths/schemas
│         │    └─ serialize JSON
│         └─ /swagger-ui[/]
│              ├─ construct embedded Swagger HTML shell
│              └─ browser later loads Swagger UI assets
│
├─ [PHASE 06] Response
│    ├─ JSON endpoint → application/json
│    └─ UI endpoint → text/html
│
▼
END
"""


def flow_liveview(entry, ws=False):
    if ws:
        return common_http_prefix(entry) + """│         ├─ YES → merged LiveView router
│         └─ NO → fallback routing
│
├─ [PHASE 03] Feature gate
│    └─ DECISION: enable_liveview == true?
│         ├─ NO → /ws not served by LiveView path
│         └─ YES → websocket route available
│
▼
FILE: crates/client/src/lib.rs
│
├─ [PHASE 04] WebSocket upgrade
│    ├─ validate Upgrade/Connection/Sec-WebSocket-* headers
│    └─ DECISION: WebSocket handshake valid?
│         ├─ NO → HTTP handshake error → END
│         └─ YES → 101 Switching Protocols
│
├─ [PHASE 05] LiveView session
│    ├─ create/attach Dioxus LiveView session
│    ├─ receive browser UI events
│    ├─ update Virtual DOM/server-side UI state
│    └─ send render patches/messages to browser
│
├─ [PHASE 06] Connection loop
│    └─ DECISION: socket still connected?
│         ├─ YES → await next UI message → repeat
│         └─ NO → cleanup session
│
▼
END
"""
    return common_http_prefix(entry) + """│         ├─ YES → merged LiveView/static route candidate
│         └─ NO → other route/fallback
│
├─ [PHASE 03] LiveView feature gate
│    └─ DECISION: enable_liveview == true?
│         ├─ NO → LiveView route unavailable; routing continues/falls back
│         └─ YES → match LiveView Router
│
▼
FILE: crates/client/src/lib.rs
│
├─ [PHASE 04] HTTP shell/static handler
│    ├─ route shell / preview / favicon according to path
│    └─ DECISION: requested LiveView/static route recognized?
│         ├─ NO → route miss
│         └─ YES → construct HTML/static response
│
▼
FILE: crates/client/src/app.rs
│
├─ [PHASE 05] Client route model
│    ├─ Dioxus Route enum represents browser-side view
│    ├─ App contexts: auth/theme/i18n/toast
│    └─ page-specific component selected after client session establishes
│
├─ [PHASE 06] Follow-up interactive transport
│    ├─ initial HTTP response delivers shell
│    └─ interactive events move to /ws LiveView session
│
▼
END
     └─ Browser receives HTML/static shell; UI lifecycle continues separately
"""


def cli_source(entry):
    low=entry.lower()
    mapping={
        ' bundle ':'src/cli/bundle.rs',' channel ':'src/cli/channel.rs',' price ':'src/cli/price.rs',' tiered ':'src/cli/price.rs',
        ' token ':'src/cli/token.rs',' protocol ':'src/cli/protocol.rs',' currency ':'src/cli/currency.rs',' user ':'src/cli/user.rs',
        ' log ':'src/cli/log.rs',' monitor ':'src/cli/monitor.rs',' install ':'src/cli/install.rs',' update':'src/main.rs'
    }
    for key,val in mapping.items():
        if key in low or (key.strip()=='update' and low.startswith('burncloud update')): return val
    return 'src/main.rs'


def flow_cli(entry, binary=False):
    if binary:
        file_map={
            'burncloud-client':'crates/client/src/main.rs','screenshot_gen':'crates/client/src/bin/screenshot_gen.rs',
            'burncloud-download':'crates/download/src/main.rs','burncloud-loop':'crates/loops/src/main.rs',
            'client-api':'crates/client/crates/client-api/src/main.rs','client-shared':'crates/client/crates/client-shared/src/main.rs',
            'client-tray':'crates/client/crates/client-tray/src/main.rs'}
        f=file_map.get(entry,'src/main.rs')
        return f"""START
│
├─ [PHASE 00] OS process launch
│    ├─ executable: {entry}
│    ├─ argv / cwd / environment inherited from OS
│    └─ DECISION: executable can be loaded/launched?
│         ├─ NO → OS-level error → END
│         └─ YES → main()
│
▼
FILE: {f}
│
├─ [PHASE 01] main() initialization
│    ├─ initialize executable-specific runtime/services
│    ├─ parse any supported arguments
│    └─ DECISION: platform/arguments/initialization valid?
│         ├─ NO → print/return error → process exit
│         └─ YES → continue
│
├─ [PHASE 02] Runtime work
│    ├─ create client/download/loop/tray structures as applicable
│    ├─ start event loop or execute one-shot job
│    └─ DECISION: long-running executable?
│         ├─ YES → enter event/service loop
│         └─ NO → produce output and exit
│
├─ [PHASE 03] Error boundary
│    └─ runtime error → log/return non-success according to executable implementation
│
▼
END / RUNNING LOOP
"""
    src=cli_source(entry)
    return f"""START
│
├─ [PHASE 00] Shell input
│    ├─ command: {entry}
│    ├─ argv tokenization done by shell
│    └─ process environment / cwd available
│
▼
FILE: src/main.rs
│
├─ [PHASE 01] Process bootstrap
│    ├─ dotenv load
│    ├─ ensure/generate MASTER_KEY
│    ├─ initialize logging
│    └─ inspect argv
│
├─ [PHASE 02] Top-level dispatch
│    └─ DECISION: default/server/router/client direct runtime mode?
│         ├─ YES → launch corresponding runtime
│         └─ NO → CLI parser path
│
▼
FILE: src/cli/commands.rs
│
├─ [PHASE 03] Clap parse
│    ├─ parse command/subcommand/options/positionals
│    └─ DECISION: syntax + required args valid?
│         ├─ NO → Clap help/error + exit code → END
│         └─ YES → typed command enum
│
├─ [PHASE 04] Command dispatch
│    ├─ match typed command variant
│    └─ call implementation module
│
▼
FILE: {src}
│
├─ [PHASE 05] Command-specific input validation
│    ├─ validate IDs/files/model names/ranges/options as required
│    └─ DECISION: semantic input valid?
│         ├─ NO → error output → END
│         └─ YES → perform operation
│
├─ [PHASE 06] External/state I/O
│    ├─ DB / filesystem / HTTP / service operation depending on command
│    └─ DECISION: operation succeeds?
│         ├─ NO → print/return error → END
│         └─ YES → domain result
│
├─ [PHASE 07] Output formatting
│    ├─ map result to table/text/status output
│    └─ write stdout/stderr
│
├─ [PHASE 08] Process exit
│    └─ success returns to shell; long-running command may remain active
│
▼
END
"""


def flow_background(entry):
    return f"""START / TRIGGER
│
├─ [PHASE 00] Trigger source
│    ├─ startup spawn / request-time tokio::spawn / manager restoration / channel message
│    └─ task: {entry}
│
├─ [PHASE 01] Spawn / registration
│    ├─ parent runtime creates async task/thread/loop
│    └─ DECISION: spawn/runtime handle available?
│         ├─ NO → task never starts; parent may log error
│         └─ YES → task owns/borrows required shared state
│
├─ [PHASE 02] Wait boundary
│    ├─ timer sleep / mpsc receive / polling interval / restored work item
│    └─ DECISION: trigger/event available?
│         ├─ NO → continue waiting
│         └─ YES → one iteration begins
│
├─ [PHASE 03] Input snapshot
│    ├─ read latest runtime/DB/request-derived state needed by job
│    └─ freeze iteration context
│
├─ [PHASE 04] Core job operation
│    ├─ execute {entry}
│    └─ may call DB / HTTP / filesystem / runtime service depending on task
│
├─ [PHASE 05] Operation result
│    └─ DECISION: iteration succeeds?
│         ├─ NO
│         │    ├─ log/record failure
│         │    ├─ preserve parent request availability when task is fail-open
│         │    └─ decide retry on next event/interval
│         └─ YES
│              ├─ update in-memory state and/or persistent state
│              └─ emit success telemetry/log
│
├─ [PHASE 06] Cancellation / lifetime
│    └─ DECISION: parent runtime still alive AND task should continue?
│         ├─ YES → back to PHASE 02
│         └─ NO → release task resources
│
▼
END / NEXT ITERATION
"""


def flow_startup(entry):
    return f"""START
│
├─ [PHASE 00] Process/environment input
│    ├─ startup target: {entry}
│    ├─ environment variables / dotenv
│    ├─ CLI/platform mode
│    └─ filesystem/database availability
│
├─ [PHASE 01] Enter startup function
│    └─ execute {entry}
│
├─ [PHASE 02] Dependency initialization
│    ├─ construct required DB/services/runtime state
│    ├─ register routes/tasks as applicable
│    └─ DECISION: dependency initialization succeeds?
│         ├─ NO → propagate startup error → process/runtime not ready → END
│         └─ YES → next dependency
│
├─ [PHASE 03] Runtime composition
│    ├─ wire shared Arc/State/services
│    ├─ compose routers/middleware/background jobs
│    └─ make dependencies reachable from runtime entrypoints
│
├─ [PHASE 04] Readiness boundary
│    └─ DECISION: all required startup stages complete?
│         ├─ NO → startup fails/returns Err
│         └─ YES → expose listener/client/event loop/runtime
│
├─ [PHASE 05] Steady-state handoff
│    ├─ long-running loops take ownership of runtime
│    └─ requests/events can now enter documented entrypoints
│
▼
END
     └─ component is READY / RUNNING
"""


def flow_ui(entry, group):
    if group == "Local UI State":
        return f"""START
│
├─ [PHASE 00] App root initialization
│    └─ state/context: {entry}
│
▼
FILE: crates/client/src/app.rs
│
├─ [PHASE 01] Create initial state
│    ├─ derive default/configured value
│    └─ store in Dioxus signal/context
│
├─ [PHASE 02] Provide context
│    ├─ descendant components can read/subscribe
│    └─ current render reads latest value
│
├─ [PHASE 03] Update path
│    └─ DECISION: UI event changes this state?
│         ├─ NO → keep current value
│         └─ YES
│              ├─ mutate signal/context
│              └─ mark dependent subtree dirty
│
├─ [PHASE 04] Re-render
│    └─ Dioxus reconciles affected component tree
│
▼
END / UI EVENT LOOP CONTINUES
"""
    if group == "Desktop UI":
        return f"""START
│
├─ [PHASE 00] Desktop event/state input
│    └─ action: {entry}
│
▼
FILE: crates/client/src/app.rs
│
├─ [PHASE 01] Platform branch
│    └─ DECISION: current platform/runtime supports desktop action?
│         ├─ NO → skip/unsupported branch → END
│         └─ YES → obtain desktop window/tray handle
│
├─ [PHASE 02] Current UI state
│    ├─ read visibility/focus/maximized/tray state as needed
│    └─ decide desired state
│
├─ [PHASE 03] Apply desktop side effect
│    ├─ maximize / show / hide / focus / tray startup
│    └─ DECISION: OS/window operation succeeds?
│         ├─ NO → log/ignore according to UI path
│         └─ YES → state visible to user
│
├─ [PHASE 04] Event loop handoff
│    └─ return control to Dioxus/desktop event loop
│
▼
END / LOOP CONTINUES
"""
    return f"""START
│
├─ [PHASE 00] Navigation input
│    ├─ browser/client route: {entry}
│    ├─ current Auth context
│    ├─ current Theme/i18n/Toast context
│    └─ optional route params/query
│
▼
FILE: crates/client/src/app.rs
│
├─ [PHASE 01] Dioxus Router match
│    └─ DECISION: Route enum/path matches?
│         ├─ NO → NotFound route/component
│         └─ YES → select mapped page component
│
├─ [PHASE 02] Route guards / context read
│    ├─ component can read Auth context
│    ├─ component can read Theme/i18n state
│    └─ DECISION: page requires authenticated state and context satisfies it?
│         ├─ NO → login/guard behavior as implemented by component/router
│         └─ YES → render page
│
├─ [PHASE 03] Component construction
│    ├─ initialize local signals/state
│    ├─ render initial VDOM
│    └─ register click/input/effect handlers
│
├─ [PHASE 04] Data boundary
│    └─ DECISION: component action/effect needs server data?
│         ├─ NO → remain local UI-only path
│         └─ YES → issue separate HTTP/API request
│              └─ that request is documented under HTTP / API, not hidden in this flow
│
├─ [PHASE 05] User-visible result
│    ├─ Dioxus reconciles VDOM
│    └─ page/render state becomes visible
│
├─ [PHASE 06] Event loop
│    └─ wait for next UI event/navigation/state update
│
▼
END / UI LOOP CONTINUES
"""


def detailed_flow(p):
    section=p['section']; group=p['group']; entry=p['entry']; title=p['title']
    if section == 'HTTP / API':
        if entry == 'GET /v1/models': return flow_models(entry)
        if entry == 'GET /api/v1/usage': return flow_usage(entry, False)
        if entry == 'GET /api/v1/usage/models': return flow_usage(entry, True)
        if group == 'AI API / Data Plane':
            if entry.startswith('GET /v1/videos/'): return flow_video_poll(entry)
            return flow_proxy(entry)
        if group == 'Authentication': return flow_public_auth(entry)
        if group in ('Channel Management','Token','User','Billing / Usage','Logs','Monitoring / Security','Cache'):
            if entry in ('GET /api/v1/usage','GET /api/v1/usage/models'):
                return flow_usage(entry, entry.endswith('/models'))
            return flow_management(entry, group)
        if group == 'Admin / Internal':
            if entry == 'GET /health': return flow_top_health(entry)
            if 'protected 404' in title: return flow_404(entry)
            return flow_internal(entry)
        if group == 'OpenAPI / Swagger': return flow_openapi(entry)
        if group == 'Web UI / LiveView / WebSocket': return flow_liveview(entry, entry == 'GET /ws')
        return flow_management(entry, group)
    if section == 'CLI / Executables': return flow_cli(entry, group == 'Workspace Binaries')
    if section == 'Background Jobs / Async Side Effects': return flow_background(entry)
    if section == 'Startup': return flow_startup(entry)
    if section == 'UI-only Actions': return flow_ui(entry, group)
    return f"START\n│\n├─ [PHASE 00] Input: {entry}\n├─ DECISION: entry accepted?\n│    ├─ NO → END\n│    └─ YES → execute\n▼\nEND\n"


def input_http(p):
    e=p['entry']; g=p['group']; low=e.lower()
    host='api.burncloud.example'
    if e == 'GET /v1/models':
        return http_block(f"GET /v1/models HTTP/1.1\nHost: {host}\nAccept: application/json")
    if e in ('GET /api/v1/usage','GET /api/v1/usage/models'):
        return http_block(f"{e} HTTP/1.1\nHost: {host}\nAuthorization: Bearer bc_live_7d4e...example\nAccept: application/json")
    if e in ('POST /v1/chat/completions','POST /chat/completions'):
        return http_block(f"{e} HTTP/1.1\nHost: {host}\nAuthorization: Bearer bc_live_7d4e...example\nContent-Type: application/json\n\n{{\n  \"model\": \"gpt-5.4\",\n  \"messages\": [{{\"role\": \"user\", \"content\": \"解释 BurnCloud 的作用\"}}],\n  \"stream\": false\n}}")
    if e == 'POST /v1/completions':
        return http_block(f"POST /v1/completions HTTP/1.1\nHost: {host}\nAuthorization: Bearer bc_live_7d4e...example\nContent-Type: application/json\n\n{{\"model\":\"gpt-5.4\",\"prompt\":\"BurnCloud 是\",\"max_tokens\":64}}")
    if e == 'POST /v1/embeddings':
        return http_block(f"POST /v1/embeddings HTTP/1.1\nHost: {host}\nAuthorization: Bearer bc_live_7d4e...example\nContent-Type: application/json\n\n{{\"model\":\"text-embedding-3-large\",\"input\":\"BurnCloud routing\"}}")
    if e == 'POST /v1/messages':
        return http_block(f"POST /v1/messages HTTP/1.1\nHost: {host}\nx-api-key: bc_live_7d4e...example\nContent-Type: application/json\n\n{{\"model\":\"claude-sonnet-4-5\",\"max_tokens\":128,\"messages\":[{{\"role\":\"user\",\"content\":\"你好\"}}]}}")
    if e == 'POST /v1/video/generations':
        return http_block(f"POST /v1/video/generations HTTP/1.1\nHost: {host}\nAuthorization: Bearer bc_live_7d4e...example\nContent-Type: application/json\n\n{{\"model\":\"video-model-pro\",\"prompt\":\"夜晚城市航拍\",\"duration\":5,\"resolution\":\"1080p\"}}")
    if e.startswith('GET /v1/videos/'):
        return http_block(f"GET /v1/videos/video_task_bc_01JXYZ HTTP/1.1\nHost: {host}\nAuthorization: Bearer bc_live_7d4e...example\nAccept: application/json")
    if ':generateContent' in e:
        path=e.split(' ',1)[1].replace('{model}','gemini-example')
        return http_block(f"POST {path} HTTP/1.1\nHost: {host}\nx-goog-api-key: bc_live_7d4e...example\nContent-Type: application/json\n\n{{\"contents\":[{{\"role\":\"user\",\"parts\":[{{\"text\":\"解释 BurnCloud\"}}]}}]}}")
    if ':streamGenerateContent' in e:
        path=e.split(' ',1)[1].replace('{model}','gemini-example')
        return http_block(f"POST {path} HTTP/1.1\nHost: {host}\nx-goog-api-key: bc_live_7d4e...example\nContent-Type: application/json\n\n{{\"contents\":[{{\"role\":\"user\",\"parts\":[{{\"text\":\"流式介绍 BurnCloud\"}}]}}]}}")
    if ':countTokens' in e:
        path=e.split(' ',1)[1].replace('{model}','gemini-example')
        return http_block(f"POST {path} HTTP/1.1\nHost: {host}\nx-goog-api-key: bc_live_7d4e...example\nContent-Type: application/json\n\n{{\"contents\":[{{\"parts\":[{{\"text\":\"需要统计的文本\"}}]}}]}}")
    if ':embedContent' in e:
        path=e.split(' ',1)[1].replace('{model}','gemini-embedding-example')
        return http_block(f"POST {path} HTTP/1.1\nHost: {host}\nx-goog-api-key: bc_live_7d4e...example\nContent-Type: application/json\n\n{{\"content\":{{\"parts\":[{{\"text\":\"BurnCloud embedding\"}}]}}}}")
    if p['title'] == 'Router fallback → proxy_handler':
        return http_block(f"POST /v1/custom-compatible-path HTTP/1.1\nHost: {host}\nAuthorization: Bearer bc_live_7d4e...example\nContent-Type: application/json\n\n{{\"model\":\"resolved-model\",\"input\":\"example\"}}")
    if g == 'Authentication':
        if 'register' in low:
            return http_block(f"POST /api/auth/register HTTP/1.1\nHost: {host}\nContent-Type: application/json\n\n{{\"username\":\"demo_user\",\"email\":\"demo@example.com\",\"password\":\"Example-Password-123!\"}}")
        if 'login' in low:
            return http_block(f"POST /api/auth/login HTTP/1.1\nHost: {host}\nContent-Type: application/json\n\n{{\"username\":\"demo_user\",\"password\":\"Example-Password-123!\"}}")
        if 'forgot-password' in low:
            return http_block(f"POST /api/auth/forgot-password HTTP/1.1\nHost: {host}\nContent-Type: application/json\n\n{{\"email\":\"demo@example.com\"}}")
        if 'reset-password' in low:
            return http_block(f"POST /api/auth/reset-password HTTP/1.1\nHost: {host}\nContent-Type: application/json\n\n{{\"token\":\"reset_token_example\",\"new_password\":\"New-Password-456!\"}}")
        return http_block(f"{e} HTTP/1.1\nHost: {host}\nAccept: application/json")
    if g in ('Web UI / LiveView / WebSocket',):
        if e == 'GET /ws':
            return http_block(f"GET /ws HTTP/1.1\nHost: {host}\nUpgrade: websocket\nConnection: Upgrade\nSec-WebSocket-Version: 13\nSec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==")
        path=e.split(' ',1)[1].replace('{*path}','dashboard')
        return http_block(f"GET {path} HTTP/1.1\nHost: {host}\nAccept: text/html")
    if g == 'Admin / Internal' and e.startswith(('GET /console/internal','POST /console/internal')):
        path=e.split(' ',1)[1]
        body='\nContent-Type: application/json\n\n{"reason":"manual maintenance"}' if e.startswith('POST ') else ''
        return http_block(f"{e.split(' ',1)[0]} {path} HTTP/1.1\nHost: {host}\nAccept: application/json{body}")
    if e == 'GET /health':
        return http_block(f"GET /health HTTP/1.1\nHost: {host}")
    if g == 'OpenAPI / Swagger':
        path=e.split(' ',1)[1]
        return http_block(f"GET {path} HTTP/1.1\nHost: {host}\nAuthorization: Bearer eyJhbGciOi...admin-jwt\nAccept: application/json,text/html")

    # protected Management API examples
    method,path=e.split(' ',1) if ' ' in e else ('GET',e)
    path=path.replace('{id}','12').replace('{token}','bc_live_7d4e...example').replace('{user_id}','10001').replace('{*path}','unknown')
    headers=f"{method} {path} HTTP/1.1\nHost: {host}\nAuthorization: Bearer eyJhbGciOi...admin-jwt\nAccept: application/json"
    if method in ('POST','PUT'):
        if g == 'Channel Management': payload='{"id":12,"name":"openai-primary","channel_type":"openai","base_url":"https://api.openai.com","status":1}'
        elif g == 'Token': payload='{"name":"production","status":1,"quota":100000000,"ip_whitelist":["203.0.113.10"]}'
        elif g == 'User' and 'topup' in low: payload='{"user_id":10001,"amount":100.0,"currency":"USD"}'
        elif 'filters' in low: payload='{"enabled":true,"threshold":25}'
        elif 'emergency-circuit-break' in low: payload='{"reason":"manual emergency isolation"}'
        else: payload='{"example":"request body"}'
        headers += "\nContent-Type: application/json\n\n" + payload
    return http_block(headers)


def input_cli(p):
    return block("$ " + p['entry'])


def input_background(p):
    return block(f"""trigger={p['group']}
job={p['entry']}
runtime=running
shared_state=available
# 该类页面的“输入”不是 HTTP body，而是启动事件、定时器、队列消息或请求侧异步事件。""")


def input_startup(p):
    return block(f"""process_target={p['entry']}
BURNCLOUD_MASTER_KEY=<configured-or-generated>
RUST_LOG=info
database_path=<runtime database>
enable_liveview=true
# 真实环境变量/参数以部署配置为准。""")


def input_ui(p):
    if p['group']=='Local UI State':
        return json_block(json.dumps({"context":p['entry'],"event":"component render/update","current_state":"example"},ensure_ascii=False,indent=2))
    if p['group']=='Desktop UI':
        return block(f"event={p['entry']}\nplatform=desktop\nwindow_state=available")
    return block(f"navigate_to={p['entry']}\nauthenticated=true\nlocale=zh-CN\ntheme=system")


def input_section(p):
    if p['section']=='HTTP / API': ex=input_http(p); note='以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。'
    elif p['section']=='CLI / Executables': ex=input_cli(p); note='CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。'
    elif p['section']=='Background Jobs / Async Side Effects': ex=input_background(p); note='后台任务通常没有 HTTP 请求体；这里把触发事件、队列/定时器和共享状态视为它的输入。'
    elif p['section']=='Startup': ex=input_startup(p); note='Startup 的输入是进程模式、环境变量、配置和外部资源可用性，而不是 API Request。'
    else: ex=input_ui(p); note='UI 页面/动作的输入是导航、用户事件和当前客户端上下文；真正的网络请求会进入独立 HTTP/API E2E 页面。'
    return f"\n## 输入示例\n\n> {note}\n\n{ex}\n\n"


def main():
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'))
    count=0
    for p in manifest['pages']:
        path=DOCS/(p['docid']+'.md')
        text=path.read_text(encoding='utf-8')
        flow=detailed_flow(p)
        new,n=FLOW_RE.subn(r"\1```text\n"+flow.rstrip()+"\n```",text,count=1)
        if n != 1:
            raise RuntimeError(f"flow block not found: {path}")
        text=new
        # generator runs before this script, so pages are fresh and should not yet contain input/output examples.
        if '## 输入示例' in text:
            raise RuntimeError(f"unexpected existing input section: {path}")
        if SOURCE_MARKER not in text:
            raise RuntimeError(f"source marker missing: {path}")
        text=text.replace(SOURCE_MARKER,input_section(p)+"## 穿过的源码文件\n",1)
        path.write_text(text,encoding='utf-8')
        count += 1
    if count != manifest['page_count']:
        raise RuntimeError((count,manifest['page_count']))
    print(f"Enriched {count} pages with detailed E2E v2 flows and input examples")

if __name__=='__main__':
    main()
