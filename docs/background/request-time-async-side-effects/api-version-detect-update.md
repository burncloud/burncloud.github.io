---
title: "API version detect / update"
slug: /background/request-time-async-side-effects/api-version-detect-update
hide_table_of_contents: true
---

# API version detect / update

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Request-time Async Side Effects → API version detect / update`

> **中文解释：** 部分上游失败触发 API version 探测/更新，为后续请求提供版本信息。
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
├─ 执行：部分上游失败触发 API version 探测/更新，为后续请求提供版本信息。
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
channel_id=12 detected_api_version=v1 version_cache_updated=true
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/router/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
