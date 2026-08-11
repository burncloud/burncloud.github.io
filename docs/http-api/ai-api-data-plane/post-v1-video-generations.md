---
title: "POST /v1/video/generations"
slug: /http-api/ai-api-data-plane/post-v1-video-generations
hide_table_of_contents: true
---

# POST /v1/video/generations

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → POST /v1/video/generations`

> **中文解释：** 视频生成；除通用代理链外，还提取 duration/resolution，并在成功后保存 task_id → channel_id 映射。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ [PHASE 00] 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: POST /v1/video/generations
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
│         ├─ YES（Management/Internal/LiveView 等）→ 对应 handler
│         └─ NO → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 03] Data Plane route selection
│    ├─ explicit /v1/models or usage routes checked first
│    └─ DECISION: explicit route matched?
│         ├─ YES → corresponding explicit handler
│         └─ NO  → proxy_handler()
│
├─ [PHASE 04] Path normalization + request identity
│    ├─ normalize_doubled_path()
│    ├─ preserve Method / URI / headers
│    ├─ request-id already attached by server middleware
│    └─ prepare AppState/runtime services
│
├─ [PHASE 05] Credential source selection
│    ├─ Candidate 1: Authorization: Bearer ...
│    ├─ Candidate 2: x-api-key
│    ├─ Candidate 3: x-goog-api-key
│    └─ DECISION: any supported credential exists?
│         ├─ NO  → HTTP 401 → END
│         └─ YES → token validation chain
│
├─ [PHASE 06] Token / user / group resolution
│    ├─ RouterDatabase new-token validation
│    ├─ DECISION: new token valid?
│    │    ├─ YES → token metadata / user_id / group / quota / policy
│    │    └─ NO  → legacy token validation
│    ├─ DECISION: legacy token valid?
│    │    ├─ YES → legacy metadata / user_id
│    │    └─ NO  → JWT fallback where supported
│    └─ DECISION: identity ultimately valid?
│         ├─ NO  → authorization error → END
│         └─ YES → continue
│
├─ [PHASE 07] Account / quota guard
│    ├─ inspect quota/order metadata
│    └─ DECISION: quota exhausted / account cannot spend?
│         ├─ YES → HTTP 402 Payment Required → END
│         └─ NO  → continue
│
├─ [PHASE 08] Local request rate limiting
│    ├─ limiter key derived from authenticated request context
│    └─ DECISION: limiter allows request?
│         ├─ NO  → HTTP 429 Too Many Requests → END
│         └─ YES → continue
│
├─ [PHASE 09] Request-body acquisition
│    ├─ collect Axum body bytes
│    └─ DECISION: body read/size/parse boundary succeeds?
│         ├─ NO  → client/request error → END
│         └─ YES → immutable request payload for routing/adaptor
│
├─ [PHASE 10] Model + protocol context extraction
│    ├─ OpenAI/Anthropic: model usually from JSON body
│    ├─ Gemini: model may come from URL path
│    ├─ detect streaming / batch / priority hints
│    ├─ detect API protocol family
│    ├─ 解析 duration/resolution；成功后异步保存 task_id → channel_id 映射
│    └─ DECISION: required model/context resolved?
│         ├─ NO  → invalid request / model resolution error → END
│         └─ YES → proxy_logic(...)
│
├─ [PHASE 11] Enter proxy_logic(...)
│    ├─ load scheduling policy for resolved user group
│    ├─ resolve requested model / model mapping
│    ├─ load candidate channel abilities
│    ├─ apply user/order/price constraints
│    └─ produce ordered/weighted candidate set
│
├─ [PHASE 12] Candidate eligibility filtering
│    ├─ ability enabled?
│    ├─ channel state allows traffic?
│    ├─ circuit breaker allows attempt?
│    ├─ rate budget / shaper allows attempt?
│    ├─ price/order constraints satisfied?
│    └─ DECISION: any candidate remains?
│         ├─ NO  → no-upstream / routing error → END
│         └─ YES → candidate attempt loop
│
├─ [PHASE 13] Candidate attempt loop
│    ├─ select next candidate
│    ├─ acquire rate budget / shaping permission
│    ├─ consult circuit breaker
│    ├─ resolve protocol / API version
│    ├─ construct upstream URL + headers + credentials
│    └─ hand request to passthrough/adaptor boundary
│
▼
FILE: crates/router/src/passthrough.rs
│
├─ [PHASE 14] Protocol transformation boundary
│    ├─ inspect source protocol + target Channel protocol
│    └─ DECISION: native passthrough possible?
│         ├─ YES
│         │    ├─ preserve compatible body/headers semantics
│         │    └─ avoid unnecessary transform
│         └─ NO
│              └─ DynamicAdaptorFactory / adaptor conversion path
│                   └─ DYNAMIC: exact transformation depends on Provider adaptor
│
├─ [PHASE 15] Upstream network I/O
│    ├─ send HTTP request through shared client
│    ├─ wait for headers/body or stream
│    └─ DECISION: upstream attempt succeeds?
│         ├─ NO
│         │    ├─ classify failure
│         │    ├─ update channel/circuit feedback
│         │    ├─ optional API-version detect/update
│         │    └─ DECISION: another eligible candidate?
│         │         ├─ YES → back to PHASE 13
│         │         └─ NO  → final upstream/routing error → END
│         └─ YES → response handling
│
▼
FILE: crates/router/src/lib.rs
│
├─ [PHASE 16] Response mode split
│    └─ DECISION: streaming response?
│         ├─ YES
│         │    ├─ stream chunks to client
│         │    ├─ collect/derive usage while stream progresses
│         │    └─ handle stream completion/disconnect
│         └─ NO
│              ├─ collect upstream body
│              └─ parse/derive usage metadata
│
├─ [PHASE 17] Unified usage + cost
│    ├─ normalize prompt/input tokens
│    ├─ normalize completion/output tokens
│    ├─ endpoint-specific usage augmentation when needed
│    ├─ PriceCache / CostCalculator lookup
│    └─ CostCalculator::calculate()
│
├─ [PHASE 18] Accounting / persistence side effects
│    ├─ enqueue RouterLog
│    ├─ enqueue RequestLog according to storage policy
│    ├─ send AIMD/rate-budget feedback
│    ├─ update circuit/channel state feedback
│    ├─ async token accessed_time update where applicable
│    └─ DECISION: calculated cost > 0?
│         ├─ YES → async quota deduction
│         └─ NO  → no quota deduction task
│
├─ [PHASE 19] Endpoint-specific async side effects
│    ├─ save video task mapping asynchronously
│
├─ [PHASE 20] Final response construction
│    ├─ preserve/normalize upstream-compatible status + body
│    ├─ attach resolved channel/model diagnostic headers where configured
│    └─ return Axum Response
│
▼
END
     └─ Client receives successful upstream-compatible response OR a terminal error from an earlier branch
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
POST /v1/video/generations HTTP/1.1
Host: api.burncloud.example
Authorization: Bearer bc_live_7d4e...example
Content-Type: application/json

{"model":"video-model-pro","prompt":"夜晚城市航拍","duration":5,"resolution":"1080p"}
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "id": "video_task_bc_01JXYZ",
  "object": "video.generation",
  "status": "queued",
  "model": "video-model-pro",
  "created": 1786380000
}
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/router/src/lib.rs` |
| 3 | `crates/router/src/passthrough.rs` |
| 4 | `crates/database/crates/router/src/lib.rs` |
| 5 | `crates/database/crates/channel/src/lib.rs` |
| 6 | `crates/service/crates/billing/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
