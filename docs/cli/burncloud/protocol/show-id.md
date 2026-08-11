---
title: "burncloud protocol show <id>"
slug: /cli/burncloud/protocol/show-id
hide_table_of_contents: true
---

# burncloud protocol show &lt;id&gt;

**树路径：** `BurnCloud → CLI / Executables → burncloud → burncloud protocol show <id>`

> **中文解释：** Clap 解析到 protocol 分支，再进入 src/cli/protocol.rs 中对应命令实现；参数校验失败时由 Clap/命令逻辑提前结束。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Shell input
│    ├─ command: burncloud protocol show <id>
│    ├─ argv tokenization done by shell
│    └─ process environment / cwd available
│
▼
FILE: src/main.rs
│
├─ Process bootstrap
│    ├─ dotenv load
│    ├─ ensure/generate MASTER_KEY
│    ├─ initialize logging
│    └─ inspect argv
│
├─ Top-level dispatch
│    └─ DECISION: default/server/router/client direct runtime mode?
│         ├─ YES → launch corresponding runtime
│         └─ NO → CLI parser path
│
▼
FILE: src/cli/commands.rs
│
├─ Clap parse
│    ├─ parse command/subcommand/options/positionals
│    └─ DECISION: syntax + required args valid?
│         ├─ NO → Clap help/error + exit code → END
│         └─ YES → typed command enum
│
├─ Command dispatch
│    ├─ match typed command variant
│    └─ call implementation module
│
▼
FILE: src/cli/protocol.rs
│
├─ Command-specific input validation
│    ├─ validate IDs/files/model names/ranges/options as required
│    └─ DECISION: semantic input valid?
│         ├─ NO → error output → END
│         └─ YES → perform operation
│
├─ External/state I/O
│    ├─ DB / filesystem / HTTP / service operation depending on command
│    └─ DECISION: operation succeeds?
│         ├─ NO → print/return error → END
│         └─ YES → domain result
│
▼
FILE: crates/database/crates/channel/src/channel_protocol_config.rs
│
├─ ChannelProtocolConfigModel::{list/get/upsert/delete...}
└─ SQL state → CLI output
│
├─ Output formatting
│    ├─ map result to table/text/status output
│    └─ write stdout/stderr
│
├─ Process exit
│    └─ success returns to shell; long-running command may remain active
│
▼
END
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ burncloud protocol show <id>
```

## 返回结果示例

> 以下为构造的典型终端输出示例；真实 ID、路径、金额、模型、版本与状态以实际 CLI 执行为准。

```text
$ burncloud protocol show <id>
id=1
name=OpenAI
type=openai
enabled=true
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `main()` | BurnCloud process bootstrap / top-level dispatch | PROCESS |
| 2 | `src/cli/commands.rs` | `command(), CLI dispatch` | Clap command tree + subcommand dispatch | ARGV |
| 3 | `src/cli/protocol.rs` | `handle_protocol_command()` | Protocol config CLI implementation | CLI → channel protocol DB |
| 4 | `crates/database/crates/channel/src/channel_protocol_config.rs` | `ChannelProtocolConfigModel::*` | Protocol configuration persistence | READ/WRITE channel protocol configs |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
