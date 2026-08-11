---
title: "Token accessed_time update"
slug: /background/request-time-async-side-effects/token-accessed_time-update
hide_table_of_contents: true
---

# Token accessed_time update

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Request-time Async Side Effects → Token accessed_time update`

> **中文解释：** Token 鉴权成功后 tokio::spawn 异步更新 accessed_time；失败不阻断主请求。
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
├─ 执行：Token 鉴权成功后 tokio::spawn 异步更新 accessed_time；失败不阻断主请求。
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
token=bc_live_7d4e...example accessed_time=2026-08-11T14:45:16+08:00 update=success
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/router/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
