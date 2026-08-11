from pathlib import Path
import re, shutil, json
from collections import OrderedDict

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
SIDEBAR = ROOT / 'site' / 'sidebars.js'
SOURCE_SHA = 'aa54e21393c6d46a6b09555ffd3661c1f22484f3'
PAGES = []


def safe(s):
    s = s.lower().strip()
    s = re.sub(r'\{([^}]+)\}', r'\1', s)
    s = s.replace(':', '-').replace('/', '-').replace(' ', '-')
    s = re.sub(r'[^a-z0-9._-]+', '-', s)
    return re.sub(r'-+', '-', s).strip('-') or 'index'


def add(section, group, title, kind, entry, source_files, logic, handler='', slug=None, meta=None):
    if slug is None:
        slug = '/'.join([safe(section), safe(group), safe(title)])
    PAGES.append(dict(section=section, group=group, title=title, kind=kind, entry=entry,
                      source_files=source_files, logic=logic, handler=handler,
                      slug='/' + slug.strip('/'), meta=meta or {}))


SERVER = 'crates/server/src/lib.rs'
ROUTER = 'crates/router/src/lib.rs'
PASSTHROUGH = 'crates/router/src/passthrough.rs'
DB_CHANNEL = 'crates/database/crates/channel/src/channel_ability.rs'
API_MOD = 'crates/server/src/api/mod.rs'

# HTTP / API — AI Data Plane
add('HTTP / API','AI API / Data Plane','GET /v1/models','models','GET /v1/models',
    [SERVER, ROUTER, DB_CHANNEL],
    '读取 channel_abilities 中 enabled = 1 的 DISTINCT model；不进入 proxy_handler，也不做用户鉴权、调度或 Provider 调用。',
    'models_handler', 'http-api/ai-api-data-plane/get-v1-models')
add('HTTP / API','AI API / Data Plane','GET /api/v1/usage','usage','GET /api/v1/usage',
    [SERVER, ROUTER, 'crates/database/crates/router/src/lib.rs'],
    '提取 Bearer Token，按新 token 表 → legacy token → JWT 的顺序识别用户，然后查询当月总请求、token 与成本。',
    'usage_handler')
add('HTTP / API','AI API / Data Plane','GET /api/v1/usage/models','usage_models','GET /api/v1/usage/models',
    [SERVER, ROUTER, 'crates/database/crates/router/src/lib.rs'],
    '与 usage 接口共用鉴权链，但数据库聚合维度改为 model，返回每个模型的请求量、token 与 cost。',
    'usage_models_handler')

proxy_entries = [
('POST /v1/chat/completions','OpenAI Chat Completions；标准聊天入口。'),
('POST /chat/completions','OpenAI Chat Completions 兼容别名；进入同一 proxy_handler。'),
('POST /v1/completions','OpenAI Legacy Completions；通过统一代理链选择 Channel 并请求上游。'),
('POST /v1/embeddings','Embeddings；统一鉴权、调度、Provider 转发和用量结算。'),
('POST /v1/messages','Anthropic Messages 原生协议；passthrough 可保持 Anthropic 请求/响应语义。'),
('POST /v1/video/generations','视频生成；除通用代理链外，还提取 duration/resolution，并在成功后保存 task_id → channel_id 映射。'),
('POST /v1beta/models/{model}:generateContent','Gemini v1beta generateContent；model 从 URL 提取。'),
('POST /v1beta/models/{model}:streamGenerateContent','Gemini v1beta 流式生成；model 从 URL 提取并进入流式响应计量。'),
('POST /v1beta/models/{model}:countTokens','Gemini v1beta countTokens；走 Gemini 原生 passthrough 规则。'),
('POST /v1beta/models/{model}:embedContent','Gemini v1beta embedContent；走 Gemini 原生 passthrough 规则。'),
('POST /v1/models/{model}:generateContent','Gemini v1 generateContent；model 从 URL 提取。'),
('POST /v1/models/{model}:streamGenerateContent','Gemini v1 流式生成；进入统一流式计量与返回链。'),
('POST /v1/models/{model}:countTokens','Gemini v1 countTokens；进入原生 passthrough。'),
('POST /v1/models/{model}:embedContent','Gemini v1 embedContent；进入原生 passthrough。'),
]
for title, note in proxy_entries:
    add('HTTP / API','AI API / Data Plane',title,'proxy',title,
        [SERVER, ROUTER, PASSTHROUGH, 'crates/database/crates/router/src/lib.rs',
         'crates/database/crates/channel/src/lib.rs', 'crates/service/crates/billing/src/lib.rs'],
        note, 'proxy_handler')

add('HTTP / API','AI API / Data Plane','GET /v1/videos/{task_id}','video_poll','GET /v1/videos/{task_id}',
    [SERVER, ROUTER, 'crates/database/crates/router/src/video_task.rs', 'crates/database/crates/channel/src/lib.rs'],
    '先鉴权，再从 task_id 查原始 channel_id；按该 Channel 的 base_url/key 直接轮询上游，不重新走模型调度。',
    'proxy_handler')
add('HTTP / API','AI API / Data Plane','Router fallback → proxy_handler','proxy_fallback','任意未被显式 Router 捕获的数据面路径',
    [SERVER, ROUTER, PASSTHROUGH],
    'Unified Server 将未命中的数据面请求交给 router_app；router_app 未命中显式 route 后进入 proxy_handler。',
    'proxy_handler')

# HTTP / API — public Authentication
for entry, handler, call, note in [
('POST /api/auth/register','create_user','register_user → get_user_roles → generate_token','注册用户；用户名冲突返回错误，注册成功后生成 JWT。'),
('POST /api/auth/login','login','login_user → get_user_roles','校验用户名密码；成功后返回 JWT 与角色。'),
('POST /api/auth/forgot-password','forgot_password','request_password_reset','即使邮箱不存在也返回成功语义，避免邮箱枚举。'),
('POST /api/auth/reset-password','reset_password','reset_password','校验 reset token 并修改密码；无效/过期 token 返回错误。'),
('GET /api/auth/google','oauth_google','UserService::oauth_url("google")','生成 Google OAuth URL；当前只返回 URL，不在此 Handler 完成回调。'),
('GET /api/auth/github','oauth_github','UserService::oauth_url("github")','生成 GitHub OAuth URL；当前只返回 URL。'),
]:
    add('HTTP / API','Authentication',entry,'public_auth',entry,
        [SERVER, API_MOD, 'crates/server/src/api/auth.rs', 'crates/service/crates/user/src/lib.rs'],
        note + ' 核心调用：' + call + '。', handler)

# HTTP / API — protected management routes
mgmt=[]
def m(group, entry, file, handler, service, note, admin=False):
    mgmt.append((group,entry,file,handler,service,note,admin))

m('Channel Management','GET /console/api/channel','crates/server/src/api/channel.rs','list_channels','ChannelService::list','管理员分页列出 Channel；limit 被限制在 1..100，offset 不小于 0。',True)
m('Channel Management','POST /console/api/channel','crates/server/src/api/channel.rs','create_channel','ChannelService::create','管理员把 ChannelDto 转成 Channel，并创建数据库记录。',True)
m('Channel Management','PUT /console/api/channel','crates/server/src/api/channel.rs','update_channel','ChannelService::update','管理员更新 Channel；id = 0 时直接拒绝。',True)
m('Channel Management','GET /console/api/channel/{id}','crates/server/src/api/channel.rs','get_channel','ChannelService::get_by_id','管理员按 ID 查询；不存在时返回 channel not found。',True)
m('Channel Management','DELETE /console/api/channel/{id}','crates/server/src/api/channel.rs','delete_channel','ChannelService::delete','管理员删除指定 Channel。',True)

for entry,handler,service,note in [
('GET /console/api/tokens','list_tokens','TokenService::list','列出 Router Token。'),
('POST /console/api/tokens','create_token','TokenService::create','生成 bc_live_<uuid>，构造 RouterToken 后写入数据库。'),
('GET /console/api/tokens/{token}','get_token','TokenService::validate','按 token 查询并返回 token 详情；不存在则报错。'),
('PUT /console/api/tokens/{token}','update_token','TokenService::update_status','更新 token status。'),
('DELETE /console/api/tokens/{token}','delete_token','TokenService::delete','删除 token。'),
('POST /console/api/tokens/{token}/rotate','rotate_token','TokenService::rotate','轮换 key，可设置旧 key 过渡时间或立即撤销。'),
('POST /console/api/tokens/{token}/revoke-old','revoke_old_key','TokenService::revoke_old_key','撤销旧 key；token 不存在时返回错误。'),
('POST /console/api/tokens/{token}/ip-whitelist','set_ip_whitelist','TokenService::set_ip_whitelist','更新 token 的 IP whitelist。'),
]: m('Token',entry,'crates/server/src/api/token.rs',handler,service,note)

for entry,handler,service,note in [
('POST /console/api/user/register','register','UserService::register_user','注意：虽然名字像注册接口，但它位于 protected router，当前先经过 JWT middleware。'),
('POST /console/api/user/login','login','UserService::login_user','当前位于 protected router；成功登录后还把 username/token 写入 ~/.burncloud/client_state.json。'),
('POST /console/api/user/topup','topup','UserService::topup','按 user_id、amount、currency 充值并返回新余额。'),
('GET /console/api/user/check_username','check_username','UserService::is_username_available','查询用户名是否可用。'),
('GET /console/api/user/recharges','list_recharges','UserService::list_recharges','从 JWT Claims.sub 得到当前用户，只查询自己的充值记录。'),
('GET /console/api/list_users','list_users','UserService::list_users','列出用户，并逐个读取角色后构造 UserSummary。'),
]: m('User',entry,'crates/server/src/api/user.rs',handler,service,note)

m('Billing / Usage','GET /api/billing/summary','crates/server/src/api/billing.rs','billing_summary_handler','BillingService::get_billing_summary_for_user','从 JWT Claims.sub 取得当前用户，按可选 start/end 查询个人账单汇总。')
m('Logs','GET /console/api/logs','crates/server/src/api/log.rs','list_logs','RouterLogService::get','按 page/page_size 计算 offset，分页返回 RouterLog。')
m('Logs','GET /console/api/usage/{user_id}','crates/server/src/api/log.rs','get_user_usage','RouterLogService::get_usage_by_user','按 URL user_id 汇总 prompt/completion/total tokens。')
m('Billing / Usage','GET /console/internal/billing/summary','crates/server/src/api/log.rs','billing_summary_handler','BillingService::get_billing_summary','该 route 当前仍被外层 JWT middleware 包住；若设置 BURNCLOUD_INTERNAL_SECRET，还额外校验 x-internal-secret。')
m('Monitoring / Security','GET /console/api/monitor','crates/server/src/api/monitor.rs','get_system_metrics','SystemMonitorService::get_metrics','读取后台系统监控缓存并返回 CPU/Memory/Disk 等指标。')

for entry,handler,service,note in [
('GET /console/api/monitor/security','security_summary','RouterLogService::get','读取最近 router_logs，按 4xx/5xx 比例计算 score、blocked_count、threat sources 和 7 日 sparkline。'),
('GET /console/api/monitor/security/events','security_events','RouterLogService::get','从 router_logs 过滤 status >= 400，转换成 RiskEvent 后再分页。'),
('GET /console/api/monitor/security/filters','security_filters_get','Database::query_with_params','读取 sys_settings.security_filters；没有记录或 JSON 无效时使用默认配置。'),
('PUT /console/api/monitor/security/filters','security_filters_put','Database::execute_query_with_params','序列化 FilterConfig，INSERT OR REPLACE 到 sys_settings。'),
('POST /console/api/monitor/security/emergency-circuit-break','security_emergency_circuit_break','post_router_internal','reason 不能为空；通过 localhost 调用 /console/internal/circuit-breaker/trip-all。'),
('GET /console/api/monitor/security/circuit-breaker-status','security_circuit_breaker_status','call_router_internal','通过 localhost 调用 /console/internal/health 获取 circuit breaker 状态。'),
]: m('Monitoring / Security',entry,'crates/server/src/api/security.rs',handler,service,note)

for entry,handler,service,note in [
('GET /console/api/cache/stats','stats','CacheService::stats','读取缓存统计；Redis 未启用/失败由 CacheService 返回结果或错误。'),
('POST /console/api/cache/clear','clear','CacheService::clear_all','清空全部缓存并返回 Cache cleared。'),
]: m('Cache',entry,'crates/server/src/api/cache.rs',handler,service,note)

for group,entry,file,handler,service,note,admin in mgmt:
    add('HTTP / API',group,entry,'management',entry,
        [SERVER, API_MOD, 'crates/server/src/api/auth.rs', file],
        note + ' 核心调用：' + service + '。', handler, meta={'admin':admin})

# duplicate semantic routes exposed in overview: give Billing / Usage dedicated pages too
for entry,handler,note in [
('GET /api/v1/usage','usage_handler','复用 Data Plane usage_handler：按 token holder 聚合月度总用量。'),
('GET /api/v1/usage/models','usage_models_handler','复用 Data Plane usage_models_handler：按 model 聚合月度用量。'),
('GET /console/api/usage/{user_id}','get_user_usage','复用 Logs 的用户用量查询：按 URL user_id 汇总 tokens。'),
]:
    add('HTTP / API','Billing / Usage',entry,'related_route',entry,
        [SERVER, ROUTER if entry.startswith('GET /api/v1') else API_MOD,
         'crates/server/src/api/log.rs' if 'console/api' in entry else 'crates/database/crates/router/src/lib.rs'],
        note, handler, slug='http-api/billing-usage/'+safe(entry))

# Admin / Internal
for entry,kind,handler,note in [
('GET /health','top_health','inline health handler','顶层 liveness probe，不需要 JWT，直接返回 ok。'),
('GET /console/internal/health','internal','health_status_handler','返回 scheduler policy、circuit breaker、channel state、rate budget 等运行态健康信息。'),
('POST /console/internal/prices/sync','internal','price_sync_handler','通过 force_sync_tx 触发价格同步任务，并最多等待 60 秒 oneshot 回应。'),
('POST /console/internal/circuit-breaker/trip-all','internal','circuit_breaker_trip_all_handler','调用 circuit_breaker.trip_all()，强制已知上游进入 Open。'),
('GET /console/internal/metrics','internal','metrics_handler','返回 Router 内部 metrics。'),
('GET /console/api/{*path} → protected 404 catch-all','management_404','api_not_found','Management API 未匹配的 /console/api/* 在 JWT 后进入 404，避免被 LiveView 返回 HTML。'),
]:
    files=[SERVER,ROUTER] if kind=='internal' else ([SERVER,API_MOD] if kind=='management_404' else [SERVER])
    add('HTTP / API','Admin / Internal',entry,kind,entry,files,note,handler)

# OpenAPI / Swagger
for entry,handler,note in [
('GET /api-docs/openapi.json','openapi_json','运行时构造 OpenAPI 3.0.3 spec 并以 JSON 返回。'),
('GET /swagger-ui','swagger_ui','返回内嵌 Swagger UI HTML，浏览器再从 CDN 加载 swagger-ui assets。'),
('GET /swagger-ui/','swagger_ui','与 /swagger-ui 使用同一个 Handler。'),
]:
    explicit_slug = 'http-api/openapi-swagger/get-swagger-ui-slash' if entry == 'GET /swagger-ui/' else None
    add('HTTP / API','OpenAPI / Swagger',entry,'openapi',entry,
        [SERVER,API_MOD,'crates/server/src/api/auth.rs','crates/server/src/api/openapi.rs'],note,handler,slug=explicit_slug)

# Web UI / LiveView / WS
web_routes=['GET /','GET /home','GET /login','GET /register','GET /forgot-password','GET /reset-password',
            'GET /console','GET /console/','GET /console/{*path}','GET /favicon.ico','GET /preview/home',
            'GET /preview/login','GET /preview/console','GET /preview/console/','GET /preview/console/{*path}']
for entry in web_routes:
    explicit_web_slug = None
    if entry == 'GET /console/': explicit_web_slug = 'http-api/web-ui-liveview-websocket/get-console-slash'
    if entry == 'GET /preview/console/': explicit_web_slug = 'http-api/web-ui-liveview-websocket/get-preview-console-slash'
    add('HTTP / API','Web UI / LiveView / WebSocket',entry,'liveview_http',entry,
        [SERVER,'crates/client/src/lib.rs','crates/client/src/app.rs'],
        '当 enable_liveview = true 时由 LiveView Router 命中，返回页面 shell/静态响应；后续交互通过 Dioxus LiveView 与 WebSocket。', slug=explicit_web_slug)
add('HTTP / API','Web UI / LiveView / WebSocket','GET /ws','websocket','GET /ws',
    [SERVER,'crates/client/src/lib.rs','crates/client/src/app.rs'],
    'HTTP Upgrade 到 WebSocket，承载 LiveView 交互；连接失败/断开由 LiveView/WebSocket 生命周期处理。')

# CLI / Executables
cli_groups = {
'update':['--check-only'],
'install':['[software]','--list','--status','--auto-deps','--local PATH','--bundle DIR'],
'bundle':['create <software> -o DIR','verify <bundle-dir>'],
'channel':['add','list','delete <id>','show <id>','update <id>'],
'price':['list','set <model>','get <model>','show <model>','delete <model>','sync-status','import <file>','export <file>','validate <file>','sync'],
'tiered':['list-tiers <model>','add-tier <model>','import-tiered <file>','delete-tiers <model>','check-tiered <model>'],
'token':['list','create','update <key>','delete <key>'],
'protocol':['list','add','delete <id>','show <id>','test --channel-id <id>'],
'currency':['list-rates','set-rate','refresh','convert <amount>'],
'user':['register','login','list','topup','recharges','check-username'],
'log':['list','usage'],
'monitor':['status','server'],
}
cli_file = {'bundle':'src/cli/bundle.rs','channel':'src/cli/channel.rs','price':'src/cli/price.rs','tiered':'src/cli/price.rs',
            'token':'src/cli/token.rs','protocol':'src/cli/protocol.rs','currency':'src/cli/currency.rs','user':'src/cli/user.rs',
            'log':'src/cli/log.rs','monitor':'src/cli/monitor.rs','install':'src/cli/install.rs','update':'src/main.rs'}
for cmd in ['burncloud','server','router','client']:
    note={'burncloud':'无参数时按平台启动：Windows 为后台 Server + 桌面 GUI/tray；非 Windows 为 Server + LiveView。',
          'server':'显式启动 Server 模式。','router':'显式启动 Router 相关模式。','client':'显式启动 Client 模式。'}[cmd]
    add('CLI / Executables','burncloud',cmd,'cli','burncloud' if cmd=='burncloud' else 'burncloud '+cmd,
        ['src/main.rs','src/cli/commands.rs'],note,slug='cli/burncloud/'+safe(cmd))
for group,subs in cli_groups.items():
    for sub in subs:
        entry='burncloud '+group+' '+sub
        add('CLI / Executables','burncloud',entry,'cli_subcommand',entry,
            ['src/main.rs','src/cli/commands.rs',cli_file[group]],
            f'Clap 解析到 {group} 分支，再进入 {cli_file[group]} 中对应命令实现；参数校验失败时由 Clap/命令逻辑提前结束。',
            slug='cli/burncloud/'+safe(group)+'/'+safe(sub))

for binname,files,note in [
('burncloud-client',['crates/client/src/main.rs','crates/client/src/app.rs'],'启动 Dioxus 客户端/桌面或 Web 入口。'),
('screenshot_gen',['crates/client/src/bin/screenshot_gen.rs'],'开发辅助二进制：创建 VirtualDom 并生成页面 SSR/screenshot 相关输出。'),
('burncloud-download',['crates/download/src/main.rs'],'下载组件可执行入口；当前 main 包含下载任务演示逻辑。'),
('burncloud-loop',['crates/loops/src/main.rs'],'Loop 工具入口，按子命令执行 jobs-aesthetic/css-optimize/gate/gates/list-gates。'),
('client-api',['crates/client/crates/client-api/src/main.rs'],'独立 ApiManagement 客户端 shell。'),
('client-shared',['crates/client/crates/client-shared/src/main.rs'],'独立 CoreRoute 客户端入口。'),
('client-tray',['crates/client/crates/client-tray/src/main.rs'],'Windows tray 可执行入口；非 Windows 为不支持分支。'),
]:
    add('CLI / Executables','Workspace Binaries',binname,'binary',binname,files,note,slug='cli/workspace-binaries/'+safe(binname))

# Background Jobs / Async Side Effects
background = [
('Long-running Jobs','System Monitor Auto Update',['crates/server/src/lib.rs','crates/service/crates/monitor/src/lib.rs'],'create_app() 启动 start_auto_update；周期采集 CPU、内存、磁盘并刷新内存缓存。'),
('Long-running Jobs','Price Sync',['crates/router/src/lib.rs','crates/router/src/price_sync.rs'],'Router 启动 price sync task；启动快路径读取现有价格，随后周期同步，也接受 force-sync channel。'),
('Long-running Jobs','Exchange Rate Sync',['crates/router/src/lib.rs','crates/service/crates/billing/src/exchange_rate.rs'],'周期检查汇率是否过期，刷新/重载数据库中的 exchange rates。'),
('Long-running Jobs','AIMD Budget Feedback',['crates/router/src/lib.rs'],'mpsc 消费请求反馈，动态调节 Channel rate budget。'),
('Long-running Jobs','Async Router Log Writer',['crates/router/src/lib.rs','crates/service/crates/router-log/src/lib.rs'],'后台消费 RouterLog 队列并持久化，避免主请求同步阻塞。'),
('Long-running Jobs','Async Request Log Writer',['crates/router/src/lib.rs'],'后台消费详细 RequestLog 队列并写入持久层。'),
('Request-time Async Side Effects','Token accessed_time update',[ROUTER],'Token 鉴权成功后 tokio::spawn 异步更新 accessed_time；失败不阻断主请求。'),
('Request-time Async Side Effects','Quota deduction',[ROUTER],'请求完成并计算 cost 后异步扣减 quota；属于请求结束后的副作用。'),
('Request-time Async Side Effects','Video task mapping save',[ROUTER],'视频生成返回 task_id 后异步保存 task_id → channel_id/user/model/duration/resolution。'),
('Request-time Async Side Effects','API version detect / update',[ROUTER],'部分上游失败触发 API version 探测/更新，为后续请求提供版本信息。'),
('Download Background Work','Download progress monitor',['crates/download/src/lib.rs'],'定期读取 aria2 状态并把进度写入数据库，直到 complete/error/client unavailable。'),
('Download Background Work','Restore incomplete downloads',['crates/download/src/lib.rs'],'DownloadManager 初始化时恢复 active 且未完成的下载并重新启动 monitor。'),
('Desktop Background Work','Windows tray thread',['crates/client/src/app.rs','crates/client/crates/client-tray/src/main.rs'],'Windows 桌面启动系统托盘线程，处理托盘生命周期。'),
('Desktop Background Work','Show-window poll loop',['crates/client/src/app.rs'],'Dioxus async loop 周期检查 show-window 状态，执行 visible/focus。'),
]
for group,title,files,note in background:
    add('Background Jobs / Async Side Effects',group,title,'background',title,files,note,slug='background/'+safe(group)+'/'+safe(title))

# Startup
for title,files,note in [
('src/main.rs',['src/main.rs'],'进程入口：dotenv → MASTER_KEY → logging → 平台/argv 分发；无参数按平台启动 GUI/LiveView，显式参数进入 server/router/client/CLI。'),
('start_server',[SERVER],'创建默认数据库 → RouterDatabase::init → UserDatabase::init → create_app → bind → axum::serve。'),
('create_app',[SERVER,API_MOD,'crates/client/src/lib.rs'],'初始化 monitor/cache/data-plane router，组合 Management/Internal/LiveView，并挂载全局 middleware 和 data-plane fallback。'),
('create_router_app',[ROUTER],'构建 HTTP client、limiter、circuit breaker、ModelRouter、scheduler、PriceCache、CostCalculator、rate budget、后台 writer/task，再注册显式路由和 proxy fallback。'),
]:
    add('Startup','Startup Chain',title,'startup',title,files,note,slug='startup/'+safe(title))

# UI-only Actions
for group,routes in [
('Guest / Public',['/','/home','/login','/register','/forgot-password','/reset-password?:token']),
('Console',['/console/dashboard','/console/deploy','/console/monitor','/console/access','/console/models','/console/users','/console/settings','/console/finance','/console/logs','/console/connect','/console/playground','/console/:..segments → NotFound']),
('Debug / e2e-preview',['/preview/home','/preview/login','/preview/console/dashboard','/preview/console/models','/preview/console/access','/preview/console/settings','/preview/console/finance','/preview/console/monitor','/preview/console/playground']),
]:
    for route in routes:
        add('UI-only Actions',group,route,'ui_route',route,['crates/client/src/app.rs'],
            'Dioxus Router 匹配客户端路由并挂载对应页面组件；这是客户端导航，不等同于 Management REST API。',
            slug='ui/'+safe(group)+'/'+safe(route))
for title,note in [
('i18n context','App 初始化国际化上下文，供页面组件读取/切换文案。'),
('Toast state / ToastContainer','App 初始化 Toast state，并在根组件挂载 ToastContainer。'),
('Auth context','App 初始化客户端认证上下文，页面据此读取登录状态。'),
('Theme state','App 初始化主题状态，驱动 UI 主题。'),
]:
    add('UI-only Actions','Local UI State',title,'ui_state',title,['crates/client/src/app.rs'],note,slug='ui/local-state/'+safe(title))
for title,note in [
('window maximize','桌面启动时执行窗口最大化相关动作。'),
('Windows tray startup','Windows 平台启动 tray thread。'),
('show / hide / focus','后台 poll 接收到 show-window 状态后更新窗口 visible/focus。'),
]:
    add('UI-only Actions','Desktop UI',title,'ui_desktop',title,['crates/client/src/app.rs'],note,slug='ui/desktop/'+safe(title))


def front(p):
    title=p['title'].replace('"', "'")
    return f'''---\ntitle: "{title}"\nslug: {p['slug']}\nhide_table_of_contents: true\n---\n\n# {p['title']}\n\n**树路径：** `BurnCloud → {p['section']} → {p['group']} → {p['title']}`\n\n> **中文解释：** {p['logic']}\n>\n> **源码基线：** `burncloud/burncloud@{SOURCE_SHA}`\n\n## End-to-End Request Flow + ICFG\n\n'''


def files_block(files):
    rows='\n'.join(f'| {i+1} | `{f}` |' for i,f in enumerate(files))
    return f'''\n## 穿过的源码文件\n\n| 顺序 | 文件 |\n|---|---|\n{rows}\n\n**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。\n'''


def http_server_prefix(entry):
    return f'''START\n│\n├─ 发起者\n│    └─ User / SDK / Browser / Operator\n│\n├─ 入口\n│    └─ {entry}\n│\n▼\nFILE: crates/server/src/lib.rs\n│\n├─ axum::serve(listener, app)\n├─ 全局 Middleware\n│    ├─ CORS\n│    ├─ TraceLayer\n│    └─ x-request-id\n│\n'''


def render(p):
    k=p['kind']; e=p['entry']; h=p['handler']; meta=p['meta']; logic=p['logic']
    if k=='models':
        flow=http_server_prefix(e)+'''├─ DECISION: 顶层 Unified App 命中 /v1/models ?\n│    └─ NO → fallback_service(router_app)\n│\n▼\nFILE: crates/router/src/lib.rs\n│\n├─ DECISION: 显式 Data Plane route == GET /v1/models ?\n│    ├─ YES → models_handler()\n│    └─ NO  → proxy_handler fallback\n│\n├─ models_handler()\n│    ├─ model_entries = []\n│    ├─ current_time = UNIX seconds\n│    └─ CALL ChannelAbilityModel::list_distinct_models(&state.db)\n│\n▼\nFILE: crates/database/crates/channel/src/channel_ability.rs\n│\n├─ db.get_connection()\n├─ DECISION: DB connection OK?\n│    ├─ NO  → Err\n│    └─ YES → SQL\n│\n├─ SELECT DISTINCT model\n│    FROM channel_abilities\n│    WHERE enabled = 1\n│    ORDER BY model\n│\n├─ DECISION: SQL OK?\n│    ├─ NO  → Err\n│    └─ YES → Ok(Vec<String>)\n│\n▼\nFILE: crates/router/src/lib.rs\n│\n├─ DECISION: list_distinct_models returned Ok?\n│    ├─ NO  → error 被 if let Ok(...) 吞掉；data=[]\n│    └─ YES → FOR EACH model\n│         └─ build {id, object, created, owned_by, permission, root, parent}\n│\n├─ serialize response_json\n├─ DECISION: serialization OK?\n│    ├─ YES → normal JSON\n│    └─ NO  → {"object":"list","data":[]}\n│\n└─ HTTP 200 application/json\n\n▼\nEND\n     └─ User / SDK receives models list\n'''
    elif k in ('usage','usage_models','related_route') and e.startswith('GET /api/v1'):
        dbcall='get_usage_stats_by_model(user_id, "month")' if 'models' in e else 'get_usage_stats(user_id, "month")'
        flow=http_server_prefix(e)+f'''├─ 顶层未命中 → fallback_service(router_app)\n│\n▼\nFILE: crates/router/src/lib.rs\n│\n├─ 显式 route → {h}()\n├─ extract_token_user()\n│    ├─ DECISION: Authorization Bearer 存在?\n│    │    ├─ NO  → HTTP 401\n│    │    └─ YES → validate token\n│    ├─ validate_token_and_get_info\n│    ├─ fallback: validate_token_detailed\n│    └─ fallback: JWT decode\n│\n├─ DECISION: token/user 可解析?\n│    ├─ NO  → 401 / 503\n│    └─ YES → user_id\n│\n├─ DB CALL: {dbcall}\n├─ DECISION: query OK?\n│    ├─ NO  → HTTP 500\n│    └─ YES → serialize usage JSON\n│\n└─ HTTP 200 application/json\n\n▼\nEND\n     └─ 返回当前 token holder 的月度用量\n'''
    elif k in ('proxy','proxy_fallback'):
        flow=http_server_prefix(e)+'''├─ 顶层未命中 → fallback_service(router_app)\n│\n▼\nFILE: crates/router/src/lib.rs\n│\n├─ router_app 未命中显式 models / usage route\n│    └─ proxy_handler()\n│\n├─ normalize_doubled_path()\n├─ Credential Source\n│    ├─ Authorization: Bearer ...\n│    ├─ x-api-key\n│    └─ x-goog-api-key\n│\n├─ DECISION: credential exists?\n│    ├─ NO  → HTTP 401\n│    └─ YES → RouterDatabase validate\n│\n├─ DECISION: token valid?\n│    ├─ YES → user_id / group / quota / order_type / price_cap\n│    └─ NO\n│         ├─ legacy token validation\n│         └─ JWT fallback\n│\n├─ DECISION: quota exhausted?\n│    ├─ YES → HTTP 402\n│    └─ NO  → continue\n│\n├─ DECISION: local rate limiter allows?\n│    ├─ NO  → HTTP 429\n│    └─ YES → collect request body\n│\n├─ Extract request context\n│    ├─ model from JSON body or Gemini URL\n│    ├─ batch / priority flags\n│    └─ video duration/resolution when applicable\n│\n├─ proxy_logic(...)\n│    ├─ load scheduler policy for user group\n│    ├─ resolve model / candidate channels\n│    ├─ filter availability / order constraints\n│    ├─ billing preflight\n│    └─ candidate attempt loop\n│         ├─ rate budget / shaper\n│         ├─ circuit breaker\n│         ├─ protocol decision\n│         └─ upstream request\n│\n▼\nFILE: crates/router/src/passthrough.rs + Dynamic Adaptor Boundary\n│\n├─ DECISION: native passthrough supported?\n│    ├─ YES → preserve OpenAI / Anthropic / Gemini native protocol\n│    └─ NO  → adaptor conversion path（DYNAMIC by Provider）\n│\n├─ Send HTTP request to selected upstream\n├─ DECISION: upstream attempt succeeds?\n│    ├─ NO  → record failure → next candidate / final error\n│    └─ YES → response / stream handling\n│\n▼\nFILE: crates/router/src/lib.rs\n│\n├─ collect UnifiedUsage\n├─ video token injection when applicable\n├─ CostCalculator::calculate()\n├─ enqueue RouterLog / RequestLog\n├─ async quota deduction when cost > 0\n├─ attach resolved channel/model headers\n└─ return upstream-compatible HTTP response\n\n▼\nEND\n     └─ User / SDK receives response\n'''
    elif k=='video_poll':
        flow=http_server_prefix(e)+'''├─ fallback_service(router_app) → proxy_handler()\n├─ credential validation / quota / rate limit\n├─ DECISION: method == GET and path starts /v1/videos/?\n│    ├─ NO  → normal proxy_logic\n│    └─ YES → special polling branch\n│\n├─ task_id = path suffix\n├─ RouterVideoTaskModel::get_by_task_id(task_id)\n├─ DECISION: mapping exists?\n│    ├─ NO  → HTTP 404 task_not_found\n│    └─ YES → channel_id\n├─ ChannelProviderModel::get_by_id(channel_id)\n├─ DECISION: Channel available?\n│    ├─ NO  → HTTP 502\n│    └─ YES → build upstream /v1/videos/{task_id}\n├─ GET upstream with Channel key\n├─ DECISION: upstream request OK?\n│    ├─ NO  → HTTP 502\n│    └─ YES → pass status/body back\n│\n▼\nEND\n     └─ polling response returned to client\n'''
    elif k=='public_auth':
        flow=http_server_prefix(e)+f'''├─ create_app() → api::routes()\n│\n▼\nFILE: crates/server/src/api/mod.rs\n│\n├─ DECISION: public auth route?\n│    ├─ YES → bypass JWT middleware\n│    └─ NO  → protected router\n│\n▼\nFILE: crates/server/src/api/auth.rs\n│\n├─ Route match → {h}()\n├─ Parse Query / JSON input if required\n├─ Execute UserService / OAuth logic\n├─ DECISION: service call successful?\n│    ├─ NO  → err(...) response\n│    └─ YES → ok(...) response\n│\n└─ HTTP response returned\n\n▼\nEND\n'''
    elif k in ('management','related_route'):
        admin='''├─ DECISION: user has admin role?\n│    ├─ NO  → Admin access required\n│    └─ YES → continue\n│\n''' if meta.get('admin') else ''
        file=p['source_files'][-1]
        flow=http_server_prefix(e)+f'''├─ create_app() → api::routes()\n│\n▼\nFILE: crates/server/src/api/mod.rs\n│\n├─ protected_routes\n├─ auth_middleware()\n│    ├─ DECISION: Authorization starts with Bearer?\n│    │    ├─ NO  → HTTP 401\n│    │    └─ YES → verify_jwt()\n│    └─ valid Claims inserted into request extensions\n│\n▼\nFILE: {file}\n│\n├─ Route match → {h}()\n│\n{admin}├─ Execute service/database operation\n├─ DECISION: operation successful?\n│    ├─ NO  → error response\n│    └─ YES → serialize success payload\n│\n└─ return HTTP response\n\n▼\nEND\n'''
    elif k=='management_404':
        flow=http_server_prefix(e)+'''├─ api::routes() protected router\n├─ auth_middleware()\n├─ DECISION: JWT valid?\n│    ├─ NO  → HTTP 401\n│    └─ YES → continue\n├─ No concrete /console/api/* route matched\n└─ api_not_found() → HTTP 404 "API endpoint not found"\n\n▼\nEND\n'''
    elif k=='top_health':
        flow=http_server_prefix(e)+'''├─ create_app() has explicit GET /health\n├─ DECISION: path == /health?\n│    ├─ NO  → continue router matching\n│    └─ YES → inline handler returns "ok"\n└─ No JWT required\n\n▼\nEND\n'''
    elif k=='internal':
        flow=http_server_prefix(e)+f'''├─ create_app() merges internal_app before LiveView\n│\n▼\nFILE: crates/router/src/lib.rs\n│\n├─ explicit internal route → {h}()\n├─ IMPORTANT: current internal_app itself has no JWT middleware\n├─ Execute internal runtime operation\n├─ DECISION: operation succeeds?\n│    ├─ NO  → route-specific 5xx/timeout response\n│    └─ YES → JSON response\n│\n▼\nEND\n'''
    elif k=='openapi':
        flow=http_server_prefix(e)+f'''├─ api::routes() places openapi::routes() inside protected_routes\n├─ auth_middleware()\n├─ DECISION: JWT valid?\n│    ├─ NO  → HTTP 401\n│    └─ YES → {h}()\n│\n▼\nFILE: crates/server/src/api/openapi.rs\n│\n├─ build OpenAPI JSON or Swagger HTML\n└─ return response\n\n▼\nEND\n'''
    elif k=='liveview_http':
        flow=http_server_prefix(e)+'''├─ DECISION: enable_liveview == true?\n│    ├─ NO  → route may fall to data-plane fallback\n│    └─ YES → merged LiveView Router\n│\n▼\nFILE: crates/client/src/lib.rs\n│\n├─ Match shell/static route\n├─ Return Dioxus LiveView HTML shell / favicon response\n│\n▼\nFILE: crates/client/src/app.rs\n│\n├─ Browser loads Dioxus route tree\n└─ Subsequent interactive state is driven by LiveView/WebSocket\n\n▼\nEND\n'''
    elif k=='websocket':
        flow=http_server_prefix(e)+'''├─ enable_liveview == true\n├─ LiveView Router matches /ws\n├─ HTTP Upgrade → WebSocket\n│\n▼\nFILE: crates/client/src/lib.rs\n│\n├─ establish LiveView socket session\n├─ exchange UI events / render updates\n├─ DECISION: connection alive?\n│    ├─ YES → continue event loop\n│    └─ NO  → close session\n│\n▼\nEND\n'''
    elif k in ('cli','cli_subcommand'):
        flow=f'''START\n│\n├─ Shell / Terminal\n│    └─ {e}\n│\n▼\nFILE: src/main.rs\n│\n├─ dotenv\n├─ ensure / generate MASTER_KEY\n├─ init_logging\n├─ parse argv\n├─ DECISION: direct server/router/client/default mode?\n│    ├─ YES → corresponding runtime entry\n│    └─ NO  → Clap CLI dispatch\n│\n▼\nFILE: src/cli/commands.rs\n│\n├─ Match command / subcommand\n├─ DECISION: parameters valid?\n│    ├─ NO  → Clap/command error → END\n│    └─ YES → dispatch implementation\n│\n▼\nFILE: {p['source_files'][-1]}\n│\n├─ Execute command-specific DB / service / filesystem / HTTP logic\n├─ DECISION: operation successful?\n│    ├─ NO  → print/return error\n│    └─ YES → print result / start requested runtime\n│\n▼\nEND\n'''
    elif k=='binary':
        flow=f'''START\n│\n├─ OS launches executable\n│    └─ {e}\n│\n▼\nFILE: {p['source_files'][0]}\n│\n├─ main()\n├─ initialize executable-specific runtime\n├─ DECISION: platform / arguments / initialization valid?\n│    ├─ NO  → error / unsupported branch\n│    └─ YES → run binary purpose\n│\n▼\nEND\n'''
    elif k=='background':
        flow=f'''START\n│\n├─ Trigger\n│    └─ Server/Router/Manager startup or request-side spawn\n│\n▼\nFILE: {p['source_files'][0]}\n│\n├─ Register / spawn background work\n├─ 执行：{logic}\n├─ DECISION: should continue?\n│    ├─ YES → sleep / await event / receive message → next iteration\n│    └─ NO  → stop task\n├─ DECISION: iteration failed?\n│    ├─ YES → log / fail-open according to task semantics\n│    └─ NO  → update state / persistence\n│\n▼\nEND / NEXT ITERATION\n'''
    elif k=='startup':
        flow=f'''START\n│\n├─ Process startup\n│    └─ {e}\n│\n▼\nFILE: {p['source_files'][0]}\n│\n├─ {logic}\n├─ DECISION: initialization step fails?\n│    ├─ YES → propagate error / process startup fails\n│    └─ NO  → continue next initialization stage\n│\n├─ Runtime objects / routes / tasks become available\n│\n▼\nEND\n     └─ server/client/runtime enters steady state\n'''
    elif k=='ui_route':
        flow=f'''START\n│\n├─ User navigation / router state\n│    └─ {e}\n│\n▼\nFILE: crates/client/src/app.rs\n│\n├─ Dioxus Route enum/router matches path\n├─ DECISION: route exists?\n│    ├─ NO  → NotFound branch\n│    └─ YES → mount mapped page component\n├─ Component reads local contexts as needed\n│    ├─ Auth context\n│    ├─ Theme\n│    ├─ i18n\n│    └─ Toast\n├─ Network calls, if any, are separate HTTP flows\n│\n▼\nEND\n     └─ page rendered / UI event loop continues\n'''
    elif k=='ui_state':
        flow=f'''START\n│\n▼\nFILE: crates/client/src/app.rs\n│\n├─ App root initializes {e}\n├─ Provide state/context to descendant components\n├─ DECISION: component updates state?\n│    ├─ YES → Dioxus re-render affected subtree\n│    └─ NO  → keep current state\n│\n▼\nEND / UI LOOP CONTINUES\n'''
    elif k=='ui_desktop':
        flow=f'''START\n│\n▼\nFILE: crates/client/src/app.rs\n│\n├─ Desktop platform branch\n├─ 执行：{logic}\n├─ DECISION: platform/state allows action?\n│    ├─ NO  → skip / unsupported branch\n│    └─ YES → apply window/tray state\n│\n▼\nEND / DESKTOP LOOP CONTINUES\n'''
    else:
        flow=f'START\n│\n├─ {e}\n│\n▼\nEND\n'
    return front(p)+'```text\n'+flow+'```\n\n'+files_block(p['source_files'])


# 清理旧生成页，只保留首页，然后全量重新生成。
DOCS.mkdir(parents=True, exist_ok=True)
for child in DOCS.iterdir():
    if child.name == 'index.md':
        continue
    if child.is_dir():
        shutil.rmtree(child)
    elif child.suffix in ('.md','.json'):
        child.unlink()

manifest=[]
seen=set()
for p in PAGES:
    if p['slug'] in seen:
        raise RuntimeError(f'duplicate slug: {p["slug"]}')
    seen.add(p['slug'])
    rel=p['slug'].strip('/')+'.md'
    target=DOCS/rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(p),encoding='utf-8')
    p['docid']=rel[:-3]
    manifest.append({k:p[k] for k in ('section','group','title','entry','slug','docid')})

(DOCS/'atlas-manifest.json').write_text(json.dumps({'source_sha':SOURCE_SHA,'page_count':len(PAGES),'pages':manifest},ensure_ascii=False,indent=2),encoding='utf-8')

sections=OrderedDict()
for p in PAGES:
    sections.setdefault(p['section'],OrderedDict()).setdefault(p['group'],[]).append(p)
lines=["module.exports = {", "  docsSidebar: [", "    {type:'doc', id:'index', label:'BurnCloud'},"]
for sec,groups in sections.items():
    lines.append(f"    {{type:'category', label:{json.dumps(sec,ensure_ascii=False)}, collapsed:false, items:[")
    for grp,items in groups.items():
        lines.append(f"      {{type:'category', label:{json.dumps(grp,ensure_ascii=False)}, collapsed:true, items:[")
        for p in items:
            lines.append(f"        {{type:'doc', id:{json.dumps(p['docid'])}, label:{json.dumps(p['title'],ensure_ascii=False)}}},")
        lines.append("      ]},")
    lines.append("    ]},")
lines += ["  ],", "};", ""]
SIDEBAR.write_text('\n'.join(lines),encoding='utf-8')
print(f'Generated {len(PAGES)} pages + docs/index.md')
