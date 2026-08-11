---
title: "burncloud monitor server"
slug: /cli/burncloud/monitor/server
hide_table_of_contents: true
---

# burncloud monitor server

**树路径：** `BurnCloud → CLI / Executables → burncloud → burncloud monitor server`

> **中文解释：** Clap 解析到 monitor 分支，再进入 src/cli/monitor.rs 中对应命令实现；参数校验失败时由 Clap/命令逻辑提前结束。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Shell input
│    ├─ command: burncloud monitor server
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
FILE: src/cli/monitor.rs
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
├─ Output formatting
│    ├─ map result to table/text/status output
│    └─ write stdout/stderr
│
├─ Process exit
│    └─ success returns to shell; long-running command may remain active
│
│
├─ 源码函数展开（静态扫描确认）
│    ├─ FILE: src/cli/monitor.rs
│    │    ├─ cmd_monitor_status()
│    │    │    └─ CALL → ChannelProviderModel::list() @ crates/database/crates/channel/src/channel_provider.rs
│    │    │    └─ CALL → get_today_stats() @ src/cli/monitor.rs
│    │    ├─ cmd_monitor_server()
│    │    │    └─ CALL → check_server_status() @ src/cli/monitor.rs
│    │    │    └─ CALL → show_recent_logs() @ src/cli/monitor.rs
│    │    │    └─ CALL → show_tmux_output() @ src/cli/monitor.rs
│    │    ├─ get_today_stats()
│    │    │    └─ CALL → ph() @ crates/database/src/placeholder.rs
│    │    ├─ check_server_status()
│    │    │    └─ CALL → check_process_running() @ src/cli/monitor.rs
│    │    │    └─ CALL → get_process_pid() @ src/cli/monitor.rs
│    │    │    └─ CALL → check_tmux_session() @ src/cli/monitor.rs
│    │    │    └─ CALL → check_port_in_use() @ src/cli/monitor.rs
│    │    │    └─ CALL → get_last_log_time() @ src/cli/monitor.rs
│    │    │    └─ CALL → get_process_uptime() @ src/cli/monitor.rs
│    │    │    └─ CALL → get_recent_errors() @ src/cli/monitor.rs
│    │    ├─ show_recent_logs()
│    │    ├─ show_tmux_output()
│    │    ├─ check_process_running()
│    │    ├─ get_process_pid()
│    │    ├─ check_tmux_session()
│    │    ├─ check_port_in_use()
│    │    ├─ get_last_log_time()
│    │    ├─ get_process_uptime()
│    │    ├─ get_recent_errors()
│    ├─ FILE: crates/database/crates/channel/src/channel_provider.rs
│    │    ├─ ChannelProviderModel::list()
│    │    │    └─ CALL → ph() @ crates/database/src/placeholder.rs
│    └─ FILE: crates/database/src/placeholder.rs
│    │    ├─ ph()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ burncloud monitor server
```

## 返回结果示例

> 以下为构造的典型终端输出示例；真实 ID、路径、金额、模型、版本与状态以实际 CLI 执行为准。

```text
$ burncloud monitor server
Monitor server started
status=running
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `main()` | BurnCloud process bootstrap / top-level dispatch | PROCESS |
| 2 | `src/cli/commands.rs` | `command(), CLI dispatch` | Clap command tree + subcommand dispatch | ARGV |
| 3 | `src/cli/monitor.rs` | `cmd_monitor_status(), cmd_monitor_server()` | System/server monitor CLI | READ DB/OS process state |
| 4 | `crates/database/crates/channel/src/channel_provider.rs` | `ChannelProviderModel::list()` | 由 cmd_monitor_status() 直接调用 | CALL / runtime-specific |
| 5 | `crates/database/src/placeholder.rs` | `ph()` | 由 ChannelProviderModel::list() 直接调用；由 get_today_stats() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
