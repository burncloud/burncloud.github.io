---
title: "Health Probe Scheduler"
slug: /background/long-running-jobs/health-probe-scheduler
hide_table_of_contents: true
---

# Health Probe Scheduler

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Long-running Jobs → Health Probe Scheduler`

> **中文解释：** ProbeScheduler::start() 启动 10 秒 ticker。当前源码的 scheduler loop 只记录 Probe scheduler tick，注释明确说明真正的 Half-Open channel 探测、Adaptor probe 和结果记录仍是待实现语义，因此不能把它描述成已经发送健康探测。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Router runtime creates ProbeScheduler
└─ CALL ProbeScheduler::start()
│
▼
FILE: crates/router/src/health_probe.rs
│
├─ ProbeScheduler::start()
│    ├─ running.swap(true)
│    └─ DECISION: already running?
│         ├─ YES → return immediately → END
│         └─ NO  → clone manager + running flag
│
├─ tokio::spawn(async move { ... })
│    ├─ ticker = interval(10 seconds)
│    └─ WHILE running == true
│         ├─ ticker.tick().await
│         ├─ tracing::debug!("Probe scheduler tick")
│         └─ next iteration
│
├─ IMPORTANT CURRENT SOURCE LIMIT
│    ├─ comments describe intended Half-Open channel discovery
│    ├─ comments describe intended adaptor probe send
│    └─ those operations are NOT implemented inside the current scheduler loop
│
├─ Stop path
│    └─ ProbeScheduler::stop() → running = false
│
▼
END / NEXT TICK
```

## 输入示例

> 后台任务通常没有 HTTP 请求体；这里把触发事件、队列/定时器和共享状态视为它的输入。

```text
trigger=Long-running Jobs
job=Health Probe Scheduler
runtime=running
shared_state=available
# 该类页面的“输入”不是 HTTP body，而是启动事件、定时器、队列消息或请求侧异步事件。
```

## 返回结果示例

> 后台任务通常不会直接向 HTTP 调用方返回 JSON；这里用一条构造的状态/日志结果表示一次成功执行后的可观测结果。

```text
job=Health Probe Scheduler
status=success
```



## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/router/src/health_probe.rs` | `health_probe` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页来自运行时代码中的真实 background/thread 入口。
