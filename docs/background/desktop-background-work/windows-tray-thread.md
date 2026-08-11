---
title: "Windows tray thread"
slug: /background/desktop-background-work/windows-tray-thread
hide_table_of_contents: true
---

# Windows tray thread

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Desktop Background Work → Windows tray thread`

&gt; **中文解释：** Windows 桌面启动系统托盘线程，处理托盘生命周期。
&gt;
&gt; **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

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
├─ 执行：Windows 桌面启动系统托盘线程，处理托盘生命周期。
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
| 2 | `crates/client/crates/client-tray/src/main.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
