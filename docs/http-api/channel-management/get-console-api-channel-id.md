---
title: "GET /console/api/channel/{id}"
slug: /http-api/channel-management/get-console-api-channel-id
hide_table_of_contents: true
---

# GET /console/api/channel/&#123;id&#125;

**树路径：** `BurnCloud → HTTP / API → Channel Management → GET /console/api/channel/{id}`

> **中文解释：** 管理员按 ID 查询；不存在时返回 channel not found。 核心调用：ChannelService::get_by_id。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ [PHASE 00] 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /console/api/channel/{id}
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
│         ├─ YES → Management API / protected route candidate
│         └─ NO  → other top-level/fallback route
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ [PHASE 03] protected_routes composition
│    ├─ route registered under Management API
│    └─ auth_middleware() wraps protected router
│
├─ [PHASE 04] JWT authentication
│    ├─ read Authorization header
│    └─ DECISION: Authorization starts with Bearer?
│         ├─ NO  → HTTP 401 → END
│         └─ YES → verify_jwt(...)
│
├─ DECISION: JWT signature/claims valid?
│    ├─ NO  → HTTP 401 → END
│    └─ YES
│         ├─ Claims inserted into request extensions
│         └─ continue to route handler
│
▼
FILE: crates/server/src/api/channel.rs
│
├─ [PHASE 05] Handler
│    └─ get_channel()
│
├─ [PHASE 06] Request extraction
│    ├─ Path params / Query params / JSON body as required by Method
│    ├─ authenticated Claims available from extensions
│    └─ DECISION: extraction/required fields valid?
│         ├─ NO  → client/error response → END
│         └─ YES → authorization/business checks
│
├─ [PHASE 07] Authorization + invariants
│    ├─ Admin role required for Channel Management
│    ├─ validate ID/status/range/reason/etc. according to handler
│    └─ DECISION: authorization/invariants pass?
│         ├─ NO  → 4xx/error payload → END
│         └─ YES → service/database call
│
├─ [PHASE 08] Service / Database boundary
│    ├─ operation type: read/query state
│    ├─ invoke route-specific Service / Database method
│    └─ DECISION: operation succeeds?
│         ├─ NO  → map error → HTTP error response
│         └─ YES → domain result
│
├─ [PHASE 09] State effects
│    ├─ READ routes: no intended mutation beyond incidental telemetry
│    ├─ WRITE routes: persist create/update/delete/config action
│    └─ route-specific async/internal calls execute before/around result when implemented
│
├─ [PHASE 10] Response mapping
│    ├─ domain model → DTO/JSON
│    ├─ pagination/summary fields where applicable
│    └─ serialize success payload
│
├─ [PHASE 11] HTTP exit
│    └─ return success or mapped error status/body
│
▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /console/api/channel/12 HTTP/1.1
Host: api.burncloud.example
Authorization: Bearer eyJhbGciOi...admin-jwt
Accept: application/json
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "id": 12,
    "name": "openai-primary",
    "channel_type": "openai",
    "base_url": "https://api.openai.com",
    "status": 1,
    "priority": 100,
    "weight": 100
  }
}
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/server/src/api/mod.rs` |
| 3 | `crates/server/src/api/auth.rs` |
| 4 | `crates/server/src/api/channel.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
