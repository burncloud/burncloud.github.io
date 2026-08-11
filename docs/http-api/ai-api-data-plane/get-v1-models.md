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
├─ 发起者
│    └─ User / SDK / Browser / Operator
│
├─ 入口
│    └─ GET /v1/models
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
├─ DECISION: 顶层 Unified App 命中 /v1/models ?
│    └─ NO → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ DECISION: 显式 Data Plane route == GET /v1/models ?
│    ├─ YES → models_handler()
│    └─ NO  → proxy_handler fallback
│
├─ models_handler()
│    ├─ model_entries = []
│    ├─ current_time = UNIX seconds
│    └─ CALL ChannelAbilityModel::list_distinct_models(&state.db)
│
▼
FILE: crates/database/crates/channel/src/channel_ability.rs
│
├─ db.get_connection()
├─ DECISION: DB connection OK?
│    ├─ NO  → Err
│    └─ YES → SQL
│
├─ SELECT DISTINCT model
│    FROM channel_abilities
│    WHERE enabled = 1
│    ORDER BY model
│
├─ DECISION: SQL OK?
│    ├─ NO  → Err
│    └─ YES → Ok(Vec<String>)
│
▼
FILE: crates/router/src/lib.rs
│
├─ DECISION: list_distinct_models returned Ok?
│    ├─ NO  → error 被 if let Ok(...) 吞掉；data=[]
│    └─ YES → FOR EACH model
│         └─ build {id, object, created, owned_by, permission, root, parent}
│
├─ serialize response_json
├─ DECISION: serialization OK?
│    ├─ YES → normal JSON
│    └─ NO  → {"object":"list","data":[]}
│
└─ HTTP 200 application/json

▼
END
     └─ User / SDK receives models list
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

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/router/src/lib.rs` |
| 3 | `crates/database/crates/channel/src/channel_ability.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
