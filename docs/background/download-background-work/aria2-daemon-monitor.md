---
title: "Aria2 Daemon Monitor"
slug: /background/download-background-work/aria2-daemon-monitor
hide_table_of_contents: true
---

# Aria2 Daemon Monitor

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Download Background Work → Aria2 Daemon Monitor`

> **中文解释：** Aria2Daemon::start() 内的 tokio::spawn 监控循环：每秒检查 aria2 child process；进程退出时调用 start_aria2_rpc() 尝试重新启动，stop() 将 running 置 false 后终止循环。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Aria2Manager::start_daemon()
│
▼
FILE: crates/download/crates/download-aria2/src/lib.rs
│
├─ Aria2Daemon::start()
│    ├─ DECISION: is_running already true?
│    │    ├─ YES → DaemonError → END
│    │    └─ NO → start_aria2_rpc()
│    ├─ save Aria2Instance in Arc<Mutex<Option<_>>>
│    ├─ is_running = true
│    └─ tokio::spawn monitor task
│
├─ Monitor loop
│    ├─ WHILE is_running == true
│    ├─ sleep 1000 ms
│    ├─ lock instance
│    └─ DECISION: aria2 child process still running?
│         ├─ YES → next iteration
│         └─ NO
│              ├─ print restart message
│              ├─ CALL start_aria2_rpc(&config)
│              └─ DECISION: restart succeeds?
│                   ├─ NO → keep loop alive; retry on later iteration
│                   └─ YES → replace stored Aria2Instance
│
├─ Stop path
│    └─ Aria2Daemon::stop()
│         ├─ is_running = false
│         ├─ kill existing child
│         └─ instance = None
│
│
├─ 源码函数展开（静态扫描确认）
│    └─ FILE: crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ std::start()
│    │    │    └─ CALL → std::start_aria2_rpc() @ crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ std::start_aria2_rpc()
│    │    │    └─ CALL → std::kill_existing_aria2() @ crates/download/crates/download-aria2/src/lib.rs
│    │    │    └─ CALL → std::find_available_port() @ crates/download/crates/download-aria2/src/lib.rs
│    │    │    └─ CALL → std::wait_for_rpc_ready() @ crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ std::stop()
│    │    │    └─ CALL → std::kill() @ crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ std::kill_existing_aria2()
│    │    ├─ std::find_available_port()
│    │    │    └─ CALL → std::check_port_available() @ crates/download/crates/download-aria2/src/lib.rs
│    │    ├─ std::wait_for_rpc_ready()
│    │    ├─ std::kill()
│    │    ├─ std::check_port_available()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END / NEXT ITERATION
```

## 输入示例

> 后台任务通常没有 HTTP 请求体；这里把触发事件、队列/定时器和共享状态视为它的输入。

```text
trigger=Download Background Work
job=Aria2 Daemon Monitor
runtime=running
shared_state=available
# 该类页面的“输入”不是 HTTP body，而是启动事件、定时器、队列消息或请求侧异步事件。
```

## 返回结果示例

> 后台任务通常不会直接向 HTTP 调用方返回 JSON；这里用一条构造的状态/日志结果表示一次成功执行后的可观测结果。

```text
job=Aria2 Daemon Monitor
status=success
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/download/crates/download-aria2/src/lib.rs` | `download / aria2 runtime symbols` | Download manager / RPC execution | NETWORK/filesystem/process state |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页来自运行时代码中的真实 background/thread 入口。
