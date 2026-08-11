---
title: "Exchange Rate Sync"
slug: /background/long-running-jobs/exchange-rate-sync
hide_table_of_contents: true
---

# Exchange Rate Sync

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Long-running Jobs → Exchange Rate Sync`

> **中文解释：** 周期检查汇率是否过期，刷新/重载数据库中的 exchange rates。
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
├─ 执行：周期检查汇率是否过期，刷新/重载数据库中的 exchange rates。
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
2026-08-11T14:45:12+08:00 exchange_rate_sync currencies=8 stale=false status=success
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/router/src/lib.rs` |
| 2 | `crates/service/crates/billing/src/exchange_rate.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
