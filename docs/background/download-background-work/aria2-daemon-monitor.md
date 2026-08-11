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
| 1 | `crates/download/crates/download-aria2/src/lib.rs` | `见上方 E2E 对应函数/入口` | 该 CLI/UI/Background/Startup 页面真实执行文件 | runtime-specific |

> 这个索引只列入当前执行链中有源码依据的文件；类型定义文件但不执行逻辑的，不为了凑数量加入。

**Execution classification: STATIC CONFIRMED** — 本页来自运行时代码中的真实 background/thread 入口。
