---
title: "GET /console/api/monitor"
slug: /http-api/monitoring-security/get-console-api-monitor
hide_table_of_contents: true
---

# GET /console/api/monitor

**树路径：** `BurnCloud → HTTP / API → Monitoring / Security → GET /console/api/monitor`

> **中文解释：** 读取后台系统监控缓存并返回 CPU/Memory/Disk 等指标。 核心调用：SystemMonitorService::get_metrics。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /console/api/monitor
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
FILE: crates/server/src/api/monitor.rs
│
├─ Handler
│    └─ get_system_metrics()
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
FILE: crates/service/crates/monitor/src/service.rs
│
├─ SystemMonitorService::get_metrics()
├─ DECISION: cached_metrics exists and still fresh?
│    ├─ YES → return cached clone
│    └─ NO  → collect_fresh_metrics()
│         └─ collect_metrics_internal()
│              └─ tokio::join!(CPU, Memory, Disk)
│
▼
FILE: crates/service/crates/monitor/src/collectors/cpu.rs
│
└─ CpuCollector::collect()
│
▼
FILE: crates/service/crates/monitor/src/collectors/memory.rs
│
└─ MemoryCollector::collect()
│
▼
FILE: crates/service/crates/monitor/src/collectors/disk.rs
│
└─ DiskCollector::collect_all()
│
▼
FILE: crates/service/crates/monitor/src/service.rs
│
└─ update cached_metrics → return SystemMetrics
│
├─ Response mapping
│    ├─ domain model → DTO/JSON
│    ├─ pagination/summary fields where applicable
│    └─ serialize success payload
│
├─ HTTP exit
│    └─ return success or mapped error status/body
│
▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /console/api/monitor HTTP/1.1
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
  "cpu_usage": 31.7,
  "memory_usage": 62.4,
  "disk_usage": 48.9,
  "uptime_seconds": 483920
}
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | Public/Protected Management route composition | ROUTE composition |
| 3 | `crates/server/src/api/auth.rs` | `auth_middleware(), verify_jwt(), public_routes()` | JWT middleware 与 public authentication routes | READ Authorization / Claims |
| 4 | `crates/server/src/api/monitor.rs` | `entry-specific function(s) shown in E2E` | 当前入口在该文件执行的直接调用点 | runtime-specific |
| 5 | `crates/service/crates/monitor/src/service.rs` | `SystemMonitorService::*` | metrics cache + collector coordination | READ OS / WRITE memory cache |
| 6 | `crates/service/crates/monitor/src/collectors/cpu.rs` | `Collector::collect*()` | OS metric collector | READ operating-system metrics |
| 7 | `crates/service/crates/monitor/src/collectors/memory.rs` | `Collector::collect*()` | OS metric collector | READ operating-system metrics |
| 8 | `crates/service/crates/monitor/src/collectors/disk.rs` | `Collector::collect*()` | OS metric collector | READ operating-system metrics |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
