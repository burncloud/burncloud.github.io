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
├─ [PHASE 00] 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /v1/videos/{task_id}
│    ├─ Input sources
│    │    ├─ Method + URI path
│    │    ├─ Query string（如有）
│    │    ├─ HTTP headers
│    │    └─ Request body（如有）
│    └─ DECISION: TCP/HTTP 请求能否到达 BurnCloud listener?
│         ├─ NO  → 网络层失败；应用代码未执行 → END
│         └─ YES → 进入 Axum
│
▼
FILE: crates/server/src/lib.rs
│
├─ [PHASE 01] 统一 HTTP Server
│    ├─ start_server() 已在进程启动时完成
│    │    ├─ database 初始化
│    │    ├─ RouterDatabase::init()
│    │    ├─ UserDatabase::init()
│    │    ├─ create_app(...)
│    │    ├─ TcpListener::bind(...)
│    │    └─ axum::serve(listener, app)
│    ├─ 当前请求进入 Unified Axum App
│    └─ 全局 middleware
│         ├─ CORS
│         ├─ TraceLayer
│         ├─ SetRequestIdLayer
│         └─ PropagateRequestIdLayer
│
├─ [PHASE 02] 顶层 Route 决策
│    └─ DECISION: Unified App 是否已有显式/合并路由命中当前 Method + Path?
│         ├─ YES（其它 route）→ corresponding handler
│         └─ NO → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 03] proxy_handler entry
│    ├─ normalize path
│    ├─ extract supported credential
│    ├─ validate token/user
│    ├─ quota guard
│    └─ local rate limiter
│
├─ [PHASE 04] Video polling special-case detection
│    └─ DECISION: Method == GET AND Path starts with /v1/videos/ ?
│         ├─ NO  → normal inference proxy_logic
│         └─ YES → polling branch
│
├─ [PHASE 05] Task identity
│    ├─ task_id = URL suffix
│    └─ DECISION: task_id non-empty/valid enough for lookup?
│         ├─ NO  → client/not-found error → END
│         └─ YES → DB lookup
│
▼
FILE: crates/database/crates/router/src/video_task.rs
│
├─ [PHASE 06] Read persisted task mapping
│    ├─ RouterVideoTaskModel::get_by_task_id(task_id)
│    └─ DECISION: mapping exists?
│         ├─ NO  → HTTP 404 task_not_found → END
│         └─ YES → channel_id + stored task metadata
│
▼
FILE: crates/database/crates/channel/src/lib.rs
│
├─ [PHASE 07] Load original Channel
│    ├─ ChannelProviderModel::get_by_id(channel_id)
│    └─ DECISION: Channel record available/configured?
│         ├─ NO  → HTTP 502 → END
│         └─ YES → base_url + credential
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 08] Direct upstream polling request
│    ├─ construct {base_url}/v1/videos/{task_id}
│    ├─ apply original Channel authentication
│    ├─ IMPORTANT: no new scheduler/model selection
│    └─ send GET through shared HTTP client
│
├─ [PHASE 09] Upstream polling result
│    └─ DECISION: network/upstream request succeeds?
│         ├─ NO  → HTTP 502 → END
│         └─ YES
│              ├─ preserve upstream status
│              ├─ collect upstream body
│              └─ return polling response
│
├─ [PHASE 10] Side effects
│    ├─ task mapping is read-only in this request
│    ├─ no fresh task mapping created
│    └─ no model scheduler selection
│
▼
END
     └─ Client receives current video task state
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /v1/videos/video_task_bc_01JXYZ HTTP/1.1
Host: api.burncloud.example
Authorization: Bearer bc_live_7d4e...example
Accept: application/json
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "video_task_bc_01JXYZ",
  "object": "video.generation",
  "status": "completed",
  "model": "video-model-pro",
  "output": [
    {
      "url": "https://example.invalid/videos/video_task_bc_01JXYZ.mp4"
    }
  ],
  "duration": 5,
  "resolution": "1080p"
}
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/router/src/lib.rs` |
| 3 | `crates/database/crates/router/src/video_task.rs` |
| 4 | `crates/database/crates/channel/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
