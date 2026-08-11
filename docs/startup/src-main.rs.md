---
title: "src/main.rs"
slug: /startup/src-main.rs
hide_table_of_contents: true
---

# src/main.rs

**树路径：** `BurnCloud → Startup → Startup Chain → src/main.rs`

&gt; **中文解释：** 进程入口：dotenv → MASTER_KEY → logging → 平台/argv 分发；无参数按平台启动 GUI/LiveView，显式参数进入 server/router/client/CLI。
&gt;
&gt; **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Process startup
│    └─ src/main.rs
│
▼
FILE: src/main.rs
│
├─ 进程入口：dotenv → MASTER_KEY → logging → 平台/argv 分发；无参数按平台启动 GUI/LiveView，显式参数进入 server/router/client/CLI。
├─ DECISION: initialization step fails?
│    ├─ YES → propagate error / process startup fails
│    └─ NO  → continue next initialization stage
│
├─ Runtime objects / routes / tasks become available
│
▼
END
     └─ server/client/runtime enters steady state
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `src/main.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
