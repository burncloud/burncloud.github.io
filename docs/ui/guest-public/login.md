---
title: "/login"
slug: /ui/guest-public/login
hide_table_of_contents: true
---

# /login

**树路径：** `BurnCloud → UI-only Actions → Guest / Public → /login`

&gt; **中文解释：** Dioxus Router 匹配客户端路由并挂载对应页面组件；这是客户端导航，不等同于 Management REST API。
&gt;
&gt; **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ User navigation / router state
│    └─ /login
│
▼
FILE: crates/client/src/app.rs
│
├─ Dioxus Route enum/router matches path
├─ DECISION: route exists?
│    ├─ NO  → NotFound branch
│    └─ YES → mount mapped page component
├─ Component reads local contexts as needed
│    ├─ Auth context
│    ├─ Theme
│    ├─ i18n
│    └─ Toast
├─ Network calls, if any, are separate HTTP flows
│
▼
END
     └─ page rendered / UI event loop continues
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/client/src/app.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
