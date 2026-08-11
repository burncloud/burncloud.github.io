---
title: "Windows tray startup"
slug: /ui/desktop/windows-tray-startup
hide_table_of_contents: true
---

# Windows tray startup

**树路径：** `BurnCloud → UI-only Actions → Desktop UI → Windows tray startup`

&gt; **中文解释：** Windows 平台启动 tray thread。
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
├─ 执行：Windows 平台启动 tray thread。
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
