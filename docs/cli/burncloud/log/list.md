---
title: "burncloud log list"
slug: /cli/burncloud/log/list
hide_table_of_contents: true
---

# burncloud log list

**树路径：** `BurnCloud → CLI / Executables → burncloud → burncloud log list`

> **中文解释：** Clap 解析到 log 分支，再进入 src/cli/log.rs 中对应命令实现；参数校验失败时由 Clap/命令逻辑提前结束。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Shell input
│    ├─ command: burncloud log list
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
FILE: src/cli/log.rs
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
FILE: crates/service/crates/router-log/src/lib.rs
│
└─ RouterLogService query
│
▼
FILE: crates/database/crates/router/src/log.rs
│
└─ RouterLogModel / aggregation SQL
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
│    ├─ FILE: src/cli/log.rs
│    │    ├─ handle_log_command()
│    │    │    └─ CALL → cmd_log_list() @ src/cli/log.rs
│    │    │    └─ CALL → cmd_log_usage() @ src/cli/log.rs
│    │    ├─ cmd_log_list()
│    │    │    └─ CALL → RouterDatabase::get_logs_filtered() @ crates/database/crates/router/src/lib.rs
│    │    ├─ cmd_log_usage()
│    │    │    └─ CALL → get_usage_stats_by_token() @ crates/database/crates/router/src/lib.rs
│    │    │    └─ CALL → get_usage_stats() @ crates/database/crates/router/src/log.rs
│    │    │    └─ CALL → get_usd_to_cny_rate() @ src/cli/log.rs
│    │    ├─ get_usd_to_cny_rate()
│    ├─ FILE: crates/database/crates/router/src/lib.rs
│    │    ├─ RouterDatabase::get_logs_filtered()
│    │    ├─ get_usage_stats_by_token()
│    └─ FILE: crates/database/crates/router/src/log.rs
│    │    ├─ get_usage_stats()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ burncloud log list
```

## 返回结果示例

> 以下为构造的典型终端输出示例；真实 ID、路径、金额、模型、版本与状态以实际 CLI 执行为准。

```text
$ burncloud log list
2026-08-11 14:40:15  user=10001 model=gpt-5.4 channel=12 status=200 tokens=44 cost=0.00042
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `main()` | BurnCloud process bootstrap / top-level dispatch | PROCESS |
| 2 | `src/cli/commands.rs` | `command(), CLI dispatch` | Clap command tree + subcommand dispatch | ARGV |
| 3 | `src/cli/log.rs` | `handle_log_command()` | Log/usage CLI implementation | CLI → RouterLogService |
| 4 | `crates/service/crates/router-log/src/lib.rs` | `RouterLogService::*, BillingService::*` | Router log / usage / billing summary service | SERVICE |
| 5 | `crates/database/crates/router/src/log.rs` | `RouterLogModel::* / usage & billing queries` | Request accounting / usage / billing persistence | READ/WRITE router_logs |
| 6 | `crates/database/crates/router/src/lib.rs` | `RouterDatabase::get_logs_filtered(), get_usage_stats_by_token()` | 由 cmd_log_list() 直接调用；由 cmd_log_usage() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
