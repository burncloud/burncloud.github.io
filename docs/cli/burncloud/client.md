---
title: "client"
slug: /cli/burncloud/client
hide_table_of_contents: true
---

# client

**树路径：** `BurnCloud → CLI / Executables → burncloud → client`

&gt; **中文解释：** 显式启动 Client 模式。
&gt;
&gt; **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Shell / Terminal
│    └─ burncloud client
│
▼
FILE: src/main.rs
│
├─ dotenv
├─ ensure / generate MASTER_KEY
├─ init_logging
├─ parse argv
├─ DECISION: direct server/router/client/default mode?
│    ├─ YES → corresponding runtime entry
│    └─ NO  → Clap CLI dispatch
│
▼
FILE: src/cli/commands.rs
│
├─ Match command / subcommand
├─ DECISION: parameters valid?
│    ├─ NO  → Clap/command error → END
│    └─ YES → dispatch implementation
│
▼
FILE: src/cli/commands.rs
│
├─ Execute command-specific DB / service / filesystem / HTTP logic
├─ DECISION: operation successful?
│    ├─ NO  → print/return error
│    └─ YES → print result / start requested runtime
│
▼
END
```


## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `src/main.rs` |
| 2 | `src/cli/commands.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
