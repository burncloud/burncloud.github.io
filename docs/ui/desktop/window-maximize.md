---
title: "window maximize"
slug: /ui/desktop/window-maximize
hide_table_of_contents: true
---

# window maximize

**树路径：** `BurnCloud → UI-only Actions → Desktop UI → window maximize`

&gt; **中文解释：** 桌面启动时执行窗口最大化相关动作。
&gt;
&gt; **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
▼
FILE: crates/client/src/app.rs
│
├─ Desktop platform branch
├─ 执行：桌面启动时执行窗口最大化相关动作。
├─ DECISION: platform/state allows action?
│    ├─ NO  → skip / unsupported branch
│    └─ YES → apply window/tray state
│
▼
END / DESKTOP LOOP CONTINUES
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/client/src/app.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
