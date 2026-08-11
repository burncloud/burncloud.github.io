from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
import re

FLOW_RE = re.compile(r"(## End-to-End Request Flow \+ ICFG\n\n)```text\n(.*?)\n```", re.S)
DETAIL_RE = re.compile(r"\n## 穿过的源码文件（详细）\n\n.*?(?=\n\*\*Execution classification:)", re.S)
ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*`([^`]*)`\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$")
FILE_SEG_RE = re.compile(r"FILE:\s*([^\n]+)\n(.*?)(?=\n▼\nFILE:|\n▼\nEND|\Z)", re.S)
CALL_NAME_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*(?:::[A-Za-z_][A-Za-z0-9_]*)*)\s*\(")
FN_DEF_RE = re.compile(r"(?m)^[ \t]*(?:pub(?:\([^)]*\))?[ \t]+)?(?:async[ \t]+)?(?:unsafe[ \t]+)?fn[ \t]+([A-Za-z_][A-Za-z0-9_]*)[^;{]*\{")
IMPL_RE = re.compile(r"(?m)^[ \t]*impl(?:\s*<[^\n{>]*>)?\s+([A-Za-z_][A-Za-z0-9_]*)[^\n{]*\{")

SKIP_NAMES = {
    "if", "match", "while", "for", "loop", "return", "Some", "None", "Ok", "Err",
    "format", "format_args", "vec", "println", "eprintln", "panic", "assert", "assert_eq",
    "tracing", "json", "rsx", "cfg", "derive", "default", "clone", "into", "from", "map",
    "unwrap_or", "unwrap_or_else", "unwrap_or_default", "as_ref", "as_deref", "to_string",
}

COMPOSITION_SKIP_HTTP = {
    "start_server", "create_app", "routes", "public_routes", "protected_routes", "liveview_router",
}
CLI_DISPATCH_SKIP = {"main", "run_async_cli", "handle_command"}


@dataclass(frozen=True)
class FnDef:
    path: str
    name: str
    qual: str | None
    body: str


def match_brace(text: str, open_pos: int) -> int:
    depth = 0
    i = open_pos
    in_str = False
    in_char = False
    escape = False
    line_comment = False
    block_comment = 0
    while i < len(text):
        c = text[i]
        n = text[i + 1] if i + 1 < len(text) else ""
        if line_comment:
            if c == "\n": line_comment = False
            i += 1; continue
        if block_comment:
            if c == "/" and n == "*": block_comment += 1; i += 2; continue
            if c == "*" and n == "/": block_comment -= 1; i += 2; continue
            i += 1; continue
        if in_str:
            if escape: escape = False
            elif c == "\\": escape = True
            elif c == '"': in_str = False
            i += 1; continue
        if in_char:
            if escape: escape = False
            elif c == "\\": escape = True
            elif c == "'": in_char = False
            i += 1; continue
        if c == "/" and n == "/": line_comment = True; i += 2; continue
        if c == "/" and n == "*": block_comment = 1; i += 2; continue
        if c == '"': in_str = True; i += 1; continue
        if c == "'": in_char = True; i += 1; continue
        if c == "{": depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0: return i
        i += 1
    return len(text) - 1


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    return text


class RustIndex:
    def __init__(self, root: Path):
        self.root = root
        self.by_name: dict[str, list[FnDef]] = {}
        self.by_qual: dict[str, list[FnDef]] = {}
        self.by_file: dict[str, list[FnDef]] = {}
        self._build()

    def _build(self):
        for f in self.root.rglob("*.rs"):
            rel = f.relative_to(self.root).as_posix()
            if "/tests/" in f"/{rel}/" or rel.startswith("target/"):
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            impl_spans = []
            for im in IMPL_RE.finditer(text):
                op = text.find("{", im.start())
                if op < 0: continue
                end = match_brace(text, op)
                impl_spans.append((op, end, im.group(1)))
            defs = []
            for m in FN_DEF_RE.finditer(text):
                op = text.find("{", m.start())
                if op < 0: continue
                end = match_brace(text, op)
                owner = None
                for a,b,t in impl_spans:
                    if a < m.start() < b:
                        owner = t
                        break
                d = FnDef(rel, m.group(1), f"{owner}::{m.group(1)}" if owner else None, text[op+1:end])
                defs.append(d)
                self.by_name.setdefault(d.name, []).append(d)
                if d.qual: self.by_qual.setdefault(d.qual, []).append(d)
            if defs: self.by_file[rel] = defs

    def find_in_file(self, path: str, name: str) -> FnDef | None:
        last = name.split("::")[-1]
        for d in self.by_file.get(path, []):
            if d.name == last and ("::" not in name or d.qual == name or name.endswith("::"+d.name)):
                return d
        for d in self.by_file.get(path, []):
            if d.name == last: return d
        return None

    def resolve(self, call: str) -> FnDef | None:
        if "::" in call:
            tail2 = "::".join(call.split("::")[-2:])
            xs = self.by_qual.get(tail2, [])
            if len(xs) == 1: return xs[0]
        name = call.split("::")[-1]
        xs = self.by_name.get(name, [])
        if len(xs) == 1: return xs[0]
        return None

    def internal_calls(self, d: FnDef) -> list[tuple[str, FnDef]]:
        code = strip_comments(d.body)
        raw = []
        raw.extend(m.group(1) for m in CALL_NAME_RE.finditer(code))
        raw.extend(m.group(1) for m in re.finditer(r"\.([A-Za-z_][A-Za-z0-9_]*)\s*\(", code))
        out=[]; seen=set()
        for c in raw:
            last=c.split("::")[-1]
            if last in SKIP_NAMES or last == d.name: continue
            target=self.resolve(c)
            if not target: continue
            key=(c,target.path,target.name)
            if key in seen: continue
            seen.add(key); out.append((c,target))
        return out


def parse_rows(text: str):
    m=DETAIL_RE.search(text)
    if not m: return []
    rows=[]
    for line in m.group(0).splitlines():
        mm=ROW_RE.match(line)
        if mm:
            _,f,s,w,st=mm.groups(); rows.append((f,s,w,st))
    return rows


def render_rows(rows):
    lines=['','## 穿过的源码文件（详细）','',
           '| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |',
           '|---:|---|---|---|---|']
    for i,(f,s,w,st) in enumerate(rows,1):
        lines.append(f'| {i} | `{f}` | `{s.replace("|","/")}` | {w.replace("|","/")} | {st.replace("|","/")} |')
    lines += ['', '> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。','']
    return '\n'.join(lines)


def replace_flow(text: str, flow: str):
    m=FLOW_RE.search(text)
    if not m: raise RuntimeError('E2E flow not found')
    return text[:m.start()] + m.group(1) + '```text\n' + flow.rstrip() + '\n```' + text[m.end():]


def replace_rows(text: str, rows):
    m=DETAIL_RE.search(text)
    if not m: raise RuntimeError('detailed source table not found')
    return text[:m.start()] + '\n' + render_rows(rows).rstrip() + '\n' + text[m.end():]


def server_flow(entry: str, mode_note: str = '') -> str:
    note = f"│    └─ {mode_note}\n" if mode_note else ''
    return f'''START
│
├─ Shell / OS 入口
│    └─ {entry}
{note}│
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
│    └─ 此路径不会进入 src/cli/commands.rs
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
END = server shutdown or fatal serve error'''


def bare_flow() -> str:
    return '''START
│
├─ Shell / OS: burncloud（无参数）
│
▼
FILE: src/main.rs
│
├─ main()
│    ├─ dotenvy::dotenv()
│    ├─ ensure_master_key()
│    ├─ init_logging()
│    └─ match args == [binary]
│
├─ DECISION: target_os == windows?
│    ├─ YES
│    │    ├─ std::thread::spawn(background server thread)
│    │    │    ├─ tokio::runtime::Runtime::new()
│    │    │    ├─ HOST / PORT
│    │    │    └─ burncloud_server::start_server(host, port, false)
│    │    │         └─ enable_liveview=false：后台 Server 不挂 LiveView Router
│    │    └─ main thread → burncloud_client::launch_gui_with_tray()
│    │
│    └─ NO（Linux/macOS 等）
│         ├─ print Headless Mode startup line
│         └─ run_async_server()
│              └─ burncloud_server::start_server(host, port, true)
│
├─ Windows server thread 后续主链与 `burncloud server` 的 start_server/create_app/create_router_app 相同
├─ Non-Windows 后续主链与 `burncloud server` 完全相同
│
▼
FILE: crates/client/src/app.rs
│
├─ Windows GUI branch: launch_gui_with_tray()
│    ├─ WindowBuilder
│    ├─ Config::new().with_window(...).with_data_directory(...)
│    └─ LaunchBuilder::desktop().launch(AppWithTray)
│
├─ AppWithTray()
│    ├─ DesktopMode context
│    ├─ maximize window
│    ├─ std::thread::spawn(start_tray)
│    ├─ spawn async show-window poll loop
│    └─ render App()
│
└─ App()
     ├─ use_init_i18n()
     ├─ use_init_toast()
     ├─ use_init_auth()
     ├─ use_init_theme()
     └─ Router<Route>
│
▼
END / LONG-RUNNING SERVER + UI LOOPS'''


def client_flow() -> str:
    return '''START
│
├─ Shell: burncloud client
│
▼
FILE: src/main.rs
│
├─ main()
│    ├─ dotenvy::dotenv()
│    ├─ ensure_master_key()
│    ├─ init_logging()
│    └─ match subcommand == "client"
│
├─ DECISION: target_os == windows?
│    ├─ YES → burncloud_client::launch_gui_with_tray()
│    └─ NO
│         ├─ println("Desktop GUI is only available on Windows.")
│         ├─ println("On Linux, use 'burncloud server' ...")
│         └─ return Ok(()) → END
│
▼
FILE: crates/client/src/app.rs
│
├─ launch_gui_with_tray()
│    ├─ WindowBuilder::new()
│    ├─ configure title / size / resizable / decorations
│    ├─ load Windows icon when available
│    ├─ temp_dir()/burncloud_webview_data
│    ├─ Config::new().with_window(...).with_data_directory(...)
│    └─ LaunchBuilder::desktop().with_cfg(config).launch(AppWithTray)
│
├─ AppWithTray()
│    ├─ use_context_provider(DesktopMode)
│    ├─ use_window()
│    ├─ use_effect → set_maximized(true)
│    ├─ std::thread::spawn → start_tray()
│    ├─ use_effect → spawn async 100ms show-window poll
│    │    └─ should_show_window() → set_visible / set_focus
│    └─ rsx! { App {} }
│
├─ App()
│    ├─ use_init_i18n()
│    ├─ use_init_toast()
│    ├─ use_init_auth()
│    ├─ use_init_theme()
│    ├─ ToastContainer
│    └─ Router<Route>
│
▼
END / DESKTOP EVENT LOOP'''


SERVER_ROWS = [
('src/main.rs','main(), is_valid_master_key(), ensure_master_key(), run_async_server()','真实 direct-mode 分发；server/router 不经过 Clap','PROCESS / ENV / filesystem'),
('crates/server/src/logging.rs','init_logging(), file_appender(), module_filter()','main() 在 direct mode 分发前初始化 tracing','INIT logs/files'),
('crates/server/src/lib.rs','start_server(), create_app()','统一 Server 启动与 Axum App composition','INIT DB/router/listener'),
('crates/database/src/database.rs','create_default_database(), Database::new(), Database::initialize(), DatabaseConnection::new(), get_default_database_path()','start_server() 的数据库创建与连接主链','READ ENV / WRITE DB file / CONNECT'),
('crates/database/src/migration/mod.rs','MigrationRunner::run()','Database::initialize() 执行版本化 DDL migration','READ/WRITE schema'),
('crates/database/src/schema/mod.rs','Schema::init(), rename/router/price/user migration calls','MigrationRunner 后执行数据修复和 seed','READ/WRITE database'),
('crates/database/crates/router/src/lib.rs','RouterDatabase::init(), RouterDatabase::insert_log(), RouterDatabase::insert_request_log()','启动建表兼容 + 后台日志 writer 的 DB facade','READ/WRITE router state'),
('crates/database/crates/user/src/lib.rs','UserDatabase::init(), assign_role()','启动用户/角色表初始化及 orphan role 修复','READ/WRITE user state'),
('crates/service/crates/monitor/src/service.rs','SystemMonitorService::new(), start_auto_update(), collect_metrics_internal()','create_app() 初始化并启动系统指标后台采集','SPAWN / READ OS / WRITE cache'),
('crates/service/crates/cache/src/service.rs','CacheService::new(), with_config(), is_available()','create_app() 初始化可选 Redis cache','NETWORK Redis / cache state'),
('crates/router/src/lib.rs','create_router_app(), configure_rate_budget_from_db()','构造 Data Plane runtime、internal routes 和多条后台任务','INIT/SPAWN router runtime'),
('crates/router/src/balancer/mod.rs','RoundRobinBalancer::new()','create_router_app() 构造 balancer','INIT memory state'),
('crates/router/src/limiter.rs','RateLimiter::new()','create_router_app() 构造本地 token-bucket limiter','INIT memory state'),
('crates/router/src/circuit_breaker.rs','CircuitBreaker::new()','create_router_app() 构造 circuit breaker','INIT breaker state'),
('crates/router/src/model_router.rs','ModelRouter::new()','create_router_app() 构造模型/渠道路由器','INIT router DB handle'),
('crates/router/src/channel_state.rs','ChannelStateTracker::new()','create_router_app() 构造运行态 Channel state tracker','INIT memory state'),
('crates/router/src/adaptor/factory.rs','DynamicAdaptorFactory::new()','create_router_app() 构造动态协议 adaptor factory','INIT adaptor cache/DB'),
('crates/router/src/adaptor/detector.rs','ApiVersionDetector::new()','create_router_app() 构造 API version detector','INIT DB handle'),
('crates/service/crates/billing/src/cache.rs','PriceCache::load(), refresh(), empty()','Router 启动加载模型价格 cache','READ billing_prices / WRITE memory cache'),
('crates/service/crates/billing/src/calculator.rs','CostCalculator::new()','Router 启动构造计费计算器','INIT billing runtime'),
('crates/router/src/exchange_rate.rs','ExchangeRateService::new(), load_rates_from_db(), start_sync_task()','Router 启动加载汇率并启动 hourly task','READ DB / SPAWN'),
('crates/router/src/scheduler/mod.rs','load_scheduler_config()','Router 启动读取 SCHEDULER_POLICIES','READ ENV / INIT policy map'),
('crates/router/src/affinity.rs','AffinityCache::default()','Router 启动构造 L3 affinity cache','INIT memory cache'),
('crates/router/src/rate_budget.rs','InMemoryBudget::new(), configure()','Router 启动构造 L2 Shaper budget','INIT/WRITE memory budget'),
('crates/router/src/price_sync.rs','start_price_sync_task(), PriceSyncService::new(), sync_all()','Router 启动 price-sync background worker','SPAWN / NETWORK / WRITE price DB/cache'),
('crates/router/src/channel_health_manager.rs','ChannelHealthManager::new()','Router AppState 构造健康管理器','INIT health state'),
('crates/service/crates/user/src/lib.rs','UserService::new()','create_app() 构造 Management user service','INIT auth/user service'),
('crates/server/src/api/mod.rs','routes()','create_app() 构造 Public/Protected Management Router','REGISTER routes only'),
('crates/server/src/api/auth.rs','public_routes(), protected_routes()','api::routes() 启动期注册 auth routes','REGISTER handlers only'),
('crates/server/src/api/billing.rs','routes()','api::routes() 启动期注册 billing route','REGISTER handler only'),
('crates/server/src/api/channel.rs','routes()','api::routes() 启动期注册 channel routes','REGISTER handlers only'),
('crates/server/src/api/token.rs','routes()','api::routes() 启动期注册 token routes','REGISTER handlers only'),
('crates/server/src/api/log.rs','routes()','api::routes() 启动期注册 log/usage routes','REGISTER handlers only'),
('crates/server/src/api/monitor.rs','routes()','api::routes() 启动期注册 monitor route','REGISTER handler only'),
('crates/server/src/api/user.rs','routes()','api::routes() 启动期注册 user routes','REGISTER handlers only'),
('crates/server/src/api/security.rs','security_routes()','api::routes() 启动期注册 security routes','REGISTER handlers only'),
('crates/server/src/api/openapi.rs','routes()','api::routes() 启动期注册 OpenAPI/Swagger routes','REGISTER handlers only'),
('crates/server/src/api/cache.rs','routes()','api::routes() 启动期注册 cache routes','REGISTER handlers only'),
('crates/client/src/lib.rs','liveview_router()','enable_liveview=true 时构造 HTML shell/WebSocket Router；App callback 仅注册','REGISTER LiveView routes'),
]


def valid_rows(src: Path, rows):
    return [r for r in rows if (src/r[0]).is_file()]


def roots_from_flow(flow: str, rows, p, idx: RustIndex):
    roots=[]; seen=set()
    for fm in FILE_SEG_RE.finditer(flow):
        path=fm.group(1).strip()
        if not (idx.root/path).is_file(): continue
        for cm in CALL_NAME_RE.finditer(fm.group(2)):
            name=cm.group(1)
            last=name.split('::')[-1]
            if p['section']=='HTTP / API' and last in COMPOSITION_SKIP_HTTP: continue
            if p['section']=='CLI / Executables' and p['entry'] not in ('burncloud','burncloud server','burncloud router','burncloud client') and last in CLI_DISPATCH_SKIP: continue
            d=idx.find_in_file(path,name)
            if d and (d.path,d.name) not in seen:
                seen.add((d.path,d.name)); roots.append(d)
    if not roots:
        for f,s,_,_ in rows:
            if not (idx.root/f).is_file(): continue
            for name in CALL_NAME_RE.findall(s):
                last=name.split('::')[-1]
                if p['section']=='HTTP / API' and last in COMPOSITION_SKIP_HTTP: continue
                if p['section']=='CLI / Executables' and p['entry'] not in ('burncloud','burncloud server','burncloud router','burncloud client') and last in CLI_DISPATCH_SKIP: continue
                d=idx.find_in_file(f,name)
                if d and (d.path,d.name) not in seen:
                    seen.add((d.path,d.name)); roots.append(d)
    return roots


def expand(idx: RustIndex, roots, depth=2, limit=28):
    edges=[]; discovered=[]; seen_defs=set(); queue=[(d,0) for d in roots]
    while queue and len(seen_defs)<limit:
        d,dep=queue.pop(0)
        key=(d.path,d.name,d.qual)
        if key in seen_defs: continue
        seen_defs.add(key); discovered.append(d)
        if dep>=depth: continue
        for call,t in idx.internal_calls(d):
            edges.append((d,call,t))
            tkey=(t.path,t.name,t.qual)
            if tkey not in seen_defs: queue.append((t,dep+1))
    return discovered,edges


def trace_block(discovered, edges):
    if not discovered: return ''
    by_caller={}
    for a,c,b in edges: by_caller.setdefault((a.path,a.name),[]).append((c,b))
    lines=['├─ 源码函数展开（静态扫描确认）']
    by_file={}
    for d in discovered: by_file.setdefault(d.path,[]).append(d)
    files=list(by_file.items())
    for fi,(path,defs) in enumerate(files):
        lines.append('│    '+('└─ ' if fi==len(files)-1 else '├─ ')+f'FILE: {path}')
        for d in defs:
            q=d.qual or d.name
            lines.append('│    │    ├─ '+q+'()')
            calls=by_caller.get((d.path,d.name),[])[:10]
            for c,t in calls:
                lines.append('│    │    │    └─ CALL → '+(t.qual or t.name)+'() @ '+t.path)
    lines += ['│','├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件']
    return '\n'.join(lines)


def inject_trace(flow: str, block: str):
    if not block or '源码函数展开（静态扫描确认）' in flow: return flow
    i=flow.rfind('\n▼\nEND')
    if i<0: return flow+'\n│\n'+block
    return flow[:i]+'\n│\n'+block+'\n│\n'+flow[i:]


def add_discovered_rows(src:Path, rows, discovered, edges):
    out=list(rows); seen={r[0] for r in out}
    incoming={}
    for a,c,b in edges: incoming.setdefault(b.path,[]).append((a,c,b))
    for d in discovered:
        if d.path in seen or not (src/d.path).is_file(): continue
        inc=incoming.get(d.path,[])
        if not inc: continue
        symbols=', '.join(sorted({(x[2].qual or x[2].name)+'()' for x in inc})[:8])
        why='；'.join(sorted({f'由 {(x[0].qual or x[0].name)}() 直接调用' for x in inc})[:3])
        out.append((d.path,symbols,why,'CALL / runtime-specific'))
        seen.add(d.path)
    return out


def special_direct(p, src, text):
    e=p['entry']
    if e in ('burncloud server','burncloud router'):
        note = '源码命令名为 router，但当前实现与 server 一样直接进入 run_async_server()' if e.endswith('router') else '显式 Server 模式；当前实现同时 enable_liveview=true'
        text=replace_flow(text,server_flow(e,note))
        text=replace_rows(text,valid_rows(src,SERVER_ROWS))
        return text,True
    if e=='burncloud':
        text=replace_flow(text,bare_flow())
        rows=[
            ('src/main.rs','main(), ensure_master_key(), run_async_server()','无参数平台分支：Windows server thread + GUI；非 Windows headless server','PROCESS/SPAWN'),
            ('crates/server/src/logging.rs','init_logging()','main() 初始化日志','INIT logs'),
            ('crates/server/src/lib.rs','start_server(), create_app()','Windows background server 或 non-Windows server 主链','LONG-RUNNING server'),
            ('crates/client/src/app.rs','launch_gui_with_tray(), AppWithTray(), App()','Windows main thread 桌面 GUI/tray','UI/SPAWN'),
        ]
        text=replace_rows(text,valid_rows(src,rows)); return text,True
    if e=='burncloud client':
        text=replace_flow(text,client_flow())
        rows=[
            ('src/main.rs','main()','client direct branch；非 Windows 直接打印提示并结束','PROCESS/platform branch'),
            ('crates/server/src/logging.rs','init_logging()','direct branch 前日志初始化','INIT logs'),
            ('crates/client/src/app.rs','launch_gui_with_tray(), AppWithTray(), App()','Windows Desktop Dioxus event loop','UI/SPAWN'),
        ]
        text=replace_rows(text,valid_rows(src,rows)); return text,True
    return text,False


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',required=True); ap.add_argument('--manifest',default='docs/atlas-manifest.json'); args=ap.parse_args()
    src=Path(args.source).resolve(); mp=Path(args.manifest); docs=mp.parent
    manifest=json.loads(mp.read_text(encoding='utf-8'))
    idx=RustIndex(src)
    changed=0; special=0; traced=0; new_files=0
    for p in manifest['pages']:
        path=docs/(p['docid']+'.md'); text=path.read_text(encoding='utf-8')
        text,is_special=special_direct(p,src,text)
        if is_special:
            special+=1
        fm=FLOW_RE.search(text)
        if not fm: raise RuntimeError(f'flow missing: {path}')
        rows=parse_rows(text)
        if not rows: raise RuntimeError(f'source rows missing: {path}')
        roots=roots_from_flow(fm.group(2),rows,p,idx)
        discovered,edges=expand(idx,roots,depth=2,limit=28)
        tb=trace_block(discovered,edges)
        if tb:
            new_flow=inject_trace(fm.group(2),tb)
            text=text[:fm.start()]+fm.group(1)+'```text\n'+new_flow.rstrip()+'\n```'+text[fm.end():]
            traced+=1
        before=len(rows)
        rows=add_discovered_rows(src,rows,discovered,edges)
        new_files += len(rows)-before
        text=replace_rows(text,rows)
        text=text.replace('**Execution classification: STATIC CONFIRMED**','**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION**')
        path.write_text(text,encoding='utf-8'); changed+=1
    print(f'Execution Truth V4: pages={changed}, special_direct_modes={special}, function_trace_pages={traced}, newly_resolved_source_files={new_files}, indexed_functions={sum(len(v) for v in idx.by_file.values())}')

if __name__=='__main__': main()
