---
title: "GET /v1/videos/{task_id}"
slug: /http-api/ai-api-data-plane/get-v1-videos-task_id
hide_table_of_contents: true
---

# GET /v1/videos/&#123;task_id&#125;

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → GET /v1/videos/{task_id}`

> **中文解释：** 先鉴权，再从 task_id 查原始 channel_id；按该 Channel 的 base_url/key 直接轮询上游，不重新走模型调度。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 发起者
│    └─ User / SDK / Browser / Operator
│
├─ 入口
│    └─ GET /v1/videos/{task_id}
│
▼
FILE: crates/server/src/lib.rs
│
├─ axum::serve(listener, app)
├─ 全局 Middleware
│    ├─ CORS
│    ├─ TraceLayer
│    └─ x-request-id
│
├─ fallback_service(router_app) → proxy_handler()
├─ credential validation / quota / rate limit
├─ DECISION: method == GET and path starts /v1/videos/?
│    ├─ NO  → normal proxy_logic
│    └─ YES → special polling branch
│
├─ task_id = path suffix
├─ RouterVideoTaskModel::get_by_task_id(task_id)
├─ DECISION: mapping exists?
│    ├─ NO  → HTTP 404 task_not_found
│    └─ YES → channel_id
├─ ChannelProviderModel::get_by_id(channel_id)
├─ DECISION: Channel available?
│    ├─ NO  → HTTP 502
│    └─ YES → build upstream /v1/videos/{task_id}
├─ GET upstream with Channel key
├─ DECISION: upstream request OK?
│    ├─ NO  → HTTP 502
│    └─ YES → pass status/body back
│
▼
END
     └─ polling response returned to client
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/router/src/lib.rs` |
| 3 | `crates/database/crates/router/src/video_task.rs` |
| 4 | `crates/database/crates/channel/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
