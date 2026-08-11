---
title: "Theme state"
slug: /ui/local-state/theme-state
hide_table_of_contents: true
---

# Theme state

**树路径：** `BurnCloud → UI-only Actions → Local UI State → Theme state`

> **中文解释：** App 初始化主题状态，驱动 UI 主题。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ App root initialization
│    └─ state/context: Theme state
│
▼
FILE: crates/client/src/app.rs
│
├─ Create initial state
│    ├─ derive default/configured value
│    └─ store in Dioxus signal/context
│
├─ Provide context
│    ├─ descendant components can read/subscribe
│    └─ current render reads latest value
│
├─ Update path
│    └─ DECISION: UI event changes this state?
│         ├─ NO → keep current value
│         └─ YES
│              ├─ mutate signal/context
│              └─ mark dependent subtree dirty
│
├─ Re-render
│    └─ Dioxus reconciles affected component tree
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
END / UI EVENT LOOP CONTINUES
```


## 输入示例

> UI 页面/动作的输入是导航、用户事件和当前客户端上下文；真正的网络请求会进入独立 HTTP/API E2E 页面。

```json
{
  "context": "Theme state",
  "event": "component render/update",
  "current_state": "example"
}
```

## 返回结果示例

> UI-only 页面没有独立 REST response；这里用构造的页面渲染或本地状态结果表示用户最终看到/客户端最终持有的结果。

```json
{
  "theme": "system",
  "resolved": "dark"
}
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/client/src/app.rs` | `App(), Route, launch_gui_with_tray()` | Dioxus root/router/desktop runtime | UI state |
| 2 | `crates/client/crates/client-shared/src/i18n.rs` | `use_init_i18n()` | 由 App() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
