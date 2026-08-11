---
title: "Video task mapping save"
slug: /background/request-time-async-side-effects/video-task-mapping-save
hide_table_of_contents: true
---

# Video task mapping save

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Request-time Async Side Effects → Video task mapping save`

> **中文解释：** 视频生成返回 task_id 后异步保存 task_id → channel_id/user/model/duration/resolution。
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
├─ 执行：视频生成返回 task_id 后异步保存 task_id → channel_id/user/model/duration/resolution。
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
task_id=video_task_bc_01JXYZ channel_id=12 user_id=10001 mapping_saved=true
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/router/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
