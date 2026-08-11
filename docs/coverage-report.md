---
title: "Coverage / Entry Point Census"
slug: /coverage-report
---

# BurnCloud Entry Point Census

> 源码基线：`burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`。本页由 CI 直接扫描源码生成，不以人工枚举数量作为完整性证明。

## 汇总

| 项目 | 数量 |
|---|---:|
| `http_route_declarations` | 63 |
| `http_unique_entries` | 49 |
| `http_documented_exact_matches` | 47 |
| `http_missing_exact_matches` | 2 |
| `dioxus_route_attributes` | 40 |
| `binary_source_entries` | 9 |
| `spawn_sites` | 37 |

## 源码存在但 Atlas 未精确匹配的 HTTP Route

| Entry | Source |
|---|---|
| `POST /console/api/auth/change-password` | `crates/server/src/api/auth.rs:95` |
| `POST /console/api/auth/logout` | `crates/server/src/api/auth.rs:94` |

## Atlas 已记录但不是直接 `.route()` 精确声明的 HTTP Entry

> 这里通常包含 Router fallback、兼容别名、LiveView 组合路由、特殊动态路径或人工语义页；需要人工确认，不直接判定为错误。

- `GET /`
- `GET /console`
- `GET /console/`
- `GET /console/internal/health`
- `GET /console/internal/metrics`
- `GET /console/{*path}`
- `GET /forgot-password`
- `GET /home`
- `GET /login`
- `GET /preview/console`
- `GET /preview/console/`
- `GET /preview/console/{*path}`
- `GET /preview/home`
- `GET /preview/login`
- `GET /register`
- `GET /reset-password`
- `GET /v1/videos/{task_id}`
- `GET /ws`
- `POST /chat/completions`
- `POST /console/internal/circuit-breaker/trip-all`
- `POST /console/internal/prices/sync`
- `POST /v1/chat/completions`
- `POST /v1/completions`
- `POST /v1/embeddings`
- `POST /v1/messages`
- `POST /v1/models/{model}{countTokens}`
- `POST /v1/models/{model}{embedContent}`
- `POST /v1/models/{model}{generateContent}`
- `POST /v1/models/{model}{streamGenerateContent}`
- `POST /v1/video/generations`
- `POST /v1beta/models/{model}{countTokens}`
- `POST /v1beta/models/{model}{embedContent}`
- `POST /v1beta/models/{model}{generateContent}`
- `POST /v1beta/models/{model}{streamGenerateContent}`

## Dioxus Route Attributes

| Route | Source |
|---|---|
| `/` | `crates/client/src/app.rs:36` |
| `/home` | `crates/client/src/app.rs:39` |
| `/login` | `crates/client/src/app.rs:41` |
| `/register` | `crates/client/src/app.rs:43` |
| `/forgot-password` | `crates/client/src/app.rs:45` |
| `/reset-password?:token` | `crates/client/src/app.rs:47` |
| `/preview/home` | `crates/client/src/app.rs:51` |
| `/preview/login` | `crates/client/src/app.rs:54` |
| `/preview/console/dashboard` | `crates/client/src/app.rs:57` |
| `/preview/console/models` | `crates/client/src/app.rs:60` |
| `/preview/console/access` | `crates/client/src/app.rs:63` |
| `/preview/console/settings` | `crates/client/src/app.rs:66` |
| `/preview/console/finance` | `crates/client/src/app.rs:69` |
| `/preview/console/monitor` | `crates/client/src/app.rs:72` |
| `/preview/console/playground` | `crates/client/src/app.rs:75` |
| `/console/dashboard` | `crates/client/src/app.rs:78` |
| `/console/deploy` | `crates/client/src/app.rs:80` |
| `/console/monitor` | `crates/client/src/app.rs:82` |
| `/console/access` | `crates/client/src/app.rs:84` |
| `/console/models` | `crates/client/src/app.rs:86` |
| `/console/users` | `crates/client/src/app.rs:88` |
| `/console/settings` | `crates/client/src/app.rs:90` |
| `/console/finance` | `crates/client/src/app.rs:92` |
| `/console/logs` | `crates/client/src/app.rs:94` |
| `/console/connect` | `crates/client/src/app.rs:96` |
| `/console/playground` | `crates/client/src/app.rs:98` |
| `/console/:..segments` | `crates/client/src/app.rs:100` |
| `/` | `crates/client/src/bin/screenshot_gen.rs:7` |
| `/console/dashboard` | `crates/client/crates/client-shared/src/components/layout.rs:18` |
| `/console/deploy` | `crates/client/crates/client-shared/src/components/layout.rs:20` |
| `/console/monitor` | `crates/client/crates/client-shared/src/components/layout.rs:22` |
| `/console/access` | `crates/client/crates/client-shared/src/components/layout.rs:24` |
| `/console/models` | `crates/client/crates/client-shared/src/components/layout.rs:26` |
| `/console/users` | `crates/client/crates/client-shared/src/components/layout.rs:28` |
| `/console/settings` | `crates/client/crates/client-shared/src/components/layout.rs:30` |
| `/console/finance` | `crates/client/crates/client-shared/src/components/layout.rs:32` |
| `/console/logs` | `crates/client/crates/client-shared/src/components/layout.rs:34` |
| `/console/connect` | `crates/client/crates/client-shared/src/components/layout.rs:36` |
| `/console/playground` | `crates/client/crates/client-shared/src/components/layout.rs:38` |
| `/console/:..segments` | `crates/client/crates/client-shared/src/components/layout.rs:40` |

## Binary / main.rs Candidates

| Kind | Source |
|---|---|
| `crate-main` | `crates/client/crates/client-api/src/main.rs` |
| `crate-main` | `crates/client/crates/client-shared/src/main.rs` |
| `crate-main` | `crates/client/crates/client-tray/src/main.rs` |
| `bin-source` | `crates/client/src/bin/screenshot_gen.rs` |
| `crate-main` | `crates/client/src/main.rs` |
| `crate-main` | `crates/download/crates/download-aria2/src/main.rs` |
| `crate-main` | `crates/download/src/main.rs` |
| `crate-main` | `crates/loops/src/main.rs` |
| `package-main` | `src/main.rs` |

## Async Spawn Sites

共扫描到 **37** 个 `spawn` 站点。它们用于核对 Background Jobs / request-time async side effects 是否漏页。

| Source | Line |
|---|---:|
| `src/main.rs` | 31 |
| `crates/router/tests/adaptor_tests.rs` | 106 |
| `crates/router/tests/auth_tests.rs` | 123 |
| `crates/router/tests/auth_tests.rs` | 196 |
| `crates/router/tests/common.rs` | 352 |
| `crates/router/tests/failover_tests.rs` | 25 |
| `crates/router/tests/balancer_tests.rs` | 27 |
| `crates/router/src/lib.rs` | 786 |
| `crates/router/src/lib.rs` | 838 |
| `crates/router/src/lib.rs` | 882 |
| `crates/router/src/lib.rs` | 899 |
| `crates/router/src/lib.rs` | 1402 |
| `crates/router/src/lib.rs` | 1421 |
| `crates/router/src/lib.rs` | 1746 |
| `crates/router/src/lib.rs` | 1955 |
| `crates/router/src/lib.rs` | 4013 |
| `crates/router/src/health_probe.rs` | 272 |
| `crates/router/src/exchange_rate.rs` | 182 |
| `crates/router/src/price_sync.rs` | 727 |
| `crates/tests/tests/api/ability_routing.rs` | 26 |
| `crates/download/src/lib.rs` | 140 |
| `crates/download/crates/download-aria2/src/lib.rs` | 616 |
| `crates/server/tests/gateway_tests.rs` | 17 |
| `crates/server/tests/group_routing_tests.rs` | 52 |
| `crates/server/tests/group_routing_tests.rs` | 60 |
| `crates/server/tests/log_api_tests.rs` | 79 |
| `crates/server/tests/api_tests.rs` | 21 |
| `crates/server/tests/api_tests.rs` | 45 |
| `crates/server/tests/api_tests.rs` | 77 |
| `crates/server/tests/api_tests.rs` | 101 |
| `crates/server/tests/api_tests.rs` | 125 |
| `crates/service/crates/monitor/src/service.rs` | 89 |
| `crates/database/tests/performance_tests.rs` | 62 |
| `crates/database/tests/error_handling_tests.rs` | 115 |
| `crates/database/tests/error_handling_tests.rs` | 204 |
| `crates/database/tests/cross_platform_tests.rs` | 185 |
| `crates/client/src/app.rs` | 168 |
