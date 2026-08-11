---
title: "create_router_app"
slug: /startup/create_router_app
hide_table_of_contents: true
---

# create_router_app

**树路径：** `BurnCloud → Startup → Startup Chain → create_router_app`

> **中文解释：** 构建 HTTP client、limiter、circuit breaker、ModelRouter、scheduler、PriceCache、CostCalculator、rate budget、后台 writer/task，再注册显式路由和 proxy fallback。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Process startup
│    └─ create_router_app
│
▼
FILE: crates/router/src/lib.rs
│
├─ 构建 HTTP client、limiter、circuit breaker、ModelRouter、scheduler、PriceCache、CostCalculator、rate budget、后台 writer/task，再注册显式路由和 proxy fallback。
├─ DECISION: initialization step fails?
│    ├─ YES → propagate error / process startup fails
│    └─ NO  → continue next initialization stage
│
├─ Runtime objects / routes / tasks become available
│
▼
END
     └─ server/client/runtime enters steady state
```


## 返回结果示例

> Startup 页面没有传统 API response；这里用构造的启动结果/运行态日志表示该阶段成功完成后系统应进入的状态。

```text
http_client=ready
model_router=ready
circuit_breaker=ready
price_cache=ready
exchange_rates=ready
background_writers=running
router=ready
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/router/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
