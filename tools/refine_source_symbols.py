from pathlib import Path
import json,re

MANIFEST=Path('docs/atlas-manifest.json')
DETAIL_RE=re.compile(r'(## 穿过的源码文件（详细）\n\n\| 顺序 \| 源码文件 \| 关键函数 / 符号 \| 为什么会经过 \| 状态 / 副作用 \|\n\|---:|---|---|---|---\|\n)(.*?)(?=\n\n> Source Traversal)',re.S)
ROW_RE=re.compile(r'^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*`([^`]*)`\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$')

BASE={
 'crates/server/src/lib.rs':('start_server(), create_app()','统一 HTTP Server / App composition / fallback','INIT + request routing'),
 'crates/server/src/api/mod.rs':('routes()','Public/Protected Management route composition','ROUTE composition'),
 'crates/server/src/api/auth.rs':('auth_middleware(), verify_jwt(), public_routes()','JWT middleware 与 public authentication routes','READ Authorization / Claims'),
 'crates/router/src/lib.rs':('create_router_app(), proxy_handler(), proxy_logic()','Data Plane 主控制流或 Router internal handler','READ/WRITE router runtime'),
 'crates/client/src/lib.rs':('liveview_router(), LiveViewPool::launch()','LiveView HTTP shell / WebSocket router','NETWORK/UI runtime'),
 'crates/client/src/app.rs':('App(), Route, launch_gui_with_tray()','Dioxus root/router/desktop runtime','UI state'),
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
 'crates/database/crates/channel/src/channel_protocol_config.rs':('ChannelProtocolConfigModel::*','Protocol configuration persistence','READ/WRITE protocol config'),
 'crates/database/crates/router/src/token.rs':('RouterTokenModel::*','Router token/quota/key persistence','READ/WRITE router token state'),
 'crates/database/crates/router/src/log.rs':('RouterLogModel::* / usage & billing queries','Request accounting / usage / billing persistence','READ/WRITE router_logs'),
 'crates/database/crates/router/src/router_video_task.rs':('RouterVideoTaskModel::*','Video task → channel mapping persistence','READ/WRITE video task mapping'),
 'crates/database/crates/user/src/lib.rs':('UserDatabase::*','User/role/recharge persistence','READ/WRITE user state'),
 'crates/database/crates/user/src/password_reset.rs':('PasswordResetDatabase::*','Password reset token persistence','READ/WRITE reset state'),
 'crates/database/crates/billing/src/billing_price.rs':('BillingPriceModel::*','Model price persistence','READ/WRITE billing prices'),
 'crates/database/crates/billing/src/billing_tiered_price.rs':('BillingTieredPriceModel::*','Tiered price persistence','READ/WRITE tiered prices'),
 'crates/database/src/lib.rs':('Database::get_connection(), query/execute helpers','Core database abstraction','SQL boundary'),
}


def defaults(file,old_s,old_w,old_st):
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
        name=Path(file).stem
        return (name,'Router runtime subsystem used by E2E path','READ/WRITE runtime state')
    if file.startswith('crates/download/'):
        return ('download / aria2 runtime symbols','Download manager / RPC execution','NETWORK/filesystem/process state')
    if file.startswith('crates/client/src/components/'):
        return ('layout/component','Dioxus layout/component wrapper','UI state')
    if old_s.startswith('见上方'):
        return ('entry-specific function(s) shown in E2E','当前入口在该文件执行的直接调用点','runtime-specific')
    return old_s,old_w,old_st


def main():
    manifest=json.loads(MANIFEST.read_text(encoding='utf-8')); changed=0; generic_left=[]
    for p in manifest['pages']:
        path=Path('docs')/(p['docid']+'.md'); text=path.read_text(encoding='utf-8'); m=DETAIL_RE.search(text)
        if not m: raise RuntimeError(f'missing detailed source table: {path}')
        out=[]
        for line in m.group(2).splitlines():
            mm=ROW_RE.match(line)
            if not mm:
                if line.strip(): out.append(line)
                continue
            n,f,s,w,st=mm.groups(); ns,nw,nst=defaults(f,s,w,st)
            out.append(f'| {n} | `{f}` | `{ns}` | {nw} | {nst} |')
            if ns.startswith('见上方'): generic_left.append((str(path),f))
        new=m.group(1)+'\n'.join(out)
        text=text[:m.start()]+new+text[m.end():];path.write_text(text,encoding='utf-8');changed+=1
    print(f'Refined source symbols on {changed} pages; unresolved_generic={len(generic_left)}')

if __name__=='__main__': main()
