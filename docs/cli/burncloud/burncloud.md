---
title: "burncloud"
slug: /cli/burncloud/burncloud
hide_table_of_contents: true
---

# burncloud

**树路径：** `BurnCloud → CLI / Executables → burncloud → burncloud`

> **中文解释：** 无参数时按平台启动：Windows 为后台 Server + 桌面 GUI/tray；非 Windows 为 Server + LiveView。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
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
END / LONG-RUNNING SERVER + UI LOOPS
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ burncloud
```

## 返回结果示例

> 无参数启动存在平台分支；下面分别给出源码可确认的终态/输出语义。

```text
# 非 Windows
Starting BurnCloud Server with LiveView (Headless Mode)...
Unified Gateway listening on 127.0.0.1:3000
- Dashboard: http://127.0.0.1:3000/
- LLM API:   http://127.0.0.1:3000/v1/...

# Windows
background_server_thread=running (enable_liveview=false)
desktop_gui_event_loop=running
system_tray_thread=running
```


## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `main(), ensure_master_key(), run_async_server()` | 无参数平台分支：Windows server thread + GUI；非 Windows headless server | PROCESS/SPAWN |
| 2 | `crates/server/src/logging.rs` | `init_logging()` | main() 初始化日志 | INIT logs |
| 3 | `crates/server/src/lib.rs` | `start_server(), create_app()` | Windows background server 或 non-Windows server 主链 | LONG-RUNNING server |
| 4 | `crates/client/src/app.rs` | `launch_gui_with_tray(), AppWithTray(), App()` | Windows main thread 桌面 GUI/tray | UI/SPAWN |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + BRANCH-SENSITIVE DIRECT MODE** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
