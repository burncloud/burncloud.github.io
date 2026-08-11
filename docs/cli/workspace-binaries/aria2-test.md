---
title: "aria2-test"
slug: /cli/workspace-binaries/aria2-test
hide_table_of_contents: true
---

# aria2-test

**树路径：** `BurnCloud → CLI / Executables → Workspace Binaries → aria2-test`

> **中文解释：** 独立 aria2 集成测试 binary：quick_start() 启动 Aria2Manager，创建 RPC client，读取全局统计和活跃任务，添加测试下载、查询任务状态，最后 shutdown manager。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ OS / Shell 启动 binary
│    └─ aria2-test
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ #[tokio::main] main()
├─ print "启动 BurnCloud Aria2 测试"
└─ CALL quick_start().await
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ quick_start()
│    ├─ Aria2Manager::new()
│    ├─ manager.download_and_setup().await
│    └─ manager.start_daemon().await
│
├─ Aria2Manager::download_and_setup()
│    └─ download_aria2()
│         ├─ determine BurnCloud local directory
│         ├─ DECISION: aria2c.exe already exists?
│         │    ├─ YES → reuse existing binary
│         │    └─ NO  → download main URL
│         │         └─ DECISION: main download succeeds?
│         │              ├─ YES → extract ZIP
│         │              └─ NO  → try backup URL → extract ZIP
│         └─ DECISION: extracted aria2c.exe exists?
│              ├─ NO → Aria2Error::DownloadError → END
│              └─ YES → return executable path
│
├─ Aria2Manager::start_daemon()
│    ├─ DECISION: daemon already exists?
│    │    ├─ YES → Aria2Error::DaemonError → END
│    │    └─ NO  → Aria2Daemon::new(...)
│    └─ Aria2Daemon::start().await
│         ├─ start_aria2_rpc(&config)
│         ├─ persist Aria2Instance in Arc<Mutex<Option<_>>>
│         ├─ is_running = true
│         └─ tokio::spawn daemon monitor loop
│              ├─ sleep 1 second
│              ├─ DECISION: aria2 child still running?
│              │    ├─ YES → continue monitoring
│              │    └─ NO  → start_aria2_rpc() restart attempt
│              └─ repeat while is_running
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ manager.create_rpc_client()
└─ DECISION: RPC client available?
     ├─ NO  → skip RPC tests → shutdown
     └─ YES → test_basic_operations(&client)
│
├─ test_basic_operations()
│    ├─ client.get_global_stat().await
│    │    └─ JSON-RPC aria2.getGlobalStat
│    └─ client.tell_active().await
│         └─ JSON-RPC aria2.tellActive
│
├─ test_download()
│    ├─ construct DownloadOptions { dir: "./downloads", ... }
│    └─ client.add_uri(test_url, options).await
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ Aria2RpcClient::add_uri()
│    ├─ find_existing_task(...)
│    │    ├─ tell_active()
│    │    ├─ tell_waiting()
│    │    ├─ tell_stopped()
│    │    └─ tell_status() / get_files() when checking duplicates
│    └─ DECISION: identical task already exists?
│         ├─ YES → return existing gid
│         └─ NO  → call_method("aria2.addUri", ...)
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ DECISION: add_uri succeeded?
│    ├─ NO  → print failure, continue cleanup
│    └─ YES
│         ├─ print GID
│         ├─ sleep 1 second
│         └─ client.tell_status(&gid)
│
├─ sleep 2 seconds
└─ manager.shutdown().await
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ Aria2Manager::shutdown()
│    └─ Aria2Daemon::stop()
│         ├─ is_running = false
│         ├─ kill aria2 child process if present
│         └─ clear daemon instance
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ print "测试完成，管理器已关闭"
└─ return Ok(())
│
▼
END
```

## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ aria2-test
```

## 返回结果示例

> 以下为构造的典型成功终端输出；端口、GID、下载速度和文件大小由实际 aria2 运行状态决定。

```text
🚀 启动 BurnCloud Aria2 测试...
aria2 RPC 服务已启动在端口: 6800
aria2 守护进程启动成功！
✅ Aria2 管理器启动成功
📡 获取到 RPC 客户端
🔍 测试基本操作...
  - 活跃下载: 0
  - 等待下载: 0
  - 下载速度: 0
  - 当前活跃任务数: 0
📥 测试下载功能...
  - 添加下载任务成功，GID: 2089b05ecca3d829
  - 任务状态: active
Aria2Manager 已关闭
🛑 测试完成，管理器已关闭
```


## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/download/crates/download-aria2/src/main.rs` | `见上方 E2E 对应函数/入口` | 该 CLI/UI/Background/Startup 页面真实执行文件 | runtime-specific |
| 2 | `crates/download/crates/download-aria2/src/lib.rs` | `见上方 E2E 对应函数/入口` | 该 CLI/UI/Background/Startup 页面真实执行文件 | runtime-specific |

> 这个索引只列入当前执行链中有源码依据的文件；类型定义文件但不执行逻辑的，不为了凑数量加入。

**Execution classification: STATIC CONFIRMED** — 入口来自当前 workspace 的 `[[bin]]` / `src/main.rs` 定义。
