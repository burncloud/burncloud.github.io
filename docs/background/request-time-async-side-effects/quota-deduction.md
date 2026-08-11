---
title: "Quota deduction"
slug: /background/request-time-async-side-effects/quota-deduction
hide_table_of_contents: true
---

# Quota deduction

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Request-time Async Side Effects → Quota deduction`

> **中文解释：** 请求完成并计算 cost 后异步扣减 quota；属于请求结束后的副作用。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Trigger
│    └─ Server/Router/Manager startup or request-side spawn
│
▼
FILE: crates/router/src/lib.rs
│
├─ Register / spawn background work
├─ 执行：请求完成并计算 cost 后异步扣减 quota；属于请求结束后的副作用。
├─ DECISION: should continue?
│    ├─ YES → sleep / await event / receive message → next iteration
│    └─ NO  → stop task
├─ DECISION: iteration failed?
│    ├─ YES → log / fail-open according to task semantics
│    └─ NO  → update state / persistence
│
▼
END / NEXT ITERATION
```


## 返回结果示例

> 后台任务通常不会直接向 HTTP 调用方返回 JSON；这里用一条构造的状态/日志结果表示一次成功执行后的可观测结果。

```text
user_id=10001 cost=0.00042 quota_before=100.00000 quota_after=99.99958 status=success
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/router/src/lib.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
