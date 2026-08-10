---
title: "Force Price Sync"
slug: /operator/price-sync/
type: runtime-flow
flow_id: user.operator.price
truth: STATIC_CONFIRMED
parent_flow: user.operator
entry_points:
  - "POST /console/internal/prices/sync"
  - "price_sync_handler"
---

# Force Price Sync

← [Internal Operator Actions](/#/operator/)

## What happens here?

handler 创建 oneshot reply channel，把 sender 发送到 background price-sync task 的 `force_sync_tx`，然后最多等待配置的 timeout。background task 未运行时立即 503；超时 / channel closed 也有独立失败响应。

## ICFG

```mermaid
flowchart TD
    E["POST /console/internal/prices/sync<br/>price_sync_handler()"] --> O["oneshot::channel()"]
    S["force_sync_tx.send(reply_tx).await"]
    SENT{"send success?"}
    E503["503 Price sync task is not running"]
    W["tokio::time::timeout(..., reply_rx)"]
    R{"wait result"}
    OK["Return sync result JSON"]
    ERR["Return timeout / task error response"]
    E --> O --> S --> SENT
    SENT -->|No| E503
    SENT -->|Yes| W --> R
    R -->|success| OK
    R -->|timeout/error| ERR
    click E "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L968" "Open handler" _blank
```

## State / Side Effects

- Async message to price-sync background task.
- Actual external price synchronization happens in that task; this handler is only the trigger/wait boundary.

## Source Evidence

- [`crates/router/src/lib.rs:L968-L1015`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L968-L1015)

**Confidence: HIGH for trigger/wait flow.**
