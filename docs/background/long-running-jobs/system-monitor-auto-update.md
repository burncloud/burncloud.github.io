---
title: "System Monitor Auto Update"
slug: /background/long-running-jobs/system-monitor-auto-update
hide_table_of_contents: true
---

# System Monitor Auto Update

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Long-running Jobs → System Monitor Auto Update`

> **中文解释：** create_app() 启动 start_auto_update；周期采集 CPU、内存、磁盘并刷新内存缓存。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START / TRIGGER
│
├─ Trigger source
│    ├─ startup spawn / request-time tokio::spawn / manager restoration / channel message
│    └─ task: System Monitor Auto Update
│
├─ Spawn / registration
│    ├─ parent runtime creates async task/thread/loop
│    └─ DECISION: spawn/runtime handle available?
│         ├─ NO → task never starts; parent may log error
│         └─ YES → task owns/borrows required shared state
│
├─ Wait boundary
│    ├─ timer sleep / mpsc receive / polling interval / restored work item
│    └─ DECISION: trigger/event available?
│         ├─ NO → continue waiting
│         └─ YES → one iteration begins
│
├─ Input snapshot
│    ├─ read latest runtime/DB/request-derived state needed by job
│    └─ freeze iteration context
│
├─ Core job operation
│    ├─ execute System Monitor Auto Update
│    └─ may call DB / HTTP / filesystem / runtime service depending on task
│
├─ Operation result
│    └─ DECISION: iteration succeeds?
│         ├─ NO
│         │    ├─ log/record failure
│         │    ├─ preserve parent request availability when task is fail-open
│         │    └─ decide retry on next event/interval
│         └─ YES
│              ├─ update in-memory state and/or persistent state
│              └─ emit success telemetry/log
│
├─ Cancellation / lifetime
│    └─ DECISION: parent runtime still alive AND task should continue?
│         ├─ YES → 返回等待边界
│         └─ NO → release task resources
│
▼
END / NEXT ITERATION
```


## 输入示例

> 后台任务通常没有 HTTP 请求体；这里把触发事件、队列/定时器和共享状态视为它的输入。

```text
trigger=Long-running Jobs
job=System Monitor Auto Update
runtime=running
shared_state=available
# 该类页面的“输入”不是 HTTP body，而是启动事件、定时器、队列消息或请求侧异步事件。
```

## 返回结果示例

> 后台任务通常不会直接向 HTTP 调用方返回 JSON；这里用一条构造的状态/日志结果表示一次成功执行后的可观测结果。

```text
2026-08-11T14:45:10+08:00 monitor_update cpu=31.7% memory=62.4% disk=48.9% status=ok
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/service/crates/monitor/src/lib.rs` | `entry-specific function(s) shown in E2E` | 当前入口在该文件执行的直接调用点 | runtime-specific |
| 3 | `crates/service/crates/monitor/src/service.rs` | `SystemMonitorService::*` | metrics cache + collector coordination | READ OS / WRITE memory cache |
| 4 | `crates/service/crates/monitor/src/collectors/cpu.rs` | `Collector::collect*()` | OS metric collector | READ operating-system metrics |
| 5 | `crates/service/crates/monitor/src/collectors/memory.rs` | `Collector::collect*()` | OS metric collector | READ operating-system metrics |
| 6 | `crates/service/crates/monitor/src/collectors/disk.rs` | `Collector::collect*()` | OS metric collector | READ operating-system metrics |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
