---
title: "/preview/home"
slug: /ui/debug-e2e-preview/preview-home
hide_table_of_contents: true
---

# /preview/home

**树路径：** `BurnCloud → UI-only Actions → Debug / e2e-preview → /preview/home`

> **中文解释：** Dioxus Router 匹配客户端路由并挂载对应页面组件；这是客户端导航，不等同于 Management REST API。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Navigation input
│    ├─ browser/client route: /preview/home
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
FILE: crates/client/src/pages/e2e_preview.rs
│
└─ selected Preview*Page component renders deterministic preview state
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
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: crates/client/src/app.rs
│    │    ├─ App()
│    │    │    └─ CALL → use_init_i18n() @ crates/client/crates/client-shared/src/i18n.rs
│    │    ├─ launch_gui_with_tray()
│    └─ FILE: crates/client/crates/client-shared/src/i18n.rs
│    │    ├─ use_init_i18n()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END / UI LOOP CONTINUES
```


## 输入示例

> UI 页面/动作的输入是导航、用户事件和当前客户端上下文；真正的网络请求会进入独立 HTTP/API E2E 页面。

```text
navigate_to=/preview/home
authenticated=true
locale=zh-CN
theme=system
```

## 返回结果示例

> UI-only 页面没有独立 REST response；这里用构造的页面渲染或本地状态结果表示用户最终看到/客户端最终持有的结果。

```text
route=/preview/home
component=preview/home
rendered=true
locale=zh-CN
theme=system
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/client/src/app.rs` | `App(), Route, launch_gui_with_tray()` | Dioxus root/router/desktop runtime | UI state |
| 2 | `crates/client/src/pages/e2e_preview.rs` | `page component / re-export` | Dioxus Route selected page module | UI component |
| 3 | `crates/client/crates/client-shared/src/i18n.rs` | `use_init_i18n()` | 由 App() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
