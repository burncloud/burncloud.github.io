---
title: "POST /api/auth/register"
slug: /http-api/authentication/post-api-auth-register
hide_table_of_contents: true
---

# POST /api/auth/register

**树路径：** `BurnCloud → HTTP / API → Authentication → POST /api/auth/register`

&gt; **中文解释：** 注册用户；用户名冲突返回错误，注册成功后生成 JWT。 核心调用：register_user → get_user_roles → generate_token。
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
│    └─ POST /api/auth/register
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
├─ Route match → create_user()
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


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/server/src/api/mod.rs` |
| 3 | `crates/server/src/api/auth.rs` |
| 4 | `crates/service/crates/user/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
