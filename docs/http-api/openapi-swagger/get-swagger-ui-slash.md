---
title: "GET /swagger-ui/"
slug: /http-api/openapi-swagger/get-swagger-ui-slash
hide_table_of_contents: true
---

# GET /swagger-ui/

**树路径：** `BurnCloud → HTTP / API → OpenAPI / Swagger → GET /swagger-ui/`

> **中文解释：** 与 /swagger-ui 使用同一个 Handler。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ 调用方与输入边界
│    ├─ Actor: User / SDK / Browser / Operator
│    ├─ Entry: GET /swagger-ui/
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
│         ├─ YES → api::routes()
│         └─ NO → other route
│
▼
FILE: crates/server/src/api/mod.rs
│
├─ OpenAPI routes are currently inside protected_routes
│    ├─ auth_middleware()
│    └─ DECISION: JWT valid?
│         ├─ NO → HTTP 401 → END
│         └─ YES → route handler
│
▼
FILE: crates/server/src/api/openapi.rs
│
├─ Handler
│    └─ swagger_ui()
│
├─ Content construction
│    └─ DECISION: endpoint type?
│         ├─ /api-docs/openapi.json
│         │    ├─ construct OpenAPI 3.0.3 object
│         │    ├─ include documented paths/schemas
│         │    └─ serialize JSON
│         └─ /swagger-ui[/]
│              ├─ construct embedded Swagger HTML shell
│              └─ browser later loads Swagger UI assets
│
├─ Response
│    ├─ JSON endpoint → application/json
│    └─ UI endpoint → text/html
│
│
├─ 源码函数展开（静态扫描确认）
│    └─ FILE: crates/server/src/api/openapi.rs
│    │    ├─ swagger_ui()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> 以下为构造的典型请求输入，用于对应上面的入口、鉴权、参数解析和分支；Host、Token、ID、模型及业务字段均为示例。

```http
GET /swagger-ui/ HTTP/1.1
Host: api.burncloud.example
Authorization: Bearer eyJhbGciOi...admin-jwt
Accept: application/json,text/html
```

## 返回结果示例

> 以下为构造的成功结果示例，用于快速理解该入口最终会向调用方、终端或运行时呈现什么；动态 ID、时间、模型、金额、Provider 与统计值以实际运行结果为准。

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<!doctype html>
<html>
  <head><title>BurnCloud Swagger UI</title></head>
  <body><div id="swagger-ui"></div></body>
</html>
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/server/src/lib.rs` | `start_server(), create_app()` | 统一 HTTP Server / App composition / fallback | INIT + request routing |
| 2 | `crates/server/src/api/mod.rs` | `routes()` | Public/Protected Management route composition | ROUTE composition |
| 3 | `crates/server/src/api/auth.rs` | `auth_middleware(), verify_jwt(), public_routes()` | JWT middleware 与 public authentication routes | READ Authorization / Claims |
| 4 | `crates/server/src/api/openapi.rs` | `swagger_ui()` | 返回 Swagger UI HTML shell | RESPONSE HTML |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
