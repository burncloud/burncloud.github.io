---
title: "Router fallback → proxy_handler"
slug: /http-api/ai-api-data-plane/router-fallback-proxy_handler
hide_table_of_contents: true
---

# Router fallback → proxy_handler

**树路径：** `BurnCloud → HTTP / API → AI API / Data Plane → Router fallback → proxy_handler`

&gt; **中文解释：** Unified Server 将未命中的数据面请求交给 router_app；router_app 未命中显式 route 后进入 proxy_handler。
&gt;
&gt; **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 发起者
│    └─ User / SDK / Browser / Operator
│
├─ 入口
│    └─ 任意未被显式 Router 捕获的数据面路径
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
├─ 顶层未命中 → fallback_service(router_app)
│
▼
FILE: crates/router/src/lib.rs
│
├─ router_app 未命中显式 models / usage route
│    └─ proxy_handler()
│
├─ normalize_doubled_path()
├─ Credential Source
│    ├─ Authorization: Bearer ...
│    ├─ x-api-key
│    └─ x-goog-api-key
│
├─ DECISION: credential exists?
│    ├─ NO  → HTTP 401
│    └─ YES → RouterDatabase validate
│
├─ DECISION: token valid?
│    ├─ YES → user_id / group / quota / order_type / price_cap
│    └─ NO
│         ├─ legacy token validation
│         └─ JWT fallback
│
├─ DECISION: quota exhausted?
│    ├─ YES → HTTP 402
│    └─ NO  → continue
│
├─ DECISION: local rate limiter allows?
│    ├─ NO  → HTTP 429
│    └─ YES → collect request body
│
├─ Extract request context
│    ├─ model from JSON body or Gemini URL
│    ├─ batch / priority flags
│    └─ video duration/resolution when applicable
│
├─ proxy_logic(...)
│    ├─ load scheduler policy for user group
│    ├─ resolve model / candidate channels
│    ├─ filter availability / order constraints
│    ├─ billing preflight
│    └─ candidate attempt loop
│         ├─ rate budget / shaper
│         ├─ circuit breaker
│         ├─ protocol decision
│         └─ upstream request
│
▼
FILE: crates/router/src/passthrough.rs + Dynamic Adaptor Boundary
│
├─ DECISION: native passthrough supported?
│    ├─ YES → preserve OpenAI / Anthropic / Gemini native protocol
│    └─ NO  → adaptor conversion path（DYNAMIC by Provider）
│
├─ Send HTTP request to selected upstream
├─ DECISION: upstream attempt succeeds?
│    ├─ NO  → record failure → next candidate / final error
│    └─ YES → response / stream handling
│
▼
FILE: crates/router/src/lib.rs
│
├─ collect UnifiedUsage
├─ video token injection when applicable
├─ CostCalculator::calculate()
├─ enqueue RouterLog / RequestLog
├─ async quota deduction when cost > 0
├─ attach resolved channel/model headers
└─ return upstream-compatible HTTP response

▼
END
     └─ User / SDK receives response
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/router/src/lib.rs` |
| 3 | `crates/router/src/passthrough.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
