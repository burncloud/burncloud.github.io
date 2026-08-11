---
title: "GET /v1/models"
slug: /http-api/ai-api-data-plane/get-v1-models
hide_table_of_contents: true
---

# GET /v1/models

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → GET /v1/models`

> **中文解释：** 读取 channel_abilities 中 enabled = 1 的 DISTINCT model；不进入 proxy_handler，也不做用户鉴权、调度或 Provider 调用。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /v1/models
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
│         ├─ YES（其它顶层 route）→ 进入对应 handler；本页路径结束
│         └─ NO（/v1/models）→ fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ Data Plane route match
│    ├─ create_router_app() 已注册显式 GET /v1/models
│    └─ DECISION: Method == GET AND Path == /v1/models ?
│         ├─ NO  → 其它显式 usage route 或 proxy_handler fallback
│         └─ YES → models_handler(State<AppState>)
│
├─ Authentication / authorization boundary
│    ├─ 当前 handler 不读取 Authorization
│    ├─ 不调用 Token/JWT validation
│    ├─ 不解析 user_id / group
│    └─ 因此没有当前用户维度的模型可见性过滤
│
├─ Handler local state
│    ├─ model_entries = []
│    ├─ SystemTime::now()
│    ├─ duration_since(UNIX_EPOCH)
│    └─ DECISION: system time conversion OK?
│         ├─ YES → current_time = duration.as_secs()
│         └─ NO  → unwrap_or_default() → current_time = 0
│
├─ CALL → ChannelAbilityModel::list_distinct_models(&state.db)
│
▼
FILE: crates/database/crates/channel/src/channel_ability.rs
│
├─ Database connection
│    ├─ db.get_connection()
│    └─ DECISION: connection acquired?
│         ├─ NO  → return Err → 回到 handler
│         └─ YES → conn.pool()
│
├─ SQL / state read
│    ├─ SELECT DISTINCT model
│    ├─ FROM channel_abilities
│    ├─ WHERE enabled = 1
│    └─ ORDER BY model
│
├─ sqlx::query_as(sql).fetch_all(pool).await
│    └─ DECISION: SQL success?
│         ├─ NO  → return Err
│         └─ YES → Vec<(String,)> → map → Ok(Vec<String>)
│
├─ Visibility semantics
│    ├─ INCLUDE only ability.enabled = 1
│    ├─ DISTINCT by model
│    ├─ NO user/group filter
│    ├─ NO channel_providers.status join
│    ├─ NO health/circuit/capacity check
│    └─ NO quota/price/billing check
│
▼
FILE: crates/router/src/lib.rs
│
├─ Handler branch merge
│    └─ DECISION: list_distinct_models returned Ok?
│         ├─ NO / Err
│         │    ├─ if let Ok(...) body skipped
│         │    └─ model_entries stays []
│         └─ YES
│              └─ FOR EACH model
│                   ├─ id = model
│                   ├─ object = "model"
│                   ├─ created = current_time
│                   ├─ owned_by = "burncloud"
│                   ├─ permission = []
│                   ├─ root = model
│                   ├─ parent = null
│                   └─ push → model_entries
│
├─ Serialization
│    ├─ response_json = {object:"list", data:model_entries}
│    ├─ serde_json::to_string(...)
│    └─ DECISION: serialization success?
│         ├─ YES → normal JSON body
│         └─ NO  → literal fallback {"object":"list","data":[]}
│
├─ HTTP response construction
│    ├─ build_response_with_header(StatusCode::OK, content-type, application/json, body)
│    ├─ Response::builder().status(200).header(...).body(...)
│    └─ DECISION: response builder success?
│         ├─ YES → HTTP 200 + JSON body
│         └─ NO  → retry status 200 + empty body
│              └─ DECISION: retry success?
│                   ├─ YES → HTTP 200 + empty body
│                   └─ NO  → Response::new(Body::empty())
│
├─ Explicitly NOT executed
│    ├─ proxy_handler
│    ├─ Token/JWT auth
│    ├─ Quota / rate limiter
│    ├─ ModelRouter / Scheduler
│    ├─ Circuit Breaker
│    ├─ Billing
│    └─ Provider / upstream
│
▼
END
     └─ Client receives model-list response
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /v1/models HTTP/1.1
Host: api.burncloud.example
Accept: application/json
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "object": "list",
  "data": [
    {
      "id": "gpt-5.4",
      "object": "model",
      "created": 1786380000,
      "owned_by": "burncloud",
      "permission": [],
      "root": "gpt-5.4",
      "parent": null
    },
    {
      "id": "claude-sonnet-4-5",
      "object": "model",
      "created": 1786380000,
      "owned_by": "burncloud",
      "permission": [],
      "root": "claude-sonnet-4-5",
      "parent": null
    }
  ]
}
```



## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 Server、Router 合并、Middleware、fallback 入口 | READ runtime composition |
| 2 | `crates/router/src/lib.rs` | `见上方 E2E 对应函数` | 该页面现有静态调用链中的源码文件 | READ/WRITE depends on entry |
| 3 | `crates/database/crates/channel/src/channel_ability.rs` | `见上方 E2E 对应函数` | 该页面现有静态调用链中的源码文件 | READ/WRITE depends on entry |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
