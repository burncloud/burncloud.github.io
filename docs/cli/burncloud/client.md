---
title: "client"
slug: /cli/burncloud/client
hide_table_of_contents: true
---

# client

**树路径：** `BurnCloud → CLI / Executables → burncloud → client`

> **中文解释：** 显式启动 Client 模式。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
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
END / DESKTOP EVENT LOOP
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ burncloud client
```

## 返回结果示例

> 以下为构造的典型终端输出示例；真实 ID、路径、金额、模型、版本与状态以实际 CLI 执行为准。

```text
BurnCloud client starting...
ui=ready
status=running
```






## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `main()` | client direct branch；非 Windows 直接打印提示并结束 | PROCESS/platform branch |
| 2 | `crates/server/src/logging.rs` | `init_logging()` | direct branch 前日志初始化 | INIT logs |
| 3 | `crates/client/src/app.rs` | `launch_gui_with_tray(), AppWithTray(), App()` | Windows Desktop Dioxus event loop | UI/SPAWN |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + BRANCH-SENSITIVE DIRECT MODE** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
