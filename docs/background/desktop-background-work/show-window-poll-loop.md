---
title: "Show-window poll loop"
slug: /background/desktop-background-work/show-window-poll-loop
hide_table_of_contents: true
---

# Show-window poll loop

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Desktop Background Work → Show-window poll loop`

> **中文解释：** Dioxus async loop 周期检查 show-window 状态，执行 visible/focus。
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
FILE: crates/client/src/app.rs
│
├─ Register / spawn background work
├─ 执行：Dioxus async loop 周期检查 show-window 状态，执行 visible/focus。
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


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/client/src/app.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
