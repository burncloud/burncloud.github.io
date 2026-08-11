---
title: "show / hide / focus"
slug: /ui/desktop/show-hide-focus
hide_table_of_contents: true
---

# show / hide / focus

**树路径：** `BurnCloud → UI-only Actions → Desktop UI → show / hide / focus`

> **中文解释：** 后台 poll 接收到 show-window 状态后更新窗口 visible/focus。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Desktop event/state input
│    └─ action: show / hide / focus
│
▼
FILE: crates/client/src/app.rs
│
├─ Platform branch
│    └─ DECISION: current platform/runtime supports desktop action?
│         ├─ NO → skip/unsupported branch → END
│         └─ YES → obtain desktop window/tray handle
│
├─ Current UI state
│    ├─ read visibility/focus/maximized/tray state as needed
│    └─ decide desired state
│
├─ Apply desktop side effect
│    ├─ maximize / show / hide / focus / tray startup
│    └─ DECISION: OS/window operation succeeds?
│         ├─ NO → log/ignore according to UI path
│         └─ YES → state visible to user
│
├─ Event loop handoff
│    └─ return control to Dioxus/desktop event loop
│
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: crates/client/src/app.rs
│    │    ├─ App()
│    │    │    └─ CALL → use_init_i18n() @ crates/client/crates/client-shared/src/i18n.rs
│    │    │    └─ CALL → use_init_toast() @ crates/client/crates/client-shared/src/components/toast.rs
│    │    │    └─ CALL → use_init_auth() @ crates/client/crates/client-shared/src/auth_context.rs
│    │    │    └─ CALL → ThemeContext::use_init_theme() @ crates/client/crates/client-shared/src/theme_context.rs
│    │    ├─ launch_gui_with_tray()
│    ├─ FILE: crates/client/crates/client-shared/src/i18n.rs
│    │    ├─ use_init_i18n()
│    ├─ FILE: crates/client/crates/client-shared/src/components/toast.rs
│    │    ├─ use_init_toast()
│    ├─ FILE: crates/client/crates/client-shared/src/auth_context.rs
│    │    ├─ use_init_auth()
│    └─ FILE: crates/client/crates/client-shared/src/theme_context.rs
│    │    ├─ ThemeContext::use_init_theme()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END / LOOP CONTINUES
```


## 输入示例

> UI 页面/动作的输入是导航、用户事件和当前客户端上下文；真正的网络请求会进入独立 HTTP/API E2E 页面。

```text
event=show / hide / focus
platform=desktop
window_state=available
```

## 返回结果示例

> UI-only 页面没有独立 REST response；这里用构造的页面渲染或本地状态结果表示用户最终看到/客户端最终持有的结果。

```text
show_window=true
window.visible=true
window.focused=true
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/client/src/app.rs` | `App(), Route, launch_gui_with_tray()` | Dioxus root/router/desktop runtime | UI state |
| 2 | `crates/client/crates/client-shared/src/i18n.rs` | `use_init_i18n()` | 由 App() 直接调用 | CALL / runtime-specific |
| 3 | `crates/client/crates/client-shared/src/components/toast.rs` | `use_init_toast()` | 由 App() 直接调用 | CALL / runtime-specific |
| 4 | `crates/client/crates/client-shared/src/auth_context.rs` | `use_init_auth()` | 由 App() 直接调用 | CALL / runtime-specific |
| 5 | `crates/client/crates/client-shared/src/theme_context.rs` | `ThemeContext::use_init_theme()` | 由 App() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
