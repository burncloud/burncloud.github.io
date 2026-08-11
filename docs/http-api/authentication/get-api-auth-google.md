---
title: "GET /api/auth/google"
slug: /http-api/authentication/get-api-auth-google
hide_table_of_contents: true
---

# GET /api/auth/google

**树路径：** `BurnCloud → HTTP / API → Authentication → GET /api/auth/google`

> **中文解释：** 生成 Google OAuth URL；当前只返回 URL，不在此 Handler 完成回调。 核心调用：UserService::oauth_url("google")。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ [PHASE 00] 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /api/auth/google
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
│         ├─ YES → matched top-level/public route path
│         └─ NO  → other route composition
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ [PHASE 03] Management API composition
│    ├─ public auth routes are mounted outside protected JWT layer
│    └─ DECISION: current path matches public Authentication route?
│         ├─ NO  → protected router / other API
│         └─ YES → no pre-handler JWT requirement
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ [PHASE 04] Handler entry
│    └─ oauth_google()
│
├─ [PHASE 05] Input extraction
│    ├─ Axum Query/Json extractor parses request fields
│    └─ DECISION: syntactic extraction succeeds?
│         ├─ NO  → Axum/client error response → END
│         └─ YES → handler validation
│
├─ [PHASE 06] Business validation
│    ├─ validate required username/email/password/token/provider inputs as applicable
│    └─ DECISION: required business input acceptable?
│         ├─ NO  → err(...) response → END
│         └─ YES → service call
│
▼
FILE: crates/service/crates/user/src/lib.rs
│
├─ [PHASE 07] UserService / OAuth operation
│    └─ CALL oauth_url("google")
│
├─ [PHASE 08] Persistence / identity branch
│    ├─ register/login/reset paths may read/write user state
│    ├─ OAuth URL path is read/config construction only
│    └─ DECISION: service operation succeeds?
│         ├─ NO  → map service error → API error response
│         └─ YES → service result
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ [PHASE 09] Security-sensitive response shaping
│    ├─ login/register success may include JWT + user roles
│    ├─ forgot-password intentionally avoids revealing account existence
│    └─ OAuth endpoints return authorization URL rather than callback completion
│
├─ [PHASE 10] Serialize / return
│    └─ ok(...) / err(...) → HTTP JSON response
│
▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /api/auth/google HTTP/1.1
Host: api.burncloud.example
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
    "url": "https://accounts.google.com/o/oauth2/v2/auth?..."
  }
}
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/server/src/api/mod.rs` |
| 3 | `crates/server/src/api/auth.rs` |
| 4 | `crates/service/crates/user/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
