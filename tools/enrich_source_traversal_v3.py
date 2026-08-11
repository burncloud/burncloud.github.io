from __future__ import annotations

from pathlib import Path
import argparse
import json
import re

FLOW_RE = re.compile(r"(## End-to-End Request Flow \+ ICFG\n\n)```text\n(.*?)\n```", re.S)
DETAIL_RE = re.compile(r"\n## 穿过的源码文件（详细）\n\n.*?(?=\n\*\*Execution classification:)", re.S)


def exists(src:Path,rel:str)->bool:
    if rel.endswith('/*'): return (src/rel[:-2]).is_dir()
    return (src/rel).is_file()


def row(file,symbols,why,state): return (file,symbols,why,state)


def parse_existing(text:str):
    m=DETAIL_RE.search(text)
    if not m:return []
    out=[]
    for line in m.group(0).splitlines():
        mm=re.match(r"\|\s*\d+\s*\|\s*`([^`]+)`\s*\|\s*`([^`]*)`\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$",line)
        if mm: out.append(tuple(x.strip() for x in mm.groups()))
    return out


def merge_rows(src,base,extra):
    out=[];seen=set()
    for r in base+extra:
        if r[0] in seen or not exists(src,r[0]): continue
        seen.add(r[0]);out.append(r)
    return out


def section(rows):
    lines=['','## 穿过的源码文件（详细）','',
           '| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |',
           '|---:|---|---|---|---|']
    for i,(f,s,w,st) in enumerate(rows,1):
        s=s.replace('|','/');w=w.replace('|','/');st=st.replace('|','/')
        lines.append(f'| {i} | `{f}` | `{s}` | {w} | {st} |')
    lines += ['', '> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。','']
    return '\n'.join(lines)


def insert_before(flow,needle,block):
    if block.strip() in flow:return flow
    i=flow.find(needle)
    if i<0:
        # fallback: insert before final END marker
        i=flow.rfind('\n▼\nEND')
    if i<0:return flow
    return flow[:i]+block.rstrip()+'\n│\n'+flow[i:]


def http_extra(p):
    g,e=p['group'],p['entry']
    x=[];block=''
    if g in ('Billing / Usage','Logs'):
        if e.startswith('GET /api/v1/usage'):
            x += [
                row('crates/router/src/lib.rs','usage_handler() / usage_models_handler()','Data Plane usage handler 与 token identity 解析','READ authenticated user'),
                row('crates/database/crates/router/src/lib.rs','get_usage_stats() / get_usage_stats_by_model()','Router DB facade 直接进入 usage aggregation','READ router_logs'),
                row('crates/database/crates/router/src/log.rs','get_usage_stats() / get_usage_stats_by_model()','执行时间范围与 model 聚合 SQL','READ router_logs'),
            ]
            block='''▼
FILE: crates/database/crates/router/src/lib.rs
│
├─ get_usage_stats(...) / get_usage_stats_by_model(...)
└─ delegate to router log aggregation
│
▼
FILE: crates/database/crates/router/src/log.rs
│
├─ build period boundary / aggregation SQL
├─ query router_logs for current user
└─ DECISION: SQL succeeds?
     ├─ NO → DatabaseError → handler error response
     └─ YES → UsageStats / Vec<ModelUsageStats>'''
        elif '/api/billing/summary' in e:
            x += [
                row('crates/server/src/api/billing.rs','billing_summary_handler()','从 Claims.sub + start/end 进入 BillingService','READ request/JWT'),
                row('crates/service/crates/router-log/src/lib.rs','BillingService::get_billing_summary_for_user()','真实 BillingService 实现；service-billing 仅做 re-export','READ billing domain'),
                row('crates/database/crates/router/src/log.rs','get_billing_summary_for_user()','按 user_id 和时间范围聚合模型请求/Token/成本','READ router_logs'),
            ]
            block='''▼
FILE: crates/service/crates/router-log/src/lib.rs
│
├─ BillingService::get_billing_summary_for_user(db, claims.sub, start, end)
└─ CALL burncloud_database_router::get_billing_summary_for_user(...)
│
▼
FILE: crates/database/crates/router/src/log.rs
│
├─ build user/time filtered billing aggregation
├─ aggregate per-model request/token/cost state
└─ DECISION: billing SQL succeeds?
     ├─ NO → DatabaseError → BillingService → err(...)
     └─ YES → BillingSummary → API handler'''
        elif '/console/internal/billing/summary' in e:
            x += [
                row('crates/server/src/api/log.rs','billing_summary_handler(), billing_summary_inner()','可选 internal secret 检查并请求全局 billing summary','READ header/env'),
                row('crates/service/crates/router-log/src/lib.rs','BillingService::get_billing_summary()','Billing aggregation service','READ billing domain'),
                row('crates/database/crates/router/src/log.rs','get_billing_summary()','全局时间范围聚合 SQL','READ router_logs'),
            ]
            block='''▼
FILE: crates/server/src/api/log.rs
│
├─ billing_summary_inner()
├─ DECISION: BURNCLOUD_INTERNAL_SECRET configured?
│    ├─ YES → x-internal-secret must match or HTTP 401
│    └─ NO  → no extra internal-secret rejection
└─ BillingService::get_billing_summary(...)
│
▼
FILE: crates/service/crates/router-log/src/lib.rs
│
└─ BillingService::get_billing_summary() → database router
│
▼
FILE: crates/database/crates/router/src/log.rs
│
├─ aggregate billing state from router_logs
└─ return BillingSummary'''
        elif '/console/api/logs' in e:
            x += [row('crates/server/src/api/log.rs','list_logs()','分页参数转 limit/offset','READ query'),row('crates/service/crates/router-log/src/lib.rs','RouterLogService::get()','Router log service','READ logs'),row('crates/database/crates/router/src/log.rs','RouterLogModel::get()','分页 SQL 和 row mapping','READ router_logs')]
            block='''▼
FILE: crates/service/crates/router-log/src/lib.rs
│
├─ RouterLogService::get(db, page_size, offset)
└─ RouterLogModel::get(...)
│
▼
FILE: crates/database/crates/router/src/log.rs
│
├─ query router_logs with pagination
└─ DECISION: DB query succeeds?
     ├─ NO → ApiError
     └─ YES → Vec<RouterLog> → LogPage'''
        elif '/console/api/usage/' in e:
            x += [row('crates/server/src/api/log.rs','get_user_usage()','Path user_id → usage service','READ path'),row('crates/service/crates/router-log/src/lib.rs','RouterLogService::get_usage_by_user()','User usage service','READ logs'),row('crates/database/crates/router/src/log.rs','RouterLogModel::get_usage_by_user()','SUM prompt/completion tokens','READ router_logs')]
            block='''▼
FILE: crates/service/crates/router-log/src/lib.rs
│
└─ RouterLogService::get_usage_by_user(db, user_id)
│
▼
FILE: crates/database/crates/router/src/log.rs
│
├─ SUM prompt_tokens / completion_tokens for user_id
└─ return tuple → handler calculates total_tokens'''
    elif g=='Monitoring / Security':
        if e=='GET /console/api/monitor':
            x += [row('crates/server/src/api/monitor.rs','get_system_metrics()','调用 AppState.monitor','READ monitor cache'),row('crates/service/crates/monitor/src/service.rs','SystemMonitorService::get_metrics(), collect_fresh_metrics(), collect_metrics_internal()','先读缓存，过期则并行采集 CPU/Memory/Disk','READ/WRITE in-memory metrics cache'),row('crates/service/crates/monitor/src/collectors/cpu.rs','CpuCollector::collect()','CPU metrics collector','READ OS metrics'),row('crates/service/crates/monitor/src/collectors/memory.rs','MemoryCollector::collect()','Memory metrics collector','READ OS metrics'),row('crates/service/crates/monitor/src/collectors/disk.rs','DiskCollector::collect_all()','Disk metrics collector','READ OS metrics')]
            block='''▼
FILE: crates/service/crates/monitor/src/service.rs
│
├─ SystemMonitorService::get_metrics()
├─ DECISION: cached_metrics exists and still fresh?
│    ├─ YES → return cached clone
│    └─ NO  → collect_fresh_metrics()
│         └─ collect_metrics_internal()
│              └─ tokio::join!(CPU, Memory, Disk)
│
▼
FILE: crates/service/crates/monitor/src/collectors/cpu.rs
│
└─ CpuCollector::collect()
│
▼
FILE: crates/service/crates/monitor/src/collectors/memory.rs
│
└─ MemoryCollector::collect()
│
▼
FILE: crates/service/crates/monitor/src/collectors/disk.rs
│
└─ DiskCollector::collect_all()
│
▼
FILE: crates/service/crates/monitor/src/service.rs
│
└─ update cached_metrics → return SystemMetrics'''
        elif e.endswith('/security') or e.endswith('/security/events'):
            x += [row('crates/server/src/api/security.rs','security_summary() / security_events()','读取 RouterLog 后派生 security 视图','READ derived security view'),row('crates/service/crates/router-log/src/lib.rs','RouterLogService::get()','读取近期 RouterLog','READ logs'),row('crates/database/crates/router/src/log.rs','RouterLogModel::get()','查询 router_logs','READ router_logs')]
            block='''▼
FILE: crates/service/crates/router-log/src/lib.rs
│
└─ RouterLogService::get(...) → RouterLogModel::get(...)
│
▼
FILE: crates/database/crates/router/src/log.rs
│
└─ read router_logs
│
▼
FILE: crates/server/src/api/security.rs
│
├─ summary: compute_security_score() + compute_sparkline()
└─ events: filter status >= 400 → log_to_risk_event() → paginate'''
        elif e.endswith('/security/filters'):
            x += [row('crates/server/src/api/security.rs','security_filters_get() / security_filters_put()','直接读取/写入 sys_settings.security_filters','READ/WRITE settings'),row('crates/database/src/lib.rs','Database::query_with_params() / execute_query_with_params()','数据库抽象执行 settings SQL','READ/WRITE sys_settings')]
            block='''▼
FILE: crates/server/src/api/security.rs
│
├─ DECISION: GET or PUT filters?
│    ├─ GET → Database::query_with_params(SELECT sys_settings)
│    │    └─ empty / invalid JSON → FilterConfig::default()
│    └─ PUT → serde_json::to_string(config)
│         └─ Database::execute_query_with_params(INSERT OR REPLACE)
│
▼
FILE: crates/database/src/lib.rs
│
└─ execute parameterized SQL against sys_settings'''
        elif 'emergency-circuit-break' in e:
            x += [row('crates/server/src/api/security.rs','security_emergency_circuit_break(), post_router_internal()','本地 loopback POST 到 Router internal endpoint','NETWORK localhost'),row('crates/router/src/lib.rs','circuit_breaker_trip_all_handler()','接收内部 trip-all 请求','WRITE breaker state'),row('crates/router/src/circuit_breaker.rs','CircuitBreaker::trip_all()','打开已知 upstream circuits','WRITE circuit state')]
            block='''▼
FILE: crates/server/src/api/security.rs
│
├─ validate reason non-empty
├─ post_router_internal("/console/internal/circuit-breaker/trip-all", body)
├─ build http://127.0.0.1:{PORT} URL
└─ optional X-Internal-Secret header
│
▼
FILE: crates/router/src/lib.rs
│
└─ circuit_breaker_trip_all_handler()
│
▼
FILE: crates/router/src/circuit_breaker.rs
│
└─ trip_all() mutates known breaker states'''
        elif 'circuit-breaker-status' in e:
            x += [row('crates/server/src/api/security.rs','security_circuit_breaker_status(), call_router_internal()','本地 GET internal health','NETWORK localhost'),row('crates/router/src/lib.rs','health_status_handler()','读取 Router runtime health/circuit state','READ runtime state'),row('crates/router/src/circuit_breaker.rs','breaker state access','health payload source之一','READ circuit state')]
            block='''▼
FILE: crates/server/src/api/security.rs
│
├─ call_router_internal("/console/internal/health")
├─ localhost reqwest GET
└─ optional X-Internal-Secret
│
▼
FILE: crates/router/src/lib.rs
│
└─ health_status_handler() builds runtime health JSON'''
    elif g=='Cache':
        x += [row('crates/server/src/api/cache.rs','stats() / clear()','Management cache handler','READ/WRITE cache request'),row('crates/service/crates/cache/src/service.rs','CacheService::stats() / clear_all() / get_connection()','Redis cache implementation','READ/WRITE Redis bc:* keys')]
        block='''▼
FILE: crates/service/crates/cache/src/service.rs
│
├─ DECISION: CacheService available / Redis connected?
│    ├─ NO → disabled/empty semantics or CacheError
│    └─ YES → ConnectionManager
├─ stats(): read Redis INFO/dbsize-like statistics
└─ clear_all(): KEYS "bc:*" → DECISION keys empty? → DEL matching keys'''
    elif g=='Admin / Internal':
        if 'prices/sync' in e:
            x += [row('crates/router/src/lib.rs','price_sync_handler()','发送 force_sync oneshot 请求','ASYNC control'),row('crates/router/src/price_sync.rs','PriceSyncService / start_price_sync_task()','价格同步实现','READ/WRITE price state')]
        elif 'trip-all' in e:
            x += [row('crates/router/src/lib.rs','circuit_breaker_trip_all_handler()','内部控制入口','WRITE breaker'),row('crates/router/src/circuit_breaker.rs','trip_all()','breaker 状态变更','WRITE runtime breaker state')]
        elif e.endswith('/health') or e.endswith('/metrics'):
            x += [row('crates/router/src/lib.rs','health_status_handler() / metrics_handler()','内部 runtime introspection','READ router runtime'),row('crates/router/src/circuit_breaker.rs','breaker snapshot','health/metrics input','READ'),row('crates/router/src/channel_state.rs','channel state snapshot','health input','READ')]
    elif g=='AI API / Data Plane':
        if e=='GET /v1/models':
            x += [row('crates/database/crates/channel/src/channel_ability.rs','ChannelAbilityModel::list_distinct_models()','enabled abilities DISTINCT model SQL','READ channel_abilities')]
        elif e=='GET /api/v1/usage' or e=='GET /api/v1/usage/models':
            x += [row('crates/database/crates/router/src/lib.rs','validate_token_and_get_info(), get_usage_stats*()','identity + usage facade','READ user/token/log state'),row('crates/database/crates/router/src/log.rs','get_usage_stats*()','usage aggregation SQL','READ router_logs')]
        elif e.startswith('GET /v1/videos/'):
            x += [row('crates/database/crates/router/src/router_video_task.rs','RouterVideoTaskModel::get_by_task_id()','task_id → original channel mapping','READ router_video_tasks'),row('crates/database/crates/channel/src/channel_provider.rs','ChannelProviderModel::get_by_id()','load original channel base_url/key','READ channel_providers')]
    elif g=='Web UI / LiveView / WebSocket':
        x += [row('crates/client/src/lib.rs','liveview_router(), LiveViewPool::launch()','HTML shell/WS upgrade/LiveView launch','NETWORK websocket'),row('crates/client/src/app.rs','App(), Route','LiveView launches Dioxus root','UI runtime')]
    return x,block


def cli_extra(p):
    e=p['entry'];x=[];block=''
    if not e.startswith('burncloud '): return x,block
    if ' price ' in e:
        x += [row('crates/database/crates/billing/src/billing_price.rs','BillingPriceModel::*','price CLI 直接 CRUD billing_prices','READ/WRITE billing_prices')]
        block='''▼
FILE: crates/database/crates/billing/src/billing_price.rs
│
├─ BillingPriceModel operation selected by price subcommand
├─ execute pricing SQL / row mapping
└─ return price domain data → CLI formatter'''
    elif ' tiered ' in e:
        x += [row('crates/database/crates/billing/src/billing_tiered_price.rs','BillingTieredPriceModel::*','tiered pricing CRUD','READ/WRITE billing tiered prices')]
        block='''▼
FILE: crates/database/crates/billing/src/billing_tiered_price.rs
│
└─ BillingTieredPriceModel operation → DB result'''
    elif ' protocol ' in e:
        x += [row('crates/database/crates/channel/src/channel_protocol_config.rs','ChannelProtocolConfigModel::*','protocol config persistence','READ/WRITE channel protocol configs')]
        block='''▼
FILE: crates/database/crates/channel/src/channel_protocol_config.rs
│
├─ ChannelProtocolConfigModel::{list/get/upsert/delete...}
└─ SQL state → CLI output'''
    elif ' channel ' in e:
        x += [row('crates/service/crates/channel/src/lib.rs','ChannelService::*','CLI channel business service','SERVICE'),row('crates/database/crates/channel/src/channel_provider.rs','ChannelProviderModel::*','channel persistence','READ/WRITE channel_providers')]
        block='''▼
FILE: crates/service/crates/channel/src/lib.rs
│
└─ ChannelService operation
│
▼
FILE: crates/database/crates/channel/src/channel_provider.rs
│
└─ ChannelProviderModel CRUD → DB result'''
    elif ' token ' in e:
        x += [row('crates/service/crates/token/src/lib.rs','TokenService::*','CLI token service','SERVICE'),row('crates/database/crates/router/src/token.rs','RouterTokenModel::*','token persistence','READ/WRITE router_tokens')]
        block='''▼
FILE: crates/service/crates/token/src/lib.rs
│
└─ TokenService operation
│
▼
FILE: crates/database/crates/router/src/token.rs
│
└─ RouterTokenModel operation → DB result'''
    elif ' user ' in e:
        x += [row('crates/service/crates/user/src/lib.rs','UserService::*','CLI user business logic','SERVICE'),row('crates/database/crates/user/src/lib.rs','UserDatabase::*','user/role/recharge persistence','READ/WRITE users')]
        block='''▼
FILE: crates/service/crates/user/src/lib.rs
│
└─ UserService operation
│
▼
FILE: crates/database/crates/user/src/lib.rs
│
└─ UserDatabase operation → domain result'''
    elif ' log ' in e:
        x += [row('crates/service/crates/router-log/src/lib.rs','RouterLogService::*','CLI log/usage service','READ logs'),row('crates/database/crates/router/src/log.rs','RouterLogModel::*','log persistence/query','READ router_logs')]
        block='''▼
FILE: crates/service/crates/router-log/src/lib.rs
│
└─ RouterLogService query
│
▼
FILE: crates/database/crates/router/src/log.rs
│
└─ RouterLogModel / aggregation SQL'''
    elif ' currency ' in e:
        x += [row('crates/database/src/lib.rs','Database::get_connection()','currency CLI uses direct sqlx queries','READ/WRITE billing_exchange_rates')]
        block='''▼
FILE: crates/database/src/lib.rs
│
├─ Database::get_connection()
└─ src/cli/currency.rs executes parameterized SQL against billing_exchange_rates'''
    elif ' monitor status' in e:
        x += [row('crates/database/crates/channel/src/channel_provider.rs','ChannelProviderModel::list()','channel count','READ channel_providers'),row('crates/database/src/lib.rs','Database::get_connection()','today statistics direct SQL','READ router_logs')]
        block='''▼
FILE: crates/database/crates/channel/src/channel_provider.rs
│
└─ ChannelProviderModel::list() → total/active channel counts
│
▼
FILE: crates/database/src/lib.rs
│
└─ direct SQL for today's requests/tokens/revenue'''
    return x,block

UI_MAP={
 '/':('crates/client/src/pages/home.rs','Root / Home page module',None),
 '/home':('crates/client/src/pages/home.rs','HomePage',None),
 '/login':('crates/client/src/pages/login.rs','LoginPage',None),
 '/register':(None,'RegisterPage','crates/client/crates/client-register/src/lib.rs'),
 '/forgot-password':('crates/client/src/pages/forgot_password.rs','ForgotPasswordPage',None),
 '/reset-password?:token':('crates/client/src/pages/reset_password.rs','ResetPasswordPage',None),
 '/console/dashboard':('crates/client/src/pages/dashboard.rs','Dashboard re-export','crates/client/crates/client-dashboard/src/lib.rs'),
 '/console/deploy':('crates/client/src/pages/deploy.rs','DeployConfig re-export','crates/client/crates/client-deploy/src/lib.rs'),
 '/console/monitor':('crates/client/src/pages/monitor.rs','ServiceMonitor re-export','crates/client/crates/client-monitor/src/lib.rs'),
 '/console/access':('crates/client/src/pages/api.rs','AccessPage re-export','crates/client/crates/client-access/src/lib.rs'),
 '/console/models':('crates/client/src/pages/models.rs','ChannelPage re-export','crates/client/crates/client-models/src/lib.rs'),
 '/console/users':('crates/client/src/pages/user.rs','UsersPage re-export','crates/client/crates/client-users/src/lib.rs'),
 '/console/settings':('crates/client/src/pages/settings.rs','SystemSettings re-export','crates/client/crates/client-settings/src/lib.rs'),
 '/console/finance':('crates/client/src/pages/billing.rs','FinancePage re-export','crates/client/crates/client-finance/src/lib.rs'),
 '/console/logs':('crates/client/src/pages/logs.rs','LogPage re-export','crates/client/crates/client-log/src/lib.rs'),
 '/console/connect':('crates/client/src/pages/connect.rs','ConnectPage re-export','crates/client/crates/client-connect/src/lib.rs'),
 '/console/playground':('crates/client/src/pages/playground.rs','PlaygroundPage re-export','crates/client/crates/client-playground/src/lib.rs'),
 '/console/:..segments → NotFound':('crates/client/src/pages/not_found.rs','NotFoundPage',None),
}


def ui_extra(p,src):
    e=p['entry'];x=[];block=''
    if e.startswith('/preview/'):
        x += [row('crates/client/src/pages/e2e_preview.rs','Preview*Page components','debug/e2e-preview route component implementation','UI render')]
        block='''▼
FILE: crates/client/src/pages/e2e_preview.rs
│
└─ selected Preview*Page component renders deterministic preview state'''
        return x,block
    if e in UI_MAP:
        wrapper,symbol,impl=UI_MAP[e]
        if e.startswith('/console/'):
            x += [row('crates/client/src/components/layout.rs','Layout','console Route layout wrapper','UI layout/auth/navigation'),row('crates/client/crates/client-shared/src/components/layout.rs','shared Layout/navigation helpers','shared console layout behavior','UI state')]
        elif e not in ('/',):
            x += [row('crates/client/src/components/guest_layout.rs','GuestLayout','guest route layout wrapper','UI layout')]
        if wrapper: x.append(row(wrapper,symbol,'Route enum 选择的页面模块/重导出','UI component'))
        if impl: x.append(row(impl,symbol.replace(' re-export',''),'实际页面组件 crate','UI component/effects'))
        parts=[]
        if e.startswith('/console/'):
            parts += ['▼\nFILE: crates/client/src/components/layout.rs\n│\n└─ Layout wraps console page / navigation / shared contexts']
        if wrapper: parts += [f'▼\nFILE: {wrapper}\n│\n└─ {symbol}']
        if impl and exists(src,impl): parts += [f'▼\nFILE: {impl}\n│\n└─ actual page component implementation / local effects']
        block='\n│\n'.join(parts)
    return x,block


def background_extra(p):
    t=p['title'];x=[];block=''
    maps={
      'System Monitor Auto Update':[row('crates/service/crates/monitor/src/service.rs','SystemMonitorService::start_auto_update(), collect_metrics_internal()','1s ticker + metrics cache update','WRITE cached_metrics'),row('crates/service/crates/monitor/src/collectors/cpu.rs','CpuCollector::collect()','CPU collection','READ OS'),row('crates/service/crates/monitor/src/collectors/memory.rs','MemoryCollector::collect()','memory collection','READ OS'),row('crates/service/crates/monitor/src/collectors/disk.rs','DiskCollector::collect_all()','disk collection','READ OS')],
      'Async Router Log Writer':[row('crates/database/crates/router/src/log.rs','RouterLogModel::insert()','background log persistence','WRITE router_logs')],
      'Async Request Log Writer':[row('crates/database/crates/router/src/log.rs','RouterRequestLogModel::insert()','background request log persistence','WRITE request logs')],
      'Token accessed_time update':[row('crates/database/crates/router/src/token.rs','RouterTokenModel::update_accessed_time()','request-side async token touch','WRITE token accessed_time')],
      'Quota deduction':[row('crates/database/crates/router/src/token.rs','RouterTokenModel::deduct_quota()','post-response async quota state mutation','WRITE token quota')],
      'Video task mapping save':[row('crates/database/crates/router/src/router_video_task.rs','RouterVideoTaskModel::save()','persist video task → channel mapping','WRITE router_video_tasks')],
      'Download progress monitor':[row('crates/download/crates/download-aria2/src/lib.rs','Aria2RpcClient::tell_status()','poll aria2 task status','NETWORK localhost RPC')],
    }
    x += maps.get(t,[])
    return x,block


def startup_extra(p):
    t=p['title'];x=[]
    if t=='create_app':
        x += [row('crates/service/crates/monitor/src/service.rs','SystemMonitorService::new(), start_auto_update()','server monitor initialization','SPAWN monitor'),row('crates/service/crates/cache/src/service.rs','CacheService::new()','cache initialization / optional Redis ping','NETWORK Redis'),row('crates/router/src/lib.rs','create_router_app()','data-plane runtime construction','INIT router'),row('crates/client/src/lib.rs','liveview_router()','optional LiveView route construction','INIT UI routes')]
    elif t=='create_router_app':
        x += [row('crates/router/src/model_router.rs','ModelRouter::*','scheduler/model route engine','INIT routing'),row('crates/router/src/circuit_breaker.rs','CircuitBreaker::*','breaker state','INIT runtime state'),row('crates/router/src/affinity.rs','affinity cache','session/channel affinity','INIT cache'),row('crates/router/src/channel_state.rs','channel state','channel runtime state','INIT state'),row('crates/router/src/aimd_limiter.rs','AIMD limiter','rate budget state','INIT state'),row('crates/router/src/price_sync.rs','start_price_sync_task()','price sync background task','SPAWN'),row('crates/router/src/exchange_rate.rs','start_sync_task()','exchange-rate background task','SPAWN'),row('crates/service/crates/billing/src/cache.rs','PriceCache::*','pricing cache','INIT/read'),row('crates/service/crates/billing/src/calculator.rs','CostCalculator::*','billing calculation engine','INIT/use')]
    return x,''


def enrich_flow(flow,section_name,group,block):
    if not block:return flow
    if section_name=='CLI / Executables': return insert_before(flow,'├─ Output formatting',block)
    if section_name=='UI-only Actions': return insert_before(flow,'├─ Component construction',block)
    if section_name=='HTTP / API': return insert_before(flow,'├─ Response mapping',block)
    return insert_before(flow,'\n▼\nEND',block)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',required=True);ap.add_argument('--manifest',default='docs/atlas-manifest.json');args=ap.parse_args()
    src=Path(args.source).resolve();mp=Path(args.manifest);docs=mp.parent;manifest=json.loads(mp.read_text(encoding='utf-8'));changed=0;deepened=0
    for p in manifest['pages']:
        path=docs/(p['docid']+'.md');text=path.read_text(encoding='utf-8');base=parse_existing(text);extra=[];block=''
        if p['section']=='HTTP / API': extra,block=http_extra(p)
        elif p['section']=='CLI / Executables': extra,block=cli_extra(p)
        elif p['section']=='UI-only Actions': extra,block=ui_extra(p,src)
        elif p['section']=='Background Jobs / Async Side Effects': extra,block=background_extra(p)
        elif p['section']=='Startup': extra,block=startup_extra(p)
        if not extra and not block: continue
        fm=FLOW_RE.search(text)
        if fm and block:
            flow=enrich_flow(fm.group(2),p['section'],p['group'],block)
            text=text[:fm.start()]+fm.group(1)+'```text\n'+flow.rstrip()+'\n```'+text[fm.end():]
            deepened+=1
        rows=merge_rows(src,base,extra)
        sm=DETAIL_RE.search(text)
        if not sm: raise RuntimeError(f'detailed source section missing: {path}')
        text=text[:sm.start()]+'\n'+section(rows).rstrip()+'\n'+text[sm.end():]
        path.write_text(text,encoding='utf-8');changed+=1
    print(f'Updated source traversal on {changed} pages; injected explicit FILE call-chain blocks on {deepened} pages')

if __name__=='__main__': main()
