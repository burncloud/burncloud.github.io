from __future__ import annotations

from pathlib import Path
import argparse
import json
import re

FLOW_RE = re.compile(r"(## End-to-End Request Flow \+ ICFG\n\n)```text\n(.*?)\n```", re.S)
SOURCE_RE = re.compile(r"\n## 穿过的源码文件\n\n.*?(?=\n\*\*Execution classification:)", re.S)
PHASE_RE = re.compile(r"\[PHASE\s+\d{2}\]\s*")

HANDLERS = {
    "POST /api/auth/register":"create_user","POST /api/auth/login":"login","POST /api/auth/forgot-password":"forgot_password","POST /api/auth/reset-password":"reset_password","GET /api/auth/google":"oauth_google","GET /api/auth/github":"oauth_github",
    "GET /console/api/channel":"list_channels","POST /console/api/channel":"create_channel","PUT /console/api/channel":"update_channel","GET /console/api/channel/{id}":"get_channel","DELETE /console/api/channel/{id}":"delete_channel",
    "GET /console/api/tokens":"list_tokens","POST /console/api/tokens":"create_token","GET /console/api/tokens/{token}":"get_token","PUT /console/api/tokens/{token}":"update_token","DELETE /console/api/tokens/{token}":"delete_token","POST /console/api/tokens/{token}/rotate":"rotate_token","POST /console/api/tokens/{token}/revoke-old":"revoke_old_key","POST /console/api/tokens/{token}/ip-whitelist":"set_ip_whitelist",
    "POST /console/api/user/register":"register","POST /console/api/user/login":"login","POST /console/api/user/topup":"topup","GET /console/api/user/check_username":"check_username","GET /console/api/user/recharges":"list_recharges","GET /console/api/list_users":"list_users",
    "GET /api/billing/summary":"billing_summary_handler","GET /console/api/logs":"list_logs","GET /console/api/usage/{user_id}":"get_user_usage","GET /console/internal/billing/summary":"billing_summary_handler",
    "GET /console/api/monitor":"get_system_metrics","GET /console/api/monitor/security":"security_summary","GET /console/api/monitor/security/events":"security_events","GET /console/api/monitor/security/filters":"security_filters_get","PUT /console/api/monitor/security/filters":"security_filters_put","POST /console/api/monitor/security/emergency-circuit-break":"security_emergency_circuit_break","GET /console/api/monitor/security/circuit-breaker-status":"security_circuit_breaker_status",
    "GET /console/api/cache/stats":"stats","POST /console/api/cache/clear":"clear",
}

CHANNEL_METHOD = {"list_channels":("list","list"),"create_channel":("create","create"),"update_channel":("update","update"),"get_channel":("get_by_id","get_by_id"),"delete_channel":("delete","delete")}
TOKEN_METHOD = {"list_tokens":("list","list"),"create_token":("create","create"),"get_token":("validate","validate"),"update_token":("update_status","update_status"),"delete_token":("delete","delete"),"rotate_token":("rotate","rotate"),"revoke_old_key":("revoke_old_key","revoke_old_key"),"set_ip_whitelist":("set_ip_whitelist","set_ip_whitelist")}
USER_METHOD = {"register":("register_user","UserDatabase::get_user_by_username / count_users / create_user / assign_role"),"login":("login_user","UserDatabase::get_user_by_username"),"topup":("topup","UserDatabase::create_recharge / update_balance"),"check_username":("is_username_available","UserDatabase::get_user_by_username"),"list_recharges":("list_recharges","UserDatabase::list_recharges"),"list_users":("list_users / get_user_roles","UserDatabase::list_users / get_user_roles")}
AUTH_METHOD = {"create_user":("register_user → get_user_roles → generate_token","UserDatabase::get_user_by_username / count_users / create_user / assign_role / get_user_roles"),"login":("login_user → get_user_roles","UserDatabase::get_user_by_username / get_user_roles"),"forgot_password":("request_password_reset","PasswordResetDatabase + UserDatabase"),"reset_password":("reset_password","PasswordResetDatabase + UserDatabase"),"oauth_google":('oauth_url("google")',"环境变量 / URL 构造；无 DB 写入"),"oauth_github":('oauth_url("github")',"环境变量 / URL 构造；无 DB 写入")}


def exists(source: Path, rel: str) -> bool:
    return (source / rel).exists()


def clean_flow(flow: str) -> str:
    flow = PHASE_RE.sub("", flow)
    flow = flow.replace("back to PHASE 13", "返回 Candidate attempt loop")
    flow = flow.replace("back to PHASE 02", "返回等待边界")
    flow = re.sub(r"PHASE\s+\d{2}", "前述步骤", flow)
    return flow


def common_server(entry: str) -> str:
    return f"""START
│
├─ 调用方输入
│    ├─ Entry: {entry}
│    ├─ Method / Path / Query / Headers / Body
│    └─ DECISION: 请求到达 BurnCloud listener?
│         ├─ NO  → 网络层结束，应用代码不执行 → END
│         └─ YES → Axum Unified App
│
▼
FILE: crates/server/src/lib.rs
│
├─ start_server()（启动时）
│    ├─ create_default_database()
│    ├─ RouterDatabase::init()
│    ├─ UserDatabase::init()
│    ├─ create_app()
│    ├─ TcpListener::bind()
│    └─ axum::serve()
│
├─ create_app()
│    ├─ merge(api::routes(...))
│    ├─ merge(internal_app)
│    ├─ optional merge(liveview_router)
│    ├─ fallback_service(router_app)
│    └─ middleware: CORS / Trace / request-id
│
"""


def flow_channel(entry: str, handler: str):
    svc, model = CHANNEL_METHOD[handler]
    read = entry.startswith("GET ")
    extract = "Query<PaginationParams> → limit.clamp(1,100) / offset.max(0)" if handler == "list_channels" else ("Json<ChannelDto> → into_channel()" if handler in ("create_channel","update_channel") else "Path<i32> → channel id")
    invariant = "DECISION: channel.id == 0? → YES: err(\"id is required\")" if handler == "update_channel" else "继续"
    return common_server(entry) + f"""├─ DECISION: Management API route 命中?
│    ├─ NO  → 其它顶层路由 / fallback
│    └─ YES → api::routes()
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ routes()
│    ├─ merge(channel::routes()) into protected_routes
│    └─ layer(middleware::from_fn(crate::auth_middleware))
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ auth_middleware()
│    ├─ read Authorization
│    ├─ require Bearer prefix
│    ├─ verify_jwt()
│    └─ DECISION: JWT valid?
│         ├─ NO  → HTTP 401 → END
│         └─ YES → Claims inserted into request extensions
│
▼
FILE: crates/server/src/api/channel.rs
│
├─ routes() matches {entry}
├─ {handler}()
│    ├─ request extraction: {extract}
│    ├─ check_admin(&state, &claims)
│    └─ DECISION: admin role present?
│         ├─ NO  → err("Admin access required") → END
│         └─ YES → continue
│
├─ check_admin()
│    └─ CALL UserDatabase::get_user_roles(...)
│
▼
FILE: crates/database/crates/user/src/lib.rs
│
├─ UserDatabase::get_user_roles()
├─ DB connection / SQL role lookup
└─ return roles → channel.rs::check_admin()
│
▼
FILE: crates/server/src/api/channel.rs
│
├─ business invariant: {invariant}
└─ CALL ChannelService::{svc}(...)
│
▼
FILE: crates/service/crates/channel/src/lib.rs
│
├─ ChannelService::{svc}()
└─ CALL ChannelProviderModel::{model}(...)
│
▼
FILE: crates/database/crates/channel/src/channel_provider.rs
│
├─ ChannelProviderModel::{model}()
├─ db.get_connection() / SQL execution / row mapping
└─ DECISION: database operation successful?
     ├─ NO  → DatabaseError → service → handler → err(...)
     └─ YES → {'Vec<Channel>' if read else 'domain result'}
│
▼
FILE: crates/service/crates/channel/src/lib.rs
│
└─ return Result to channel handler
│
▼
FILE: crates/server/src/api/channel.rs
│
├─ DECISION: ChannelService result Ok?
│    ├─ NO  → err(e)
│    └─ YES → ok(domain/DTO)
└─ IntoResponse → HTTP response
│
▼
END
"""


def flow_token(entry: str, handler: str):
    svc, model = TOKEN_METHOD[handler]
    return common_server(entry) + f"""├─ DECISION: Management API route 命中?
│    ├─ NO → other route
│    └─ YES → protected_routes
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ merge(token::routes())
└─ auth_middleware wraps protected router
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ auth_middleware() → verify_jwt()
└─ DECISION: JWT valid?
     ├─ NO → HTTP 401 → END
     └─ YES → Claims → next
│
▼
FILE: crates/server/src/api/token.rs
│
├─ routes() matches {entry}
├─ {handler}()
├─ parse Path / Query / Json according to method
├─ validate token-specific fields / rotation / whitelist parameters
└─ CALL TokenService::{svc}(...)
│
▼
FILE: crates/service/crates/token/src/lib.rs
│
├─ TokenService::{svc}()
└─ CALL RouterTokenModel::{model}(...)
│
▼
FILE: crates/database/crates/router/src/token.rs
│
├─ RouterTokenModel::{model}()
├─ DB read/write + token state/rotation/quota fields
└─ DECISION: DB/token operation successful?
     ├─ NO → DatabaseError / not found / validation result
     └─ YES → RouterToken / bool / TokenRotationResult / ()
│
▼
FILE: crates/service/crates/token/src/lib.rs
│
└─ return Result to API handler
│
▼
FILE: crates/server/src/api/token.rs
│
├─ map result to ok(...) / err(...)
└─ return HTTP JSON response
│
▼
END
"""


def flow_user(entry: str, handler: str, public=False):
    if public:
        svc, dbops = AUTH_METHOD[handler]
        dbfile = "crates/database/crates/user/src/password_reset.rs" if handler in ("forgot_password","reset_password") else "crates/database/crates/user/src/lib.rs"
        return common_server(entry) + f"""├─ DECISION: public Authentication route 命中?
│    ├─ NO → protected/other route
│    └─ YES → public_routes（不经过 JWT middleware）
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ public_routes = auth::public_routes()
└─ merge public + protected routers
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ public_routes() matches {entry}
├─ {handler}()
├─ Axum Json/State extraction
└─ CALL UserService::{svc}
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ UserService operation: {svc}
├─ password hash/verify, JWT, OAuth/config logic as applicable
└─ persistence calls: {dbops}
│
▼
FILE: {dbfile}
│
├─ user/password-reset state read/write when this path needs persistence
└─ return database result
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ combine DB result with password/JWT/business rules
└─ DECISION: UserService operation successful?
     ├─ NO → typed UserServiceError
     └─ YES → user/token/reset/OAuth result
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ map success/error via ok(...) / err(...)
└─ return HTTP response
│
▼
END
"""
    svc, dbops = USER_METHOD[handler]
    return common_server(entry) + f"""├─ DECISION: protected User route 命中?
│    ├─ NO → other route
│    └─ YES → protected_routes
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ merge(user::routes())
└─ auth_middleware wraps protected router
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ auth_middleware() → verify_jwt()
└─ DECISION: JWT valid?
     ├─ NO → HTTP 401 → END
     └─ YES → Claims inserted
│
▼
FILE: crates/server/src/api/user.rs
│
├─ routes() matches {entry}
├─ {handler}()
├─ Path/Query/Json/Claims extraction
└─ CALL UserService::{svc}(...)
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ UserService::{svc}()
├─ password/JWT/balance/recharge logic as applicable
└─ DB calls: {dbops}
│
▼
FILE: crates/database/crates/user/src/lib.rs
│
├─ UserDatabase read/write
├─ db.get_connection() / SQL execution / row mapping
└─ DECISION: persistence operation successful?
     ├─ NO → DatabaseError → UserServiceError
     └─ YES → user/balance/roles/recharge result
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
└─ return domain result
│
▼
FILE: crates/server/src/api/user.rs
│
├─ map domain result to API response
└─ return HTTP JSON
│
▼
END
"""


def expand_proxy_flow(flow: str) -> str:
    # Make previously implicit crate crossings visible in the single master graph.
    marker = "├─ Account / quota guard"
    if marker not in flow:
        marker = "├─ Account / quota guard"
    insert_identity = """
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
"""
    # Insert after identity resolution block, before quota guard.
    idx = flow.find("├─ Account / quota guard")
    if idx >= 0 and "FILE: crates/database/crates/router/src/token.rs" not in flow:
        flow = flow[:idx] + insert_identity + flow[idx:]

    routing_marker = "├─ Candidate eligibility filtering"
    idx = flow.find(routing_marker)
    if idx >= 0 and "FILE: crates/router/src/model_router.rs" not in flow:
        insert = """
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
"""
        flow = flow[:idx] + insert + flow[idx:]

    preflight = "├─ Candidate attempt loop"
    idx = flow.find(preflight)
    if idx >= 0 and "FILE: crates/service/crates/billing/src/calculator.rs" not in flow:
        insert = """
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
"""
        flow = flow[:idx] + insert + flow[idx:]

    usage_marker = "├─ Unified usage + cost"
    idx = flow.find(usage_marker)
    if idx >= 0 and "FILE: crates/service/crates/billing/src/usage" not in flow:
        insert = """
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
"""
        flow = flow[:idx] + insert + flow[idx:]
    return flow


def base_table_files(text: str):
    m = SOURCE_RE.search(text)
    if not m: return []
    return re.findall(r"\|\s*\d+\s*\|\s*`([^`]+)`", m.group(0))


def chain_for(p, source: Path, text: str):
    section, group, entry = p["section"], p["group"], p["entry"]
    h = HANDLERS.get(entry)
    items = []
    def add(file, funcs, why, state):
        if file.endswith("/*") or exists(source,file):
            if not any(x[0] == file for x in items): items.append((file,funcs,why,state))

    if section == "HTTP / API":
        add("crates/server/src/lib.rs","start_server(), create_app()","统一 Server、Router 合并、Middleware、fallback 入口","READ runtime composition")
        if group == "Channel Management":
            svc, model = CHANNEL_METHOD[h]
            add("crates/server/src/api/mod.rs","routes()","把 channel::routes() 合并进 protected_routes","ROUTE")
            add("crates/server/src/api/auth.rs","auth_middleware(), verify_jwt()","JWT 认证并注入 Claims","READ auth header")
            add("crates/server/src/api/channel.rs",f"{h}(), check_admin()","参数、管理员授权、Handler 响应映射","READ/WRITE request domain")
            add("crates/database/crates/user/src/lib.rs","UserDatabase::get_user_roles()","check_admin() 的角色查询","READ user_roles")
            add("crates/service/crates/channel/src/lib.rs",f"ChannelService::{svc}()","Channel 业务层","SERVICE")
            add("crates/database/crates/channel/src/channel_provider.rs",f"ChannelProviderModel::{model}()","Channel 持久化 CRUD","READ/WRITE channel_providers")
        elif group == "Token":
            svc, model = TOKEN_METHOD[h]
            add("crates/server/src/api/mod.rs","routes()","protected route composition","ROUTE")
            add("crates/server/src/api/auth.rs","auth_middleware(), verify_jwt()","JWT authentication","READ auth")
            add("crates/server/src/api/token.rs",f"{h}()","Token Handler / request validation / response mapping","READ/WRITE token request")
            add("crates/service/crates/token/src/lib.rs",f"TokenService::{svc}()","Token business service","SERVICE")
            add("crates/database/crates/router/src/token.rs",f"RouterTokenModel::{model}()","Router token persistence","READ/WRITE router_tokens")
        elif group == "User":
            svc, _ = USER_METHOD[h]
            add("crates/server/src/api/mod.rs","routes()","protected route composition","ROUTE")
            add("crates/server/src/api/auth.rs","auth_middleware(), verify_jwt()","JWT authentication","READ auth")
            add("crates/server/src/api/user.rs",f"{h}()","User Handler / Claims / DTO","READ/WRITE request")
            add("crates/service/crates/user/src/lib.rs",f"UserService::{svc}()","User business logic","SERVICE")
            add("crates/database/crates/user/src/lib.rs","UserDatabase::*","user/role/balance/recharge persistence","READ/WRITE users")
        elif group == "Authentication":
            svc, dbops = AUTH_METHOD[h]
            add("crates/server/src/api/mod.rs","routes()","public auth routes outside JWT middleware","ROUTE")
            add("crates/server/src/api/auth.rs",f"{h}()","Auth DTO / Handler / response policy","REQUEST/RESPONSE")
            add("crates/service/crates/user/src/lib.rs",f"UserService::{svc}","password/JWT/OAuth/user business logic","SERVICE")
            if h in ("forgot_password","reset_password"):
                add("crates/database/crates/user/src/password_reset.rs","PasswordResetDatabase::*","reset token persistence","READ/WRITE password reset")
            add("crates/database/crates/user/src/lib.rs","UserDatabase::*","user/role persistence when applicable","READ/WRITE users")
        elif group == "AI API / Data Plane" and entry not in ("GET /v1/models","GET /api/v1/usage","GET /api/v1/usage/models") and not entry.startswith("GET /v1/videos/"):
            add("crates/router/src/lib.rs","create_router_app(), proxy_handler(), proxy_logic()","Admission + candidate loop + response settlement","HOT PATH")
            add("crates/database/crates/router/src/token.rs","RouterTokenModel::*","token/quota persistence behind RouterDatabase","READ/WRITE token state")
            add("crates/service/crates/user/src/lib.rs","UserService::resolve_traffic_class()","traffic class resolution","READ cache/user roles")
            add("crates/database/crates/user/src/lib.rs","UserDatabase::get_user_roles()","traffic class cache miss backing query","READ roles")
            add("crates/router/src/model_router.rs","ModelRouter::route_with_scheduler()","scheduler/candidate construction","DYNAMIC route decision")
            add("crates/router/src/affinity.rs","affinity cache/ranking symbols","session affinity input to scheduling","READ/WRITE affinity")
            add("crates/router/src/channel_state.rs","channel runtime state","candidate state input","READ runtime state")
            add("crates/router/src/circuit_breaker.rs","CircuitBreaker::*","per-candidate breaker admission/feedback","READ/WRITE breaker state")
            add("crates/router/src/aimd_limiter.rs","AIMD/rate-budget symbols","local shaping / feedback","READ/WRITE rate budget")
            add("crates/service/crates/billing/src/cache.rs","PriceCache::*","pricing lookup","READ price cache")
            add("crates/service/crates/billing/src/calculator.rs","CostCalculator::preflight(), calculate()","billing admission and settlement","READ price / compute cost")
            add("crates/router/src/passthrough.rs","should_passthrough(), passthrough helpers","native protocol/upstream boundary","NETWORK I/O")
            add("crates/router/src/adaptor/*","DynamicAdaptorFactory / provider adaptors","non-native protocol conversion","DYNAMIC Provider branch")
            add("crates/service/crates/billing/src/usage/*","UsageParser::*","provider usage normalization","READ response usage")
            add("crates/database/crates/router/src/log.rs","RouterLog/RequestLog persistence","accounting/audit persistence","WRITE logs")
        else:
            for f in base_table_files(text):
                add(f,"见上方 E2E 对应函数","该页面现有静态调用链中的源码文件","READ/WRITE depends on entry")
    else:
        for f in base_table_files(text):
            add(f,"见上方 E2E 对应函数/入口","该 CLI/UI/Background/Startup 页面真实执行文件","runtime-specific")
    return items


def source_section(items):
    lines = ["", "## 穿过的源码文件（详细）", "", "| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |", "|---:|---|---|---|---|"]
    for i,(f,funcs,why,state) in enumerate(items,1):
        funcs = funcs.replace("|","/"); why=why.replace("|","/"); state=state.replace("|","/")
        lines.append(f"| {i} | `{f}` | `{funcs}` | {why} | {state} |")
    lines += ["", "> 这个索引只列入当前执行链中有源码依据的文件；类型定义文件但不执行逻辑的，不为了凑数量加入。", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--manifest", default="docs/atlas-manifest.json")
    args = ap.parse_args()
    source = Path(args.source).resolve()
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    docs = Path(args.manifest).parent
    changed=0
    for p in manifest["pages"]:
        path = docs/(p["docid"]+".md")
        text = path.read_text(encoding="utf-8")
        m = FLOW_RE.search(text)
        if not m: raise RuntimeError(f"flow missing: {path}")
        flow = clean_flow(m.group(2))
        e,g,s = p["entry"],p["group"],p["section"]
        h = HANDLERS.get(e)
        if g == "Channel Management" and h:
            flow = flow_channel(e,h)
        elif g == "Token" and h:
            flow = flow_token(e,h)
        elif g == "User" and h:
            flow = flow_user(e,h,False)
        elif g == "Authentication" and h:
            flow = flow_user(e,h,True)
        elif s == "HTTP / API" and g == "AI API / Data Plane" and e not in ("GET /v1/models","GET /api/v1/usage","GET /api/v1/usage/models") and not e.startswith("GET /v1/videos/"):
            flow = expand_proxy_flow(flow)
        text = text[:m.start()] + m.group(1) + "```text\n" + flow.rstrip() + "\n```" + text[m.end():]
        items = chain_for(p,source,text)
        if not items: raise RuntimeError(f"no source traversal: {path}")
        sm = SOURCE_RE.search(text)
        if not sm: raise RuntimeError(f"source section missing: {path}")
        text = text[:sm.start()] + "\n" + source_section(items).rstrip() + "\n" + text[sm.end():]
        if re.search(r"\[PHASE\s+\d",text): raise RuntimeError(f"phase label remains: {path}")
        path.write_text(text,encoding="utf-8")
        changed += 1
    print(f"Deepened source traversal and removed PHASE labels on {changed} pages")

if __name__ == "__main__":
    main()
