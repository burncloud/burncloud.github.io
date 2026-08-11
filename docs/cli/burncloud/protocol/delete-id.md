---
title: "burncloud protocol delete <id>"
slug: /cli/burncloud/protocol/delete-id
hide_table_of_contents: true
---

# burncloud protocol delete &lt;id&gt;

**树路径：** `BurnCloud → CLI / Executables → burncloud → burncloud protocol delete <id>`

> **中文解释：** Clap 解析到 protocol 分支，再进入 src/cli/protocol.rs 中对应命令实现；参数校验失败时由 Clap/命令逻辑提前结束。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Shell input
│    ├─ command: burncloud protocol delete <id>
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
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: src/cli/protocol.rs
│    │    ├─ handle_protocol_command()
│    │    │    └─ CALL → ChannelProtocolConfigModel::list() @ crates/database/crates/channel/src/channel_protocol_config.rs
│    │    │    └─ CALL → channel_type_to_name() @ src/cli/protocol.rs
│    │    │    └─ CALL → ChannelProtocolConfigModel::upsert() @ crates/database/crates/channel/src/channel_protocol_config.rs
│    │    │    └─ CALL → ChannelProtocolConfigModel::delete() @ crates/database/crates/channel/src/channel_protocol_config.rs
│    │    ├─ channel_type_to_name()
│    ├─ FILE: crates/database/crates/channel/src/channel_protocol_config.rs
│    │    ├─ ChannelProtocolConfigModel::list()
│    │    │    └─ CALL → ph() @ crates/database/src/placeholder.rs
│    │    ├─ ChannelProtocolConfigModel::upsert()
│    │    │    └─ CALL → ph() @ crates/database/src/placeholder.rs
│    │    │    └─ CALL → phs() @ crates/database/src/placeholder.rs
│    │    ├─ ChannelProtocolConfigModel::delete()
│    │    │    └─ CALL → ph() @ crates/database/src/placeholder.rs
│    └─ FILE: crates/database/src/placeholder.rs
│    │    ├─ ph()
│    │    ├─ phs()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ burncloud protocol delete <id>
```

## 返回结果示例

> 以下为构造的典型终端输出示例；真实 ID、路径、金额、模型、版本与状态以实际 CLI 执行为准。

```text
$ burncloud protocol delete <id>
Protocol deleted successfully
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `main()` | BurnCloud process bootstrap / top-level dispatch | PROCESS |
| 2 | `src/cli/commands.rs` | `command(), CLI dispatch` | Clap command tree + subcommand dispatch | ARGV |
| 3 | `src/cli/protocol.rs` | `handle_protocol_command()` | Protocol config CLI implementation | CLI → channel protocol DB |
| 4 | `crates/database/crates/channel/src/channel_protocol_config.rs` | `ChannelProtocolConfigModel::*` | Protocol configuration persistence | READ/WRITE channel protocol configs |
| 5 | `crates/database/src/placeholder.rs` | `ph(), phs()` | 由 ChannelProtocolConfigModel::delete() 直接调用；由 ChannelProtocolConfigModel::list() 直接调用；由 ChannelProtocolConfigModel::upsert() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
