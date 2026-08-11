---
title: "burncloud tiered add-tier <model>"
slug: /cli/burncloud/tiered/add-tier-model
hide_table_of_contents: true
---

# burncloud tiered add-tier &lt;model&gt;

**树路径：** `BurnCloud → CLI / Executables → burncloud → burncloud tiered add-tier <model>`

> **中文解释：** Clap 解析到 tiered 分支，再进入 src/cli/price.rs 中对应命令实现；参数校验失败时由 Clap/命令逻辑提前结束。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ [PHASE 00] Shell input
│    ├─ command: burncloud tiered add-tier <model>
│    ├─ argv tokenization done by shell
│    └─ process environment / cwd available
│
▼
FILE: src/main.rs
│
├─ [PHASE 01] Process bootstrap
│    ├─ dotenv load
│    ├─ ensure/generate MASTER_KEY
│    ├─ initialize logging
│    └─ inspect argv
│
├─ [PHASE 02] Top-level dispatch
│    └─ DECISION: default/server/router/client direct runtime mode?
│         ├─ YES → launch corresponding runtime
│         └─ NO → CLI parser path
│
▼
FILE: src/cli/commands.rs
│
├─ [PHASE 03] Clap parse
│    ├─ parse command/subcommand/options/positionals
│    └─ DECISION: syntax + required args valid?
│         ├─ NO → Clap help/error + exit code → END
│         └─ YES → typed command enum
│
├─ [PHASE 04] Command dispatch
│    ├─ match typed command variant
│    └─ call implementation module
│
▼
FILE: src/cli/price.rs
│
├─ [PHASE 05] Command-specific input validation
│    ├─ validate IDs/files/model names/ranges/options as required
│    └─ DECISION: semantic input valid?
│         ├─ NO → error output → END
│         └─ YES → perform operation
│
├─ [PHASE 06] External/state I/O
│    ├─ DB / filesystem / HTTP / service operation depending on command
│    └─ DECISION: operation succeeds?
│         ├─ NO → print/return error → END
│         └─ YES → domain result
│
├─ [PHASE 07] Output formatting
│    ├─ map result to table/text/status output
│    └─ write stdout/stderr
│
├─ [PHASE 08] Process exit
│    └─ success returns to shell; long-running command may remain active
│
▼
END
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ burncloud tiered add-tier <model>
```

## 返回结果示例

> 以下为构造的典型终端输出示例；真实 ID、路径、金额、模型、版本与状态以实际 CLI 执行为准。

```text
$ burncloud tiered add-tier <model>
Tier added successfully
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `src/main.rs` |
| 2 | `src/cli/commands.rs` |
| 3 | `src/cli/price.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
