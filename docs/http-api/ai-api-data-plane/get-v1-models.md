---
title: "GET /v1/models"
slug: /http-api/ai-api-data-plane/get-v1-models
hide_table_of_contents: true
---

# GET /v1/models

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → GET /v1/models`

> 本页只保留一张总的**文本流程图**。从请求发起开始，一直穿透到 HTTP Response 返回，包含经过的文件、函数、Route 判断、数据库判断、异常分支和最终业务结果。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## 完整 End-to-End Request Flow + ICFG

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ START                                                                        │
│ 用户 / OpenAI SDK / curl / AI Client                                        │
└──────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP
                                      ▼
                         GET /v1/models
                                      │
                                      ▼
════════════════════════════════════════════════════════════════════════════════
① HTTP SERVER
文件：crates/server/src/lib.rs
════════════════════════════════════════════════════════════════════════════════
                                      │
                                      ▼
                            start_server()
                                      │
                    ┌─────────────────┴─────────────────┐
                    │ Server 启动阶段已完成：           │
                    │ Database::new                     │
                    │ RouterDatabase::init              │
                    │ UserDatabase::init                │
                    │ create_app()                      │
                    │ TcpListener::bind                 │
                    │ axum::serve                       │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                            Unified Axum App
                                      │
                                      ▼
                    ┌───────────────────────────────────┐
                    │ Global Middleware                 │
                    │                                   │
                    │ CORS                              │
                    │ TraceLayer                        │
                    │ SetRequestIdLayer                 │
                    │ PropagateRequestIdLayer           │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                  ┌─────────────────────────────────────┐
                  │ 判断 A：Unified App 是否已有        │
                  │ 更高优先级 Route 命中？             │
                  │                                     │
                  │ - /health                           │
                  │ - Management API                    │
                  │ - Router Internal API               │
                  │ - LiveView                          │
                  └──────────────┬──────────────────────┘
                                 │
                  ┌──────────────┴──────────────┐
                  │ YES                         │ NO
                  ▼                             ▼
        进入其它 Handler                GET /v1/models 没有命中
        与本页无关                     上述顶层 Route
                                                │
                                                ▼
                                  fallback_service(router_app)
                                                │
                                                ▼
════════════════════════════════════════════════════════════════════════════════
② DATA PLANE ROUTER
文件：crates/router/src/lib.rs
════════════════════════════════════════════════════════════════════════════════
                                                │
                                                ▼
                                      router_app
                         （由 create_router_app() 构建）
                                                │
                                                ▼
                 ┌────────────────────────────────────────────┐
                 │ 判断 B：显式 Data Plane Route 是否匹配？   │
                 │                                            │
                 │ Method = GET                               │
                 │ Path   = /v1/models                        │
                 └───────────────┬────────────────────────────┘
                                 │
                   ┌─────────────┼─────────────────────┐
                   │ YES         │ 其它显式 Route      │ NO
                   ▼             ▼                     ▼
          models_handler()   usage_handler 等      proxy_handler
                   │
                   │
                   │ 关键逻辑：因为已经命中显式 GET /v1/models
                   │ 所以这条请求不会进入 proxy_handler
                   │
                   ├──────────────────────────────────────────────────────────┐
                   │                                                          │
                   │ 本 Endpoint 当前也没有以下步骤：                         │
                   │                                                          │
                   │ ✕ Authorization Header 读取                              │
                   │ ✕ API Token Validation                                   │
                   │ ✕ JWT Validation                                         │
                   │ ✕ User / Group 解析                                      │
                   │ ✕ Quota Check                                            │
                   │ ✕ Local Rate Limiter                                     │
                   │ ✕ ModelRouter                                             │
                   │ ✕ Scheduler / Affinity                                    │
                   │ ✕ Rate Budget / Shaper                                   │
                   │ ✕ Circuit Breaker                                         │
                   │ ✕ Billing Preflight                                       │
                   │ ✕ Provider Adaptor                                        │
                   │ ✕ Upstream AI Provider                                    │
                   │                                                          │
                   └──────────────────────────────────────────────────────────┘
                   │
                   ▼
════════════════════════════════════════════════════════════════════════════════
③ MODELS HANDLER — 前半段
文件：crates/router/src/lib.rs
函数：models_handler(State<AppState>)
════════════════════════════════════════════════════════════════════════════════
                   │
                   ▼
          model_entries = []
                   │
                   ▼
          SystemTime::now()
                   │
                   ▼
          duration_since(UNIX_EPOCH)
                   │
                   ▼
       ┌────────────────────────────┐
       │ 判断 C：系统时间转换成功？ │
       └────────────┬───────────────┘
                    │
          ┌─────────┴─────────┐
          │ YES               │ NO
          ▼                   ▼
 current_time = seconds   unwrap_or_default()
                              │
                              ▼
                       current_time = 0
          │                   │
          └─────────┬─────────┘
                    │
                    ▼
 ChannelAbilityModel::list_distinct_models(&state.db)
                    │
                    ▼
════════════════════════════════════════════════════════════════════════════════
④ DATABASE QUERY
文件：crates/database/crates/channel/src/channel_ability.rs
函数：ChannelAbilityModel::list_distinct_models()
════════════════════════════════════════════════════════════════════════════════
                    │
                    ▼
            db.get_connection()
                    │
                    ▼
       ┌───────────────────────────┐
       │ 判断 D：获取 DB 连接成功？│
       └────────────┬──────────────┘
                    │
          ┌─────────┴─────────┐
          │ YES               │ NO
          ▼                   ▼
      conn.pool()          返回 Err
          │                   │
          ▼                   │
 ┌──────────────────────────────────────────────────────────────────────────┐
 │ SQL                                                                      │
 │                                                                          │
 │ SELECT DISTINCT model                                                   │
 │ FROM channel_abilities                                                  │
 │ WHERE enabled = 1                                                       │
 │ ORDER BY model;                                                         │
 └───────────────────────────┬──────────────────────────────────────────────┘
                             │
                             ▼
                  sqlx::query_as(sql)
                             │
                             ▼
                  fetch_all(conn.pool())
                             │
                             ▼
                  ┌───────────────────────┐
                  │ 判断 E：SQL 查询成功？│
                  └──────────┬────────────┘
                             │
                   ┌─────────┴─────────┐
                   │ YES               │ NO
                   ▼                   ▼
           Vec<(String,)>           返回 Err
                   │                   │
                   ▼                   │
          map tuple → model            │
                   │                   │
                   ▼                   │
          Ok(Vec<String>)              │
                   │                   │
                   └─────────┬─────────┘
                             │
                             ▼
════════════════════════════════════════════════════════════════════════════════
⑤ MODELS HANDLER — 返回数据逻辑
文件：crates/router/src/lib.rs
════════════════════════════════════════════════════════════════════════════════
                             │
                             ▼
              ┌───────────────────────────────┐
              │ 判断 F：list_distinct_models │
              │ 是否返回 Ok？                │
              └──────────────┬────────────────┘
                             │
                   ┌─────────┴─────────┐
                   │ YES               │ NO / Err
                   ▼                   ▼
            得到 models           DB 错误被
                   │              if let Ok(...)
                   │              直接吞掉
                   │                   │
                   │                   ▼
                   │            model_entries = []
                   │                   │
                   ▼                   │
        ┌─────────────────────┐        │
        │ 判断 G：models 为空？│        │
        └──────────┬──────────┘        │
                   │                   │
          ┌────────┴────────┐          │
          │ YES             │ NO       │
          ▼                 ▼          │
 model_entries = []      for model     │
                            │           │
                            ▼           │
                 构造每个 Model JSON   │
                            │           │
                 ┌──────────┴──────────┐│
                 │ id         = model  ││
                 │ object     = model  ││
                 │ created    = 当前请求时间
                 │ owned_by   = burncloud
                 │ permission = []     ││
                 │ root       = model  ││
                 │ parent     = null   ││
                 └──────────┬──────────┘│
                            │           │
                            ▼           │
                 push(model_entries)    │
                            │           │
                            ▼           │
                 ┌───────────────────┐  │
                 │ 判断 H：还有 model？│  │
                 └─────────┬─────────┘  │
                           │            │
                    YES ───┘            │
                           │ NO         │
                           ▼            │
                   循环结束             │
                           │            │
          ┌────────────────┴────────────┘
          │
          ▼
构造 response_json

{
  "object": "list",
  "data": model_entries
}
          │
          ▼
serde_json::to_string(response_json)
          │
          ▼
┌────────────────────────────┐
│ 判断 I：JSON 序列化成功？   │
└────────────┬───────────────┘
             │
      ┌──────┴──────┐
      │ YES         │ NO
      ▼             ▼
正常 JSON Body   fallback Body
                {"object":"list","data":[]}
      │             │
      └──────┬──────┘
             │
             ▼
════════════════════════════════════════════════════════════════════════════════
⑥ HTTP RESPONSE BUILDER
文件：crates/router/src/lib.rs
函数：build_response_with_header()
════════════════════════════════════════════════════════════════════════════════
             │
             ▼
 build_response_with_header(
     StatusCode::OK,
     "content-type",
     "application/json",
     Body::from(json)
 )
             │
             ▼
 Response::builder()
    .status(200)
    .header(content-type, application/json)
    .body(body)
             │
             ▼
┌──────────────────────────────┐
│ 判断 J：Response 构造成功？   │
└─────────────┬────────────────┘
              │
       ┌──────┴───────────┐
       │ YES              │ NO
       ▼                  ▼
HTTP 200              再构造一次
JSON Body             status(200)
       │              empty body
       │                  │
       │                  ▼
       │        ┌──────────────────────┐
       │        │ 判断 K：第二次成功？ │
       │        └──────────┬───────────┘
       │                   │
       │            ┌──────┴──────┐
       │            │ YES         │ NO
       │            ▼             ▼
       │        HTTP 200      Response::new(
       │        empty body    Body::empty()
       │            │             │
       └────────────┴──────┬──────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ END                                                                          │
│ HTTP Response 返回 用户 / SDK                                               │
└──────────────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ 最终业务语义                                                                 │
│                                                                              │
│ 返回 channel_abilities 中：                                                 │
│                                                                              │
│     enabled = 1                                                             │
│                                                                              │
│ 的 DISTINCT model，并按 model 排序。                                         │
│                                                                              │
│ 当前 SQL 没有判断：                                                          │
│                                                                              │
│ - 当前用户是谁                                                               │
│ - 用户属于哪个 group                                                         │
│ - channel_providers.status                                                   │
│ - Channel Health                                                             │
│ - Circuit Breaker                                                            │
│ - RPM / TPM Capacity                                                         │
│ - Quota                                                                      │
│ - Price / Price Cap                                                          │
│                                                                              │
│ 因此：                                                                       │
│                                                                              │
│ enabled ability 存在                                                         │
│     ≠ 当前用户一定可用                                                       │
│     ≠ Provider 当前一定健康                                                  │
│     ≠ 此刻一定可以成功路由                                                   │
│                                                                              │
│ 另外：                                                                       │
│ DB 连接失败 / SQL 查询失败 / 真正没有模型                                    │
│ 当前都可能最终表现为：                                                       │
│                                                                              │
│ HTTP 200                                                                     │
│ { "object": "list", "data": [] }                                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

## 穿过的源码文件

| 顺序 | 文件 | 关键函数 / 逻辑 |
|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server()` → `create_app()` → `fallback_service(router_app)` |
| 2 | `crates/router/src/lib.rs` | `create_router_app()` → `GET /v1/models` → `models_handler()` → `build_response_with_header()` |
| 3 | `crates/database/crates/channel/src/channel_ability.rs` | `ChannelAbilityModel::list_distinct_models()` → `channel_abilities` SQL |

**Execution classification: STATIC CONFIRMED** — 上图中的执行路径、判断、SQL 和文件位置均由当前 BurnCloud 源码直接确认。
