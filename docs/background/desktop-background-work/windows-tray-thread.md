---
title: "Windows tray thread"
slug: /background/desktop-background-work/windows-tray-thread
hide_table_of_contents: true
---

# Windows tray thread

**树路径：** `BurnCloud → Background Jobs / Async Side Effects → Desktop Background Work → Windows tray thread`

> **中文解释：** Windows 桌面启动系统托盘线程，处理托盘生命周期。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START / TRIGGER
│
├─ Trigger source
│    ├─ startup spawn / request-time tokio::spawn / manager restoration / channel message
│    └─ task: Windows tray thread
│
├─ Spawn / registration
│    ├─ parent runtime creates async task/thread/loop
│    └─ DECISION: spawn/runtime handle available?
│         ├─ NO → task never starts; parent may log error
│         └─ YES → task owns/borrows required shared state
│
├─ Wait boundary
│    ├─ timer sleep / mpsc receive / polling interval / restored work item
│    └─ DECISION: trigger/event available?
│         ├─ NO → continue waiting
│         └─ YES → one iteration begins
│
├─ Input snapshot
│    ├─ read latest runtime/DB/request-derived state needed by job
│    └─ freeze iteration context
│
├─ Core job operation
│    ├─ execute Windows tray thread
│    └─ may call DB / HTTP / filesystem / runtime service depending on task
│
├─ Operation result
│    └─ DECISION: iteration succeeds?
│         ├─ NO
│         │    ├─ log/record failure
│         │    ├─ preserve parent request availability when task is fail-open
│         │    └─ decide retry on next event/interval
│         └─ YES
│              ├─ update in-memory state and/or persistent state
│              └─ emit success telemetry/log
│
├─ Cancellation / lifetime
│    └─ DECISION: parent runtime still alive AND task should continue?
│         ├─ YES → 返回等待边界
│         └─ NO → release task resources
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
END / NEXT ITERATION
```


## 输入示例

> 后台任务通常没有 HTTP 请求体；这里把触发事件、队列/定时器和共享状态视为它的输入。

```text
trigger=Desktop Background Work
job=Windows tray thread
runtime=running
shared_state=available
# 该类页面的“输入”不是 HTTP body，而是启动事件、定时器、队列消息或请求侧异步事件。
```

## 返回结果示例

> 后台任务通常不会直接向 HTTP 调用方返回 JSON；这里用一条构造的状态/日志结果表示一次成功执行后的可观测结果。

```text
tray=started icon=visible menu_items=3 status=running
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/client/src/app.rs` | `App(), Route, launch_gui_with_tray()` | Dioxus root/router/desktop runtime | UI state |
| 2 | `crates/client/crates/client-tray/src/main.rs` | `page/service component implementation` | Feature-specific client crate reached from page wrapper | UI effects/state |
| 3 | `crates/client/crates/client-shared/src/i18n.rs` | `use_init_i18n()` | 由 App() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
