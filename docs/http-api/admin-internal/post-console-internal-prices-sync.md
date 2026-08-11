---
title: "POST /console/internal/prices/sync"
slug: /http-api/admin-internal/post-console-internal-prices-sync
hide_table_of_contents: true
---

# POST /console/internal/prices/sync

**树路径：** `BurnCloud → HTTP / API → Admin / Internal → POST /console/internal/prices/sync`

> **中文解释：** 通过 force_sync_tx 触发价格同步任务，并最多等待 60 秒 oneshot 回应。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: POST /console/internal/prices/sync
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
│         ├─ YES → merged Router Internal route
│         └─ NO  → continue to other routes/fallback
│
▼
FILE: crates/router/src/lib.rs
│
├─ Internal route match
│    └─ price_sync_handler()
│
├─ Authentication boundary
│    ├─ Router internal_app itself is not wrapped by Management JWT middleware
│    └─ network exposure therefore depends on server deployment/binding/firewall
│
├─ Runtime-state operation
│    ├─ read/mutate in-memory Router runtime services
│    ├─ force-sync route sends channel message and awaits oneshot/timeout
│    └─ DECISION: required runtime service/channel available?
│         ├─ NO  → route-specific 5xx/timeout/error response
│         └─ YES → perform operation
│
├─ Route-specific state
│    ├─ health: scheduler/circuit/channel/rate-budget snapshot
│    ├─ price sync: force_sync_tx + oneshot result
│    ├─ trip-all: circuit_breaker.trip_all()
│    └─ metrics: Router runtime counters
│
├─ Serialize result
│    └─ DECISION: operation/result successful?
│         ├─ NO  → error HTTP response
│         └─ YES → JSON success response
│
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: crates/router/src/lib.rs
│    │    ├─ price_sync_handler()
│    │    │    └─ CALL → build_response_with_header() @ crates/router/src/lib.rs
│    │    ├─ build_response_with_header()
│    │    │    └─ CALL → PriceCache::empty() @ crates/service/crates/billing/src/cache.rs
│    └─ FILE: crates/service/crates/billing/src/cache.rs
│    │    ├─ PriceCache::empty()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
POST /console/internal/prices/sync HTTP/1.1
Host: api.burncloud.example
Accept: application/json
Content-Type: application/json

{"reason":"manual maintenance"}
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "updated_models": 46,
  "duration_ms": 842
}
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/router/src/lib.rs` | `create_router_app(), proxy_handler(), proxy_logic()` | Data Plane 主控制流或 Router internal handler | READ/WRITE router runtime |
| 3 | `crates/router/src/price_sync.rs` | `price_sync` | Router runtime subsystem used by E2E path | READ/WRITE runtime state |
| 4 | `crates/service/crates/billing/src/cache.rs` | `PriceCache::empty()` | 由 build_response_with_header() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
