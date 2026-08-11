---
title: "System Monitor Auto Update"
slug: /background/long-running-jobs/system-monitor-auto-update
hide_table_of_contents: true
---

# System Monitor Auto Update

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Long-running Jobs → System Monitor Auto Update`

&gt; **中文解释：** create_app() 启动 start_auto_update；周期采集 CPU、内存、磁盘并刷新内存缓存。
&gt;
&gt; **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Trigger
│    └─ Server/Router/Manager startup or request-side spawn
│
▼
FILE: crates/server/src/lib.rs
│
├─ Register / spawn background work
├─ 执行：create_app() 启动 start_auto_update；周期采集 CPU、内存、磁盘并刷新内存缓存。
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


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/service/crates/monitor/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
