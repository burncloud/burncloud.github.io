---
title: "/register"
slug: /ui/guest-public/register
hide_table_of_contents: true
---

# /register

**树路径：** `BurnCloud → UI-only Actions → Guest / Public → /register`

> **中文解释：** Dioxus Router 匹配客户端路由并挂载对应页面组件；这是客户端导航，不等同于 Management REST API。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Navigation input
│    ├─ browser/client route: /register
│    ├─ current Auth context
│    ├─ current Theme/i18n/Toast context
│    └─ optional route params/query
│
▼
FILE: crates/client/src/app.rs
│
├─ Dioxus Router match
│    └─ DECISION: Route enum/path matches?
│         ├─ NO → NotFound route/component
│         └─ YES → select mapped page component
│
├─ Route guards / context read
│    ├─ component can read Auth context
│    ├─ component can read Theme/i18n state
│    └─ DECISION: page requires authenticated state and context satisfies it?
│         ├─ NO → login/guard behavior as implemented by component/router
│         └─ YES → render page
│
▼
FILE: crates/client/crates/client-register/src/lib.rs
│
└─ actual page component implementation / local effects
│
├─ Component construction
│    ├─ initialize local signals/state
│    ├─ render initial VDOM
│    └─ register click/input/effect handlers
│
├─ Data boundary
│    └─ DECISION: component action/effect needs server data?
│         ├─ NO → remain local UI-only path
│         └─ YES → issue separate HTTP/API request
│              └─ that request is documented under HTTP / API, not hidden in this flow
│
├─ User-visible result
│    ├─ Dioxus reconciles VDOM
│    └─ page/render state becomes visible
│
├─ Event loop
│    └─ wait for next UI event/navigation/state update
│
▼
END / UI LOOP CONTINUES
```


## 输入示例

> UI 页面/动作的输入是导航、用户事件和当前客户端上下文；真正的网络请求会进入独立 HTTP/API E2E 页面。

```text
navigate_to=/register
authenticated=true
locale=zh-CN
theme=system
```

## 返回结果示例

> UI-only 页面没有独立 REST response；这里用构造的页面渲染或本地状态结果表示用户最终看到/客户端最终持有的结果。

```text
route=/register
component=register
rendered=true
locale=zh-CN
theme=system
```



## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/client/src/app.rs` | `见上方 E2E 对应函数/入口` | 该 CLI/UI/Background/Startup 页面真实执行文件 | runtime-specific |
| 2 | `crates/client/src/components/guest_layout.rs` | `GuestLayout` | guest route layout wrapper | UI layout |
| 3 | `crates/client/crates/client-register/src/lib.rs` | `RegisterPage` | 实际页面组件 crate | UI component/effects |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
