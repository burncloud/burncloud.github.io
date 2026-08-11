---
title: "POST /console/internal/prices/sync"
slug: /http-api/admin-internal/post-console-internal-prices-sync
hide_table_of_contents: true
---

# POST /console/internal/prices/sync

**树路径：** `BurnCloud → HTTP / API → Admin / Internal → POST /console/internal/prices/sync`

&gt; **中文解释：** 通过 force_sync_tx 触发价格同步任务，并最多等待 60 秒 oneshot 回应。
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
│    └─ POST /console/internal/prices/sync
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
├─ create_app() merges internal_app before LiveView
│
▼
FILE: crates/router/src/lib.rs
│
├─ explicit internal route → price_sync_handler()
├─ IMPORTANT: current internal_app itself has no JWT middleware
├─ Execute internal runtime operation
├─ DECISION: operation succeeds?
│    ├─ NO  → route-specific 5xx/timeout response
│    └─ YES → JSON response
│
▼
END
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/server/src/lib.rs` |
| 2 | `crates/router/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
