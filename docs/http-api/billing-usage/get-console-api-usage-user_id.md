---
title: "GET /console/api/usage/{user_id}"
slug: /http-api/billing-usage/get-console-api-usage-user_id
hide_table_of_contents: true
---

# GET /console/api/usage/&#123;user_id&#125;

**树路径：** `BurnCloud → HTTP / API → Billing / Usage → GET /console/api/usage/{user_id}`

> **中文解释：** 复用 Logs 的用户用量查询：按 URL user_id 汇总 tokens。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /console/api/usage/{user_id}
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
├─ 统一 HTTP Server
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
├─ 顶层 Route 决策
│    └─ DECISION: Unified App 是否已有显式/合并路由命中当前 Method + Path?
│         ├─ YES → Management API / protected route candidate
│         └─ NO  → other top-level/fallback route
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ protected_routes composition
│    ├─ route registered under Management API
│    └─ auth_middleware() wraps protected router
│
├─ JWT authentication
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
FILE: crates/server/src/api/log.rs
│
├─ Handler
│    └─ get_user_usage()
│
├─ Request extraction
│    ├─ Path params / Query params / JSON body as required by Method
│    ├─ authenticated Claims available from extensions
│    └─ DECISION: extraction/required fields valid?
│         ├─ NO  → client/error response → END
│         └─ YES → authorization/business checks
│
├─ Authorization + invariants
│    ├─ Route uses authenticated Claims/user context as implemented
│    ├─ validate ID/status/range/reason/etc. according to handler
│    └─ DECISION: authorization/invariants pass?
│         ├─ NO  → 4xx/error payload → END
│         └─ YES → service/database call
│
├─ Service / Database boundary
│    ├─ operation type: read/query state
│    ├─ invoke route-specific Service / Database method
│    └─ DECISION: operation succeeds?
│         ├─ NO  → map error → HTTP error response
│         └─ YES → domain result
│
├─ State effects
│    ├─ READ routes: no intended mutation beyond incidental telemetry
│    ├─ WRITE routes: persist create/update/delete/config action
│    └─ route-specific async/internal calls execute before/around result when implemented
│
▼
FILE: crates/service/crates/router-log/src/lib.rs
│
└─ RouterLogService::get_usage_by_user(db, user_id)
│
▼
FILE: crates/database/crates/router/src/log.rs
│
├─ SUM prompt_tokens / completion_tokens for user_id
└─ return tuple → handler calculates total_tokens
│
├─ Response mapping
│    ├─ domain model → DTO/JSON
│    ├─ pagination/summary fields where applicable
│    └─ serialize success payload
│
├─ HTTP exit
│    └─ return success or mapped error status/body
│
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: crates/server/src/api/log.rs
│    │    ├─ get_user_usage()
│    │    │    └─ CALL → RouterLogService::get_usage_by_user() @ crates/service/crates/router-log/src/lib.rs
│    └─ FILE: crates/service/crates/router-log/src/lib.rs
│    │    ├─ RouterLogService::get_usage_by_user()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /console/api/usage/10001 HTTP/1.1
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
  "user_id": 10001,
  "prompt_tokens": 18420560,
  "completion_tokens": 6912840,
  "total_tokens": 25333400
}
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | Public/Protected Management route composition | ROUTE composition |
| 3 | `crates/server/src/api/log.rs` | `get_user_usage()` | 按 Path user_id 汇总 token usage | READ path/logs |
| 4 | `crates/service/crates/router-log/src/lib.rs` | `RouterLogService::*, BillingService::*` | Router log / usage / billing summary service | SERVICE |
| 5 | `crates/database/crates/router/src/log.rs` | `RouterLogModel::* / usage & billing queries` | Request accounting / usage / billing persistence | READ/WRITE router_logs |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
