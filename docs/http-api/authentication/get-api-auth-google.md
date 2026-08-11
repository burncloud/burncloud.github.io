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
├─ 发起者
│    └─ User / SDK / Browser / Operator
│
├─ 入口
│    └─ GET /api/auth/google
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
├─ create_app() → api::routes()
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ DECISION: public auth route?
│    ├─ YES → bypass JWT middleware
│    └─ NO  → protected router
│
▼
FILE: crates/server/src/api/auth.rs
│
├─ Route match → oauth_google()
├─ Parse Query / JSON input if required
├─ Execute UserService / OAuth logic
├─ DECISION: service call successful?
│    ├─ NO  → err(...) response
│    └─ YES → ok(...) response
│
└─ HTTP response returned

▼
END
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
