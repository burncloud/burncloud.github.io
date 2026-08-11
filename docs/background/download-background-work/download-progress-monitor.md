---
title: "Download progress monitor"
slug: /background/download-background-work/download-progress-monitor
hide_table_of_contents: true
---

# Download progress monitor

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Download Background Work → Download progress monitor`

> **中文解释：** 定期读取 aria2 状态并把进度写入数据库，直到 complete/error/client unavailable。
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
FILE: crates/download/src/lib.rs
│
├─ Register / spawn background work
├─ 执行：定期读取 aria2 状态并把进度写入数据库，直到 complete/error/client unavailable。
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
gid=2089b05ecca3d829 progress=64.8% speed=42.1MB/s status=active
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/download/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
