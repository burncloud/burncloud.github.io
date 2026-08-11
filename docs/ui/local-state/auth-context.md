---
title: "Auth context"
slug: /ui/local-state/auth-context
hide_table_of_contents: true
---

# Auth context

**树路径：** `BurnCloud → UI-only Actions → Local UI State → Auth context`

&gt; **中文解释：** App 初始化客户端认证上下文，页面据此读取登录状态。
&gt;
&gt; **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
▼
FILE: crates/client/src/app.rs
│
├─ App root initializes Auth context
├─ Provide state/context to descendant components
├─ DECISION: component updates state?
│    ├─ YES → Dioxus re-render affected subtree
│    └─ NO  → keep current state
│
▼
END / UI LOOP CONTINUES
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/client/src/app.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
