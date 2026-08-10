---
title: "Billing & Logging"
slug: /api-requests/chat-completion/billing-settlement/
type: runtime-flow
flow_id: user.api.chat.billing
truth: STATIC_CONFIRMED
parent_flow: user.api.chat
entry_points:
  - "proxy_logic returns to proxy_handler"
---

# Billing & Logging

← [Chat Completion](/api-requests/chat-completion/)

## What happens here?

`proxy_logic()` 返回后，`proxy_handler()` 从共享 `UnifiedTokenCounter` 读取 usage；Veo/Seedance 在 provider 没有 usage 时还会用请求字段补 video tokens。若 usage 非空且 model 已知，调用 `CostCalculator::calculate()`；随后写 RouterLog / optional request log，最后仅当 `cost > 0` 时异步执行 quota 扣减。

## ICFG

```mermaid
flowchart TD
    E["proxy_logic() 返回 ProxyResult"]
    U["token_counter.get_usage()"]
    VID["必要时注入 Veo / Seedance video_tokens"]
    HAS{"usage 非空?"}
    MOD{"model_name 已知?"}
    CALC["CostCalculator::calculate(model, usage, flags, pricing_region)"]
    CRES{"calculate result"}
    COK["得到 cost + CostBreakdown"]
    MISS["PriceNotFound / calc_error → cost=0 + status"]
    ZERO["usage empty / no model / upstream error → cost=0 状态"]
    LOG["构建 RouterLog + tracing::info"]
    SEND["log_tx.send(log).await"]
    DETAIL{"request_log_data 存在?"}
    RLOG["try_send RouterRequestLog"]
    POS{"cost > 0?"}
    DED["tokio::spawn deduct_quota(user,token,cost)"]
    HDR["注入 X-Channel-Id / X-Model-Id"]
    OUT["Return response"]
    E --> U --> VID --> HAS
    HAS -->|No| ZERO --> LOG
    HAS -->|Yes| MOD
    MOD -->|No| ZERO
    MOD -->|Yes| CALC --> CRES
    CRES -->|Ok| COK --> LOG
    CRES -->|Err| MISS --> LOG
    LOG --> SEND --> DETAIL
    DETAIL -->|Yes| RLOG --> POS
    DETAIL -->|No| POS
    POS -->|Yes| DED --> HDR
    POS -->|No| HDR
    HDR --> OUT
    click CALC "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1778" "Open cost calculation" _blank
    click DED "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1948" "Open quota deduction scheduling" _blank
```

## State / Side Effects

- **Persistent log write:** background log consumer writes RouterLog.
- **Optional detailed request log:** async channel / try_send.
- **Quota mutation:** asynchronous only when `cost > 0`.
- **Metrics/counters:** missing-price and billing counters can mutate.

## Source Evidence

- Usage and cost: [`crates/router/src/lib.rs:L1754-L1816`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1754-L1816)
- Log construction/enqueue: [`crates/router/src/lib.rs:L1823-L1946`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1823-L1946)
- Quota deduction + response headers: [`crates/router/src/lib.rs:L1948-L1982`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1948-L1982)

**Confidence: HIGH — STATIC CONFIRMED**
