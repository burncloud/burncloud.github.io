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
| 1 | `crates/client/src/app.rs` | `见上方 E2E 对应函数/入口` | 该 CLI/UI/Background/Startup 页面真实执行文件 | runtime-specific |

> 这个索引只列入当前执行链中有源码依据的文件；类型定义文件但不执行逻辑的，不为了凑数量加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
