---
title: "GET /console/api/monitor/security/events"
slug: /http-api/monitoring-security/get-console-api-monitor-security-events
hide_table_of_contents: true
---

# GET /console/api/monitor/security/events

**树路径：** `BurnCloud → HTTP / API → Monitoring / Security → GET /console/api/monitor/security/events`

> **中文解释：** 从 router_logs 过滤 status &gt;= 400，转换成 RiskEvent 后再分页。 核心调用：RouterLogService::get。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /console/api/monitor/security/events
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
FILE: crates/server/src/api/security.rs
│
├─ Handler
│    └─ security_events()
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
└─ RouterLogService::get(...) → RouterLogModel::get(...)
│
▼
FILE: crates/database/crates/router/src/log.rs
│
└─ read router_logs
│
▼
FILE: crates/server/src/api/security.rs
│
├─ summary: compute_security_score() + compute_sparkline()
└─ events: filter status >= 400 → log_to_risk_event() → paginate
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
│    ├─ FILE: crates/server/src/api/security.rs
│    │    ├─ security_events()
│    │    │    └─ CALL → RouterLogService::get() @ crates/service/crates/router-log/src/lib.rs
│    │    │    └─ CALL → err() @ crates/server/src/api/response.rs
│    │    ├─ compute_security_score()
│    │    ├─ compute_sparkline()
│    │    ├─ log_to_risk_event()
│    ├─ FILE: crates/service/crates/router-log/src/lib.rs
│    │    ├─ RouterLogService::get()
│    └─ FILE: crates/server/src/api/response.rs
│    │    ├─ err()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /console/api/monitor/security/events HTTP/1.1
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
  "data": [
    {
      "id": "risk_50123",
      "type": "upstream_error",
      "severity": "medium",
      "status": 502,
      "source": "203.0.113.20",
      "created_at": "2026-08-11T14:42:31+08:00"
    }
  ],
  "total": 1
}
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | Public/Protected Management route composition | ROUTE composition |
| 3 | `crates/server/src/api/auth.rs` | `auth_middleware(), verify_jwt(), public_routes()` | JWT middleware 与 public authentication routes | READ Authorization / Claims |
| 4 | `crates/server/src/api/security.rs` | `security_events(), log_to_risk_event()` | RouterLog error rows → RiskEvent | READ logs |
| 5 | `crates/service/crates/router-log/src/lib.rs` | `RouterLogService::*, BillingService::*` | Router log / usage / billing summary service | SERVICE |
| 6 | `crates/database/crates/router/src/log.rs` | `RouterLogModel::* / usage & billing queries` | Request accounting / usage / billing persistence | READ/WRITE router_logs |
| 7 | `crates/server/src/api/response.rs` | `err()` | 由 security_events() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
