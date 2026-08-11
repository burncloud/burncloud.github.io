from pathlib import Path
import json,re

MANIFEST=Path('docs/atlas-manifest.json')
DETAIL_RE=re.compile(r'\n## 穿过的源码文件（详细）\n\n.*?(?=\n\*\*Execution classification:)',re.S)
ROW_RE=re.compile(r'^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*`([^`]*)`\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$')

BASE={
 'crates/server/src/lib.rs':('start_server(), create_app()','统一 HTTP Server / App composition / fallback','INIT + request routing'),
 'crates/server/src/api/mod.rs':('routes()','Public/Protected Management route composition','ROUTE composition'),
 'crates/server/src/api/auth.rs':('auth_middleware(), verify_jwt(), public_routes()','JWT middleware 与 public authentication routes','READ Authorization / Claims'),
 'crates/router/src/lib.rs':('create_router_app(), proxy_handler(), proxy_logic()','Data Plane 主控制流或 Router internal handler','READ/WRITE router runtime'),
 'crates/client/src/lib.rs':('liveview_router(), LiveViewPool::launch()','LiveView HTTP shell / WebSocket router','NETWORK/UI runtime'),
 'crates/client/src/app.rs':('App(), Route, launch_gui_with_tray()','Dioxus root/router/desktop runtime','UI state'),
 'crates/client/crates/client-shared/src/components/layout.rs':('Layout / shared navigation helpers','Console shared layout implementation','UI layout/navigation state'),
 'src/main.rs':('main()','BurnCloud process bootstrap / top-level dispatch','PROCESS'),
 'src/cli/commands.rs':('command(), CLI dispatch','Clap command tree + subcommand dispatch','ARGV'),
 'src/cli/channel.rs':('handle_channel_command()','Channel CLI implementation','CLI → service/DB'),
 'src/cli/price.rs':('handle_price_command() / tiered pricing branches','Price and tiered-pricing CLI implementation','CLI → billing DB'),
 'src/cli/token.rs':('handle_token_command()','Token CLI implementation','CLI → TokenService'),
 'src/cli/protocol.rs':('handle_protocol_command()','Protocol config CLI implementation','CLI → channel protocol DB'),
 'src/cli/currency.rs':('handle_currency_command()','Exchange-rate CLI; includes direct SQL','READ/WRITE billing_exchange_rates'),
 'src/cli/user.rs':('handle_user_command()','User CLI implementation','CLI → UserService'),
 'src/cli/log.rs':('handle_log_command()','Log/usage CLI implementation','CLI → RouterLogService'),
 'src/cli/monitor.rs':('cmd_monitor_status(), cmd_monitor_server()','System/server monitor CLI','READ DB/OS process state'),
 'crates/service/crates/channel/src/lib.rs':('ChannelService::*','Channel service boundary','SERVICE'),
 'crates/service/crates/token/src/lib.rs':('TokenService::*','Token service boundary','SERVICE'),
 'crates/service/crates/user/src/lib.rs':('UserService::*','User/auth business service','SERVICE'),
 'crates/service/crates/router-log/src/lib.rs':('RouterLogService::*, BillingService::*','Router log / usage / billing summary service','SERVICE'),
 'crates/service/crates/cache/src/service.rs':('CacheService::*','Redis-backed cache implementation','READ/WRITE Redis'),
 'crates/service/crates/monitor/src/service.rs':('SystemMonitorService::*','metrics cache + collector coordination','READ OS / WRITE memory cache'),
 'crates/database/crates/channel/src/channel_provider.rs':('ChannelProviderModel::*','Channel provider persistence','READ/WRITE channel_providers'),
 'crates/database/crates/channel/src/channel_ability.rs':('ChannelAbilityModel::*','Model/group/channel ability persistence','READ/WRITE channel_abilities'),
 'crates/database/crates/channel/src/channel_protocol_config.rs':('ChannelProtocolConfigModel::*','Protocol configuration persistence','READ/WRITE channel protocol configs'),
 'crates/database/crates/router/src/token.rs':('RouterTokenModel::*','Router token/quota/key persistence','READ/WRITE router token state'),
 'crates/database/crates/router/src/log.rs':('RouterLogModel::* / usage & billing queries','Request accounting / usage / billing persistence','READ/WRITE router_logs'),
 'crates/database/crates/router/src/router_video_task.rs':('RouterVideoTaskModel::*','Video task → channel mapping persistence','READ/WRITE video task mapping'),
 'crates/database/crates/user/src/lib.rs':('UserDatabase::*','User/role/recharge persistence','READ/WRITE user state'),
 'crates/database/crates/user/src/password_reset.rs':('PasswordResetDatabase::*','Password reset token persistence','READ/WRITE reset state'),
 'crates/database/crates/billing/src/billing_price.rs':('BillingPriceModel::*','Model price persistence','READ/WRITE billing prices'),
 'crates/database/crates/billing/src/billing_tiered_price.rs':('BillingTieredPriceModel::*','Tiered price persistence','READ/WRITE tiered prices'),
 'crates/database/src/lib.rs':('Database::get_connection(), query/execute helpers','Core database abstraction','SQL boundary'),
}

ENTRY_SYMBOLS={
 ('crates/server/src/api/billing.rs','GET /api/billing/summary'):('billing_summary_handler()','Billing summary Handler：Claims.sub + start/end → BillingService','READ JWT/query'),
 ('crates/server/src/api/log.rs','GET /console/api/logs'):('list_logs()','分页读取 RouterLog','READ query/logs'),
 ('crates/server/src/api/log.rs','GET /console/api/usage/{user_id}'):('get_user_usage()','按 Path user_id 汇总 token usage','READ path/logs'),
 ('crates/server/src/api/log.rs','GET /console/internal/billing/summary'):('billing_summary_handler(), billing_summary_inner()','可选 internal secret + 全局 billing summary','READ header/env/logs'),
 ('crates/server/src/api/monitor.rs','GET /console/api/monitor'):('get_system_metrics()','读取 SystemMonitorService 指标','READ monitor cache/OS metrics'),
 ('crates/server/src/api/cache.rs','GET /console/api/cache/stats'):('stats()','读取 CacheService stats','READ Redis/cache state'),
 ('crates/server/src/api/cache.rs','POST /console/api/cache/clear'):('clear()','调用 CacheService::clear_all()','WRITE Redis/cache state'),
 ('crates/server/src/api/security.rs','GET /console/api/monitor/security'):('security_summary(), compute_security_score(), compute_sparkline()','RouterLog → SecuritySummary 派生','READ logs'),
 ('crates/server/src/api/security.rs','GET /console/api/monitor/security/events'):('security_events(), log_to_risk_event()','RouterLog error rows → RiskEvent','READ logs'),
 ('crates/server/src/api/security.rs','GET /console/api/monitor/security/filters'):('security_filters_get()','读取 sys_settings.security_filters','READ sys_settings'),
 ('crates/server/src/api/security.rs','PUT /console/api/monitor/security/filters'):('security_filters_put()','写入 sys_settings.security_filters','WRITE sys_settings'),
 ('crates/server/src/api/security.rs','POST /console/api/monitor/security/emergency-circuit-break'):('security_emergency_circuit_break(), post_router_internal()','loopback POST Router trip-all','NETWORK localhost / WRITE breaker'),
 ('crates/server/src/api/security.rs','GET /console/api/monitor/security/circuit-breaker-status'):('security_circuit_breaker_status(), call_router_internal()','loopback GET Router health','NETWORK localhost / READ runtime state'),
 ('crates/server/src/api/openapi.rs','GET /api-docs/openapi.json'):('openapi_json()','构造并返回 OpenAPI JSON','RESPONSE generation'),
 ('crates/server/src/api/openapi.rs','GET /swagger-ui'):('swagger_ui()','返回 Swagger UI HTML shell','RESPONSE HTML'),
 ('crates/server/src/api/openapi.rs','GET /swagger-ui/'):('swagger_ui()','返回 Swagger UI HTML shell','RESPONSE HTML'),
}


def defaults(file,old_s,old_w,old_st,p):
    key=(file,p['entry'])
    if key in ENTRY_SYMBOLS:return ENTRY_SYMBOLS[key]
    if file in BASE:return BASE[file]
    if file.startswith('crates/client/src/pages/'):
        return ('page component / re-export','Dioxus Route selected page module','UI component')
    if file.startswith('crates/client/crates/client-'):
        return ('page/service component implementation','Feature-specific client crate reached from page wrapper','UI effects/state')
    if file.startswith('crates/service/crates/monitor/src/collectors/'):
        return ('Collector::collect*()','OS metric collector','READ operating-system metrics')
    if file.startswith('crates/service/crates/billing/src/usage/'):
        return ('UsageParser::*','Provider response usage normalization','READ response body/stream')
    if file.startswith('crates/router/src/adaptor/'):
        return ('DynamicAdaptorFactory / provider adaptor','Cross-protocol request/response transformation','DYNAMIC Provider transform')
    if file.startswith('crates/router/src/'):
        return (Path(file).stem,'Router runtime subsystem used by E2E path','READ/WRITE runtime state')
    if file.startswith('crates/download/'):
        return ('download / aria2 runtime symbols','Download manager / RPC execution','NETWORK/filesystem/process state')
    if file.startswith('crates/client/src/components/'):
        return ('layout/component','Dioxus layout/component wrapper','UI state')
    if old_s.startswith('见上方'):
        return ('entry-specific function(s) shown in E2E','当前入口在该文件执行的直接调用点','runtime-specific')
    return old_s,old_w,old_st


def rebuild(rows):
    lines=['','## 穿过的源码文件（详细）','',
           '| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |',
           '|---:|---|---|---|---|']
    for i,(f,s,w,st) in enumerate(rows,1):
        s=s.replace('|','/');w=w.replace('|','/');st=st.replace('|','/')
        lines.append(f'| {i} | `{f}` | `{s}` | {w} | {st} |')
    lines += ['', '> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。','']
    return '\n'.join(lines)


def main():
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8'));changed=0;generic_fallbacks=0
    for p in manifest['pages']:
        path=Path('docs')/(p['docid']+'.md');text=path.read_text(encoding='utf-8');m=DETAIL_RE.search(text)
        if not m: raise RuntimeError(f'missing detailed source table: {path}')
        rows=[]
        for line in m.group(0).splitlines():
            mm=ROW_RE.match(line)
            if not mm: continue
            _,f,s,w,st=mm.groups();ns,nw,nst=defaults(f,s,w,st,p);rows.append((f,ns,nw,nst))
            if ns.startswith('entry-specific function'): generic_fallbacks+=1
        if not rows: raise RuntimeError(f'no source rows parsed: {path}')
        text=text[:m.start()]+'\n'+rebuild(rows).rstrip()+'\n'+text[m.end():]
        path.write_text(text,encoding='utf-8');changed+=1
    print(f'Refined source symbols on {changed} pages; generic_fallback_rows={generic_fallbacks}')

if __name__=='__main__': main()
