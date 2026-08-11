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
├─ OS / Shell 启动 binary: aria2-test
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
│    ├─ download_and_setup()
│    │    └─ download_aria2()
│    │         ├─ DECISION: aria2c.exe already exists?
│    │         │    ├─ YES → reuse
│    │         │    └─ NO  → main download → fallback backup download
│    │         ├─ extract_aria2()
│    │         └─ DECISION: executable exists after extraction?
│    │              ├─ NO → Aria2Error::DownloadError → END
│    │              └─ YES → continue
│    └─ start_daemon()
│         └─ Aria2Daemon::start()
│              ├─ start_aria2_rpc()
│              ├─ store Aria2Instance
│              ├─ is_running = true
│              └─ tokio::spawn daemon monitor loop
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ manager.create_rpc_client()
├─ DECISION: RPC client exists?
│    ├─ NO → skip tests → cleanup
│    └─ YES
│         ├─ test_basic_operations()
│         │    ├─ get_global_stat() → aria2.getGlobalStat
│         │    └─ tell_active() → aria2.tellActive
│         └─ test_download()
│              └─ add_uri(test_url, DownloadOptions)
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ Aria2RpcClient::add_uri()
│    ├─ find_existing_task()
│    │    ├─ tell_active()
│    │    ├─ tell_waiting()
│    │    ├─ tell_stopped()
│    │    └─ tell_status() / get_files()
│    └─ DECISION: identical task exists?
│         ├─ YES → return existing gid
│         └─ NO  → call_method("aria2.addUri", ...)
│
▼
FILE: crates/download/crates/download-aria2/src/main.rs
│
├─ DECISION: add_uri success?
│    ├─ NO → print error; continue cleanup
│    └─ YES → print gid → sleep → tell_status(gid)
├─ sleep 2 seconds
└─ manager.shutdown()
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ Aria2Manager::shutdown()
│    └─ Aria2Daemon::stop()
│         ├─ is_running = false
│         ├─ kill child process
│         └─ clear instance
│
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ quick_start()
│    │    │    └─ CALL → Aria2Manager::new() @ crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ Aria2RpcClient::new()
│    │    ├─ Aria2Manager::download_and_setup()
│    │    │    └─ CALL → download_aria2() @ crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ download_aria2()
│    │    │    └─ CALL → get_burncloud_dir() @ crates/download/crates/download-aria2/src/lib.rs
│    │    │    └─ CALL → download_file() @ crates/download/crates/download-aria2/src/lib.rs
│    │    │    └─ CALL → extract_aria2() @ crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ extract_aria2()
│    │    ├─ Aria2Manager::start_daemon()
│    │    │    └─ CALL → Aria2Daemon::new() @ crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ Aria2Daemon::start()
│    │    │    └─ CALL → start_aria2_rpc() @ crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ start_aria2_rpc()
│    │    │    └─ CALL → kill_existing_aria2() @ crates/download/crates/download-aria2/src/lib.rs
│    │    │    └─ CALL → find_available_port() @ crates/download/crates/download-aria2/src/lib.rs
│    │    │    └─ CALL → wait_for_rpc_ready() @ crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ Aria2RpcClient::add_uri()
│    │    ├─ Aria2RpcClient::find_existing_task()
│    │    ├─ Aria2RpcClient::tell_active()
│    │    ├─ Aria2RpcClient::tell_waiting()
│    │    ├─ Aria2RpcClient::tell_stopped()
│    │    ├─ Aria2RpcClient::tell_status()
│    │    ├─ Aria2RpcClient::get_files()
│    │    ├─ Aria2RpcClient::call_method()
│    │    ├─ Aria2RpcClient::shutdown()
│    │    ├─ Aria2Daemon::stop()
│    │    ├─ Aria2Manager::new()
│    │    ├─ get_burncloud_dir()
│    │    ├─ download_file()
│    │    ├─ Aria2Daemon::new()
│    │    ├─ kill_existing_aria2()
│    │    ├─ find_available_port()
│    │    │    └─ CALL → check_port_available() @ crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ wait_for_rpc_ready()
│    │    ├─ check_port_available()
│    └─ FILE: crates/download/crates/download-aria2/src/main.rs
│    │    ├─ test_basic_operations()
│    │    ├─ test_download()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
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
📥 测试下载功能...
  - 添加下载任务成功，GID: 2089b05ecca3d829
  - 任务状态: active
Aria2Manager 已关闭
🛑 测试完成，管理器已关闭
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/download/crates/download-aria2/src/main.rs` | `download / aria2 runtime symbols` | Download manager / RPC execution | NETWORK/filesystem/process state |
| 2 | `crates/download/crates/download-aria2/src/lib.rs` | `download / aria2 runtime symbols` | Download manager / RPC execution | NETWORK/filesystem/process state |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 入口来自当前 workspace 的 `[[bin]]` / `src/main.rs` 定义。
