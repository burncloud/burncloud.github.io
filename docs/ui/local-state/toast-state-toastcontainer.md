---
title: "Toast state / ToastContainer"
slug: /ui/local-state/toast-state-toastcontainer
hide_table_of_contents: true
---

# Toast state / ToastContainer

**树路径：** `BurnCloud → UI-only Actions → Local UI State → Toast state / ToastContainer`

> **中文解释：** App 初始化 Toast state，并在根组件挂载 ToastContainer。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ [PHASE 00] App root initialization
│    └─ state/context: Toast state / ToastContainer
│
▼
FILE: crates/client/src/app.rs
│
├─ [PHASE 01] Create initial state
│    ├─ derive default/configured value
│    └─ store in Dioxus signal/context
│
├─ [PHASE 02] Provide context
│    ├─ descendant components can read/subscribe
│    └─ current render reads latest value
│
├─ [PHASE 03] Update path
│    └─ DECISION: UI event changes this state?
│         ├─ NO → keep current value
│         └─ YES
│              ├─ mutate signal/context
│              └─ mark dependent subtree dirty
│
├─ [PHASE 04] Re-render
│    └─ Dioxus reconciles affected component tree
│
▼
END / UI EVENT LOOP CONTINUES
```


## 输入示例

> UI 页面/动作的输入是导航、用户事件和当前客户端上下文；真正的网络请求会进入独立 HTTP/API E2E 页面。

```json
{
  "context": "Toast state / ToastContainer",
  "event": "component render/update",
  "current_state": "example"
}
```

## 返回结果示例

> UI-only 页面没有独立 REST response；这里用构造的页面渲染或本地状态结果表示用户最终看到/客户端最终持有的结果。

```json
{
  "visible": true,
  "level": "success",
  "message": "操作成功"
}
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/client/src/app.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
