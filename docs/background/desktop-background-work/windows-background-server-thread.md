---
title: "Windows Background Server Thread"
slug: /background/desktop-background-work/windows-background-server-thread
hide_table_of_contents: true
---

# Windows Background Server Thread

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Desktop Background Work → Windows Background Server Thread`

> **中文解释：** Windows 下无参数启动 burncloud.exe 时，main() 创建 std::thread::spawn，在新 Tokio Runtime 中调用 burncloud_server::start_server(host, port, false)，同时主线程继续 launch_gui_with_tray()。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ User launches burncloud.exe with no CLI arguments on Windows
│
▼
FILE: src/main.rs
│
├─ main()
│    ├─ dotenvy::dotenv()
│    ├─ ensure_master_key()
│    ├─ init_logging()
│    └─ DECISION: args == [binary] AND target_os == windows?
│         ├─ NO → other CLI/server/client branch
│         └─ YES → std::thread::spawn server thread
│
├─ Background OS thread
│    ├─ tokio::runtime::Runtime::new()
│    ├─ read HOST or default 127.0.0.1
│    ├─ read PORT or DEFAULT_PORT
│    └─ rt.block_on(burncloud_server::start_server(host, port, false))
│
▼
FILE: crates/server/src/lib.rs
│
├─ start_server(host, port, enable_liveview=false)
│    ├─ create_default_database()
│    ├─ RouterDatabase::init()
│    ├─ UserDatabase::init()
│    ├─ create_app(db, false)
│    ├─ TcpListener::bind()
│    └─ axum::serve()
│
├─ DECISION: server startup/runtime returns Err?
│    ├─ YES → src/main.rs thread prints "Server failed to start"
│    └─ NO → server thread remains serving requests
│
▼
FILE: src/main.rs
│
└─ Main Windows thread independently continues
     └─ burncloud_client::launch_gui_with_tray()
│
▼
END / SERVER THREAD CONTINUES
```

## 输入示例

> 后台任务通常没有 HTTP 请求体；这里把触发事件、队列/定时器和共享状态视为它的输入。

```text
trigger=Desktop Background Work
job=Windows Background Server Thread
runtime=running
shared_state=available
# 该类页面的“输入”不是 HTTP body，而是启动事件、定时器、队列消息或请求侧异步事件。
```

## 返回结果示例

> 后台任务通常不会直接向 HTTP 调用方返回 JSON；这里用一条构造的状态/日志结果表示一次成功执行后的可观测结果。

```text
job=Windows Background Server Thread
status=success
```


## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `见上方 E2E 对应函数/入口` | 该 CLI/UI/Background/Startup 页面真实执行文件 | runtime-specific |
| 2 | `crates/server/src/lib.rs` | `见上方 E2E 对应函数/入口` | 该 CLI/UI/Background/Startup 页面真实执行文件 | runtime-specific |

> 这个索引只列入当前执行链中有源码依据的文件；类型定义文件但不执行逻辑的，不为了凑数量加入。

**Execution classification: STATIC CONFIRMED** — 本页来自运行时代码中的真实 background/thread 入口。
