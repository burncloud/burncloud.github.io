---
title: "Async Router Log Writer"
slug: /background/long-running-jobs/async-router-log-writer
hide_table_of_contents: true
---

# Async Router Log Writer

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Long-running Jobs → Async Router Log Writer`

> **中文解释：** 后台消费 RouterLog 队列并持久化，避免主请求同步阻塞。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Trigger
│    └─ Server/Router/Manager startup or request-side spawn
│
▼
FILE: crates/router/src/lib.rs
│
├─ Register / spawn background work
├─ 执行：后台消费 RouterLog 队列并持久化，避免主请求同步阻塞。
├─ DECISION: should continue?
│    ├─ YES → sleep / await event / receive message → next iteration
│    └─ NO  → stop task
├─ DECISION: iteration failed?
│    ├─ YES → log / fail-open according to task semantics
│    └─ NO  → update state / persistence
│
▼
END / NEXT ITERATION
```


## 返回结果示例

> 后台任务通常不会直接向 HTTP 调用方返回 JSON；这里用一条构造的状态/日志结果表示一次成功执行后的可观测结果。

```text
2026-08-11T14:45:14+08:00 router_log_writer persisted=64 queue_remaining=0 status=ok
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/router/src/lib.rs` |
| 2 | `crates/service/crates/router-log/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
