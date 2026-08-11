---
title: "burncloud channel delete <id>"
slug: /cli/burncloud/channel/delete-id
hide_table_of_contents: true
---

# burncloud channel delete &lt;id&gt;

**树路径：** `BurnCloud → CLI / Executables → burncloud → burncloud channel delete <id>`

> **中文解释：** Clap 解析到 channel 分支，再进入 src/cli/channel.rs 中对应命令实现；参数校验失败时由 Clap/命令逻辑提前结束。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Shell input
│    ├─ command: burncloud channel delete <id>
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
FILE: src/cli/channel.rs
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
FILE: crates/service/crates/channel/src/lib.rs
│
└─ ChannelService operation
│
▼
FILE: crates/database/crates/channel/src/channel_provider.rs
│
└─ ChannelProviderModel CRUD → DB result
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
│    ├─ FILE: src/cli/channel.rs
│    │    ├─ handle_channel_command()
│    │    │    └─ CALL → cmd_channel_add() @ src/cli/channel.rs
│    │    │    └─ CALL → cmd_channel_list() @ src/cli/channel.rs
│    │    │    └─ CALL → cmd_channel_show() @ src/cli/channel.rs
│    │    │    └─ CALL → cmd_channel_update() @ src/cli/channel.rs
│    │    │    └─ CALL → cmd_channel_delete() @ src/cli/channel.rs
│    │    ├─ cmd_channel_add()
│    │    │    └─ CALL → parse_channel_type() @ src/cli/channel.rs
│    │    │    └─ CALL → get_default_models() @ src/cli/channel.rs
│    │    │    └─ CALL → get_default_base_url() @ src/cli/channel.rs
│    │    │    └─ CALL → get_default_channel_name() @ src/cli/channel.rs
│    │    │    └─ CALL → ChannelProviderModel::create() @ crates/database/crates/channel/src/channel_provider.rs
│    │    ├─ cmd_channel_list()
│    │    │    └─ CALL → ChannelProviderModel::list() @ crates/database/crates/channel/src/channel_provider.rs
│    │    │    └─ CALL → get_channel_type_name() @ src/cli/channel.rs
│    │    ├─ cmd_channel_show()
│    │    │    └─ CALL → ChannelProviderModel::get_by_id() @ crates/database/crates/channel/src/channel_provider.rs
│    │    │    └─ CALL → get_channel_type_name() @ src/cli/channel.rs
│    │    ├─ cmd_channel_update()
│    │    │    └─ CALL → ChannelProviderModel::get_by_id() @ crates/database/crates/channel/src/channel_provider.rs
│    │    │    └─ CALL → ChannelProviderModel::update() @ crates/database/crates/channel/src/channel_provider.rs
│    │    ├─ cmd_channel_delete()
│    │    │    └─ CALL → ChannelProviderModel::get_by_id() @ crates/database/crates/channel/src/channel_provider.rs
│    │    │    └─ CALL → ChannelProviderModel::delete() @ crates/database/crates/channel/src/channel_provider.rs
│    │    ├─ parse_channel_type()
│    │    ├─ get_default_models()
│    │    ├─ get_default_base_url()
│    │    ├─ get_default_channel_name()
│    │    ├─ get_channel_type_name()
│    └─ FILE: crates/database/crates/channel/src/channel_provider.rs
│    │    ├─ ChannelProviderModel::create()
│    │    ├─ ChannelProviderModel::list()
│    │    ├─ ChannelProviderModel::get_by_id()
│    │    ├─ ChannelProviderModel::update()
│    │    ├─ ChannelProviderModel::delete()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ burncloud channel delete <id>
```

## 返回结果示例

> 以下为构造的典型终端输出示例；真实 ID、路径、金额、模型、版本与状态以实际 CLI 执行为准。

```text
$ burncloud channel delete <id>
Channel deleted successfully
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `main()` | BurnCloud process bootstrap / top-level dispatch | PROCESS |
| 2 | `src/cli/commands.rs` | `command(), CLI dispatch` | Clap command tree + subcommand dispatch | ARGV |
| 3 | `src/cli/channel.rs` | `handle_channel_command()` | Channel CLI implementation | CLI → service/DB |
| 4 | `crates/service/crates/channel/src/lib.rs` | `ChannelService::*` | Channel service boundary | SERVICE |
| 5 | `crates/database/crates/channel/src/channel_provider.rs` | `ChannelProviderModel::*` | Channel provider persistence | READ/WRITE channel_providers |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
