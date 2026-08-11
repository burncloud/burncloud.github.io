---
title: "src/main.rs"
slug: /startup/src-main.rs
hide_table_of_contents: true
---

# src/main.rs

**树路径：** `BurnCloud → Startup → Startup Chain → src/main.rs`

> **中文解释：** 进程入口：dotenv → MASTER_KEY → logging → 平台/argv 分发；无参数按平台启动 GUI/LiveView，显式参数进入 server/router/client/CLI。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Process/environment input
│    ├─ startup target: src/main.rs
│    ├─ environment variables / dotenv
│    ├─ CLI/platform mode
│    └─ filesystem/database availability
│
├─ Enter startup function
│    └─ execute src/main.rs
│
├─ Dependency initialization
│    ├─ construct required DB/services/runtime state
│    ├─ register routes/tasks as applicable
│    └─ DECISION: dependency initialization succeeds?
│         ├─ NO → propagate startup error → process/runtime not ready → END
│         └─ YES → next dependency
│
├─ Runtime composition
│    ├─ wire shared Arc/State/services
│    ├─ compose routers/middleware/background jobs
│    └─ make dependencies reachable from runtime entrypoints
│
├─ Readiness boundary
│    └─ DECISION: all required startup stages complete?
│         ├─ NO → startup fails/returns Err
│         └─ YES → expose listener/client/event loop/runtime
│
├─ Steady-state handoff
│    ├─ long-running loops take ownership of runtime
│    └─ requests/events can now enter documented entrypoints
│
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: src/main.rs
│    │    ├─ main()
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → ensure_master_key() @ src/main.rs
│    │    │    └─ CALL → init_logging() @ crates/server/src/logging.rs
│    │    │    └─ CALL → start_server() @ crates/server/src/lib.rs
│    │    │    └─ CALL → launch_gui_with_tray() @ crates/client/src/app.rs
│    │    │    └─ CALL → run_async_server() @ src/main.rs
│    │    │    └─ CALL → run_async_cli() @ src/main.rs
│    │    │    └─ CALL → show_help() @ src/cli/commands.rs
│    │    ├─ ensure_master_key()
│    │    │    └─ CALL → is_valid_master_key() @ src/main.rs
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    ├─ run_async_server()
│    │    │    └─ CALL → start_server() @ crates/server/src/lib.rs
│    │    ├─ run_async_cli()
│    │    │    └─ CALL → handle_command() @ src/cli/commands.rs
│    │    ├─ is_valid_master_key()
│    ├─ FILE: crates/server/src/api/response.rs
│    │    ├─ ok()
│    ├─ FILE: crates/server/src/logging.rs
│    │    ├─ init_logging()
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → file_appender() @ crates/server/src/logging.rs
│    │    │    └─ CALL → module_filter() @ crates/server/src/logging.rs
│    │    ├─ file_appender()
│    │    ├─ module_filter()
│    ├─ FILE: crates/server/src/lib.rs
│    │    ├─ start_server()
│    │    │    └─ CALL → create_default_database() @ crates/database/src/database.rs
│    │    │    └─ CALL → RouterDatabase::init() @ crates/database/crates/router/src/lib.rs
│    │    │    └─ CALL → UserDatabase::init() @ crates/database/crates/user/src/lib.rs
│    │    │    └─ CALL → create_app() @ crates/server/src/lib.rs
│    │    ├─ create_app()
│    ├─ FILE: crates/client/src/app.rs
│    │    ├─ launch_gui_with_tray()
│    ├─ FILE: src/cli/commands.rs
│    │    ├─ show_help()
│    │    ├─ handle_command()
│    ├─ FILE: crates/database/src/database.rs
│    │    ├─ create_default_database()
│    ├─ FILE: crates/database/crates/router/src/lib.rs
│    │    ├─ RouterDatabase::init()
│    └─ FILE: crates/database/crates/user/src/lib.rs
│    │    ├─ UserDatabase::init()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
     └─ component is READY / RUNNING
```


## 输入示例

> Startup 的输入是进程模式、环境变量、配置和外部资源可用性，而不是 API Request。

```text
process_target=src/main.rs
BURNCLOUD_MASTER_KEY=<configured-or-generated>
RUST_LOG=info
database_path=<runtime database>
enable_liveview=true
# 真实环境变量/参数以部署配置为准。
```

## 返回结果示例

> Startup 页面没有传统 API response；这里用构造的启动结果/运行态日志表示该阶段成功完成后系统应进入的状态。

```text
dotenv=loaded
master_key=ready
logging=initialized
mode=server+liveview
startup_dispatch=success
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `main()` | BurnCloud process bootstrap / top-level dispatch | PROCESS |
| 2 | `crates/server/src/api/response.rs` | `ok()` | 由 ensure_master_key() 直接调用；由 init_logging() 直接调用；由 main() 直接调用 | CALL / runtime-specific |
| 3 | `crates/server/src/logging.rs` | `file_appender(), init_logging(), module_filter()` | 由 init_logging() 直接调用；由 main() 直接调用 | CALL / runtime-specific |
| 4 | `crates/server/src/lib.rs` | `create_app(), start_server()` | 由 main() 直接调用；由 run_async_server() 直接调用；由 start_server() 直接调用 | CALL / runtime-specific |
| 5 | `crates/client/src/app.rs` | `launch_gui_with_tray()` | 由 main() 直接调用 | CALL / runtime-specific |
| 6 | `src/cli/commands.rs` | `handle_command(), show_help()` | 由 main() 直接调用；由 run_async_cli() 直接调用 | CALL / runtime-specific |
| 7 | `crates/database/src/database.rs` | `create_default_database()` | 由 start_server() 直接调用 | CALL / runtime-specific |
| 8 | `crates/database/crates/router/src/lib.rs` | `RouterDatabase::init()` | 由 start_server() 直接调用 | CALL / runtime-specific |
| 9 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::init()` | 由 start_server() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
