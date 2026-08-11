---
title: "window maximize"
slug: /ui/desktop/window-maximize
hide_table_of_contents: true
---

# window maximize

**树路径：** `BurnCloud → UI-only Actions → Desktop UI → window maximize`

> **中文解释：** 桌面启动时执行窗口最大化相关动作。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ [PHASE 00] Desktop event/state input
│    └─ action: window maximize
│
▼
FILE: crates/client/src/app.rs
│
├─ [PHASE 01] Platform branch
│    └─ DECISION: current platform/runtime supports desktop action?
│         ├─ NO → skip/unsupported branch → END
│         └─ YES → obtain desktop window/tray handle
│
├─ [PHASE 02] Current UI state
│    ├─ read visibility/focus/maximized/tray state as needed
│    └─ decide desired state
│
├─ [PHASE 03] Apply desktop side effect
│    ├─ maximize / show / hide / focus / tray startup
│    └─ DECISION: OS/window operation succeeds?
│         ├─ NO → log/ignore according to UI path
│         └─ YES → state visible to user
│
├─ [PHASE 04] Event loop handoff
│    └─ return control to Dioxus/desktop event loop
│
▼
END / LOOP CONTINUES
```


## 输入示例

> UI 页面/动作的输入是导航、用户事件和当前客户端上下文；真正的网络请求会进入独立 HTTP/API E2E 页面。

```text
event=window maximize
platform=desktop
window_state=available
```

## 返回结果示例

> UI-only 页面没有独立 REST response；这里用构造的页面渲染或本地状态结果表示用户最终看到/客户端最终持有的结果。

```text
window.maximized=true
window.visible=true
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/client/src/app.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
