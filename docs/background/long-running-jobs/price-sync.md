---
title: "Price Sync"
slug: /background/long-running-jobs/price-sync
hide_table_of_contents: true
---

# Price Sync

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Long-running Jobs → Price Sync`

> **中文解释：** Router 启动 price sync task；启动快路径读取现有价格，随后周期同步，也接受 force-sync channel。
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
├─ 执行：Router 启动 price sync task；启动快路径读取现有价格，随后周期同步，也接受 force-sync channel。
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
2026-08-11T14:45:11+08:00 price_sync updated_models=46 duration_ms=842 status=success
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/router/src/lib.rs` |
| 2 | `crates/router/src/price_sync.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
