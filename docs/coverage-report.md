---
title: "Coverage / Entry Point Census"
slug: /coverage-report
---

# BurnCloud Entry Point Census

> 源码基线：`burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`。本页由 CI 从真实源码扫描生成；HTTP、主 Dioxus 路由、Binary 的缺失数量必须为 0 才允许发布。

## 汇总

| 项目 | 数量 |
|---|---:|
| `http_route_declarations` | 61 |
| `http_unique_entries` | 47 |
| `http_documented_exact_matches` | 47 |
| `http_missing_exact_matches` | 0 |
| `main_dioxus_unique_routes` | 27 |
| `ui_documented_exact_matches` | 27 |
| `ui_missing_exact_matches` | 0 |
| `binary_source_entries` | 9 |
| `binary_documented_source_matches` | 9 |
| `binary_missing_source_matches` | 0 |
| `runtime_spawn_sites` | 17 |

## HTTP Coverage

**Missing = 0。** 扫描到的直接 Axum Method + Path 声明均有 Atlas 覆盖。

### Atlas 中的 fallback / 组合 / 语义 HTTP Entry

> 下列项目不一定对应直接 `.route()`；常见于 router fallback、LiveView 组合路由、动态路径或兼容入口，因此单列人工审计。

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
- `POST /v1/models/{model}:countTokens`
- `POST /v1/models/{model}:embedContent`
- `POST /v1/models/{model}:generateContent`
- `POST /v1/models/{model}:streamGenerateContent`
- `POST /v1/video/generations`
- `POST /v1beta/models/{model}:countTokens`
- `POST /v1beta/models/{model}:embedContent`
- `POST /v1beta/models/{model}:generateContent`
- `POST /v1beta/models/{model}:streamGenerateContent`

## Main Dioxus UI Coverage

**Missing = 0。** `crates/client/src/app.rs` 的主 Route 集合均有 UI-only Atlas 页面。

## Binary Coverage

| Binary | Source | Coverage |
|---|---|---|
| `burncloud-client-api` | `crates/client/crates/client-api/src/main.rs` | COVERED |
| `burncloud-client-shared` | `crates/client/crates/client-shared/src/main.rs` | COVERED |
| `burncloud-client-tray` | `crates/client/crates/client-tray/src/main.rs` | COVERED |
| `screenshot_gen` | `crates/client/src/bin/screenshot_gen.rs` | COVERED |
| `burncloud-client` | `crates/client/src/main.rs` | COVERED |
| `aria2-test` | `crates/download/crates/download-aria2/src/main.rs` | COVERED |
| `burncloud-download` | `crates/download/src/main.rs` | COVERED |
| `burncloud-loop` | `crates/loops/src/main.rs` | COVERED |
| `burncloud` | `src/main.rs` | COVERED |

## Runtime Async Spawn Sites

排除 tests/examples/benches 后，共扫描到 **17** 个运行时代码 `spawn` 站点。它们作为 Background / async side-effect 人工覆盖审计清单。

| Source | Line | Kind |
|---|---:|---|
| `src/main.rs` | 31 | `std::thread::spawn` |
| `crates/router/src/health_probe.rs` | 272 | `tokio::spawn` |
| `crates/router/src/lib.rs` | 786 | `tokio::spawn` |
| `crates/router/src/lib.rs` | 838 | `tokio::spawn` |
| `crates/router/src/lib.rs` | 882 | `tokio::spawn` |
| `crates/router/src/lib.rs` | 899 | `tokio::spawn` |
| `crates/router/src/lib.rs` | 1402 | `tokio::spawn` |
| `crates/router/src/lib.rs` | 1421 | `tokio::spawn` |
| `crates/router/src/lib.rs` | 1746 | `tokio::spawn` |
| `crates/router/src/lib.rs` | 1955 | `tokio::spawn` |
| `crates/router/src/lib.rs` | 4013 | `tokio::spawn` |
| `crates/router/src/exchange_rate.rs` | 182 | `tokio::spawn` |
| `crates/router/src/price_sync.rs` | 727 | `tokio::spawn` |
| `crates/client/src/app.rs` | 168 | `std::thread::spawn` |
| `crates/download/src/lib.rs` | 140 | `tokio::spawn` |
| `crates/download/crates/download-aria2/src/lib.rs` | 616 | `tokio::spawn` |
| `crates/service/crates/monitor/src/service.rs` | 89 | `tokio::spawn` |

## 全部主 Dioxus Route 源码位置

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

## Runtime Spawn → Background Page Coverage

扫描到的 runtime spawn 共 **17** 个；已映射 **17**，未映射 **0**。

| Source | Line | Background Atlas Page |
|---|---:|---|
| `src/main.rs` | 31 | `background/desktop-background-work/windows-background-server-thread` |
| `crates/router/src/health_probe.rs` | 272 | `background/long-running-jobs/health-probe-scheduler` |
| `crates/router/src/lib.rs` | 786 | `background/long-running-jobs/exchange-rate-sync` |
| `crates/router/src/lib.rs` | 838 | `background/long-running-jobs/aimd-budget-feedback` |
| `crates/router/src/lib.rs` | 882 | `background/long-running-jobs/async-router-log-writer` |
| `crates/router/src/lib.rs` | 899 | `background/long-running-jobs/async-request-log-writer` |
| `crates/router/src/lib.rs` | 1402 | `background/request-time-async-side-effects/token-accessed_time-update` |
| `crates/router/src/lib.rs` | 1421 | `background/request-time-async-side-effects/token-accessed_time-update` |
| `crates/router/src/lib.rs` | 1746 | `background/request-time-async-side-effects/video-task-mapping-save` |
| `crates/router/src/lib.rs` | 1955 | `background/request-time-async-side-effects/quota-deduction` |
| `crates/router/src/lib.rs` | 4013 | `background/request-time-async-side-effects/api-version-detect-update` |
| `crates/router/src/exchange_rate.rs` | 182 | `background/long-running-jobs/exchange-rate-sync` |
| `crates/router/src/price_sync.rs` | 727 | `background/long-running-jobs/price-sync` |
| `crates/client/src/app.rs` | 168 | `background/desktop-background-work/windows-tray-thread` |
| `crates/download/src/lib.rs` | 140 | `background/download-background-work/download-progress-monitor` |
| `crates/download/crates/download-aria2/src/lib.rs` | 616 | `background/download-background-work/aria2-daemon-monitor` |
| `crates/service/crates/monitor/src/service.rs` | 89 | `background/long-running-jobs/system-monitor-auto-update` |
