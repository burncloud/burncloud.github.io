---
title: "burncloud user login"
slug: /cli/burncloud/user/login
hide_table_of_contents: true
---

# burncloud user login

**树路径：** `BurnCloud → CLI / Executables → burncloud → burncloud user login`

> **中文解释：** Clap 解析到 user 分支，再进入 src/cli/user.rs 中对应命令实现；参数校验失败时由 Clap/命令逻辑提前结束。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ Shell input
│    ├─ command: burncloud user login
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
FILE: src/cli/user.rs
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
FILE: crates/service/crates/user/src/lib.rs
│
└─ UserService operation
│
▼
FILE: crates/database/crates/user/src/lib.rs
│
└─ UserDatabase operation → domain result
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
│    ├─ FILE: src/cli/user.rs
│    │    ├─ handle_user_command()
│    │    │    └─ CALL → UserDatabase::init() @ crates/database/crates/user/src/lib.rs
│    │    │    └─ CALL → cmd_user_register() @ src/cli/user.rs
│    │    │    └─ CALL → cmd_user_login() @ src/cli/user.rs
│    │    │    └─ CALL → cmd_user_list() @ src/cli/user.rs
│    │    │    └─ CALL → cmd_user_topup() @ src/cli/user.rs
│    │    │    └─ CALL → cmd_user_recharges() @ src/cli/user.rs
│    │    │    └─ CALL → cmd_user_check_username() @ src/cli/user.rs
│    │    ├─ cmd_user_register()
│    │    │    └─ CALL → UserDatabase::get_user_by_username() @ crates/database/crates/user/src/lib.rs
│    │    │    └─ CALL → UserDatabase::create_user() @ crates/database/crates/user/src/lib.rs
│    │    │    └─ CALL → UserDatabase::assign_role() @ crates/database/crates/user/src/lib.rs
│    │    ├─ cmd_user_login()
│    │    │    └─ CALL → UserDatabase::get_user_by_username() @ crates/database/crates/user/src/lib.rs
│    │    │    └─ CALL → BundleVerifier::verify() @ crates/installer/src/bundle.rs
│    │    │    └─ CALL → UserDatabase::get_user_roles() @ crates/database/crates/user/src/lib.rs
│    │    ├─ cmd_user_list()
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → UserDatabase::list_users() @ crates/database/crates/user/src/lib.rs
│    │    ├─ cmd_user_topup()
│    │    │    └─ CALL → UserDatabase::get_user_by_username() @ crates/database/crates/user/src/lib.rs
│    │    │    └─ CALL → UserDatabase::get_user_by_id() @ crates/database/crates/user/src/lib.rs
│    │    │    └─ CALL → UserDatabase::create_recharge() @ crates/database/crates/user/src/lib.rs
│    │    │    └─ CALL → UserDatabase::update_balance() @ crates/database/crates/user/src/lib.rs
│    │    ├─ cmd_user_recharges()
│    │    │    └─ CALL → ok() @ crates/server/src/api/response.rs
│    │    │    └─ CALL → UserDatabase::list_recharges() @ crates/database/crates/user/src/lib.rs
│    │    ├─ cmd_user_check_username()
│    │    │    └─ CALL → UserDatabase::get_user_by_username() @ crates/database/crates/user/src/lib.rs
│    ├─ FILE: crates/database/crates/user/src/lib.rs
│    │    ├─ UserDatabase::init()
│    │    │    └─ CALL → Database::kind() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::query() @ crates/database/src/database.rs
│    │    │    └─ CALL → DatabaseConnection::pool() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::fetch_one() @ crates/database/src/database.rs
│    │    │    └─ CALL → Database::fetch_all() @ crates/database/src/database.rs
│    │    │    └─ CALL → UserDatabase::assign_role() @ crates/database/crates/user/src/lib.rs
│    │    ├─ UserDatabase::assign_role()
│    │    ├─ UserDatabase::get_user_by_username()
│    │    ├─ UserDatabase::create_user()
│    │    ├─ UserDatabase::get_user_roles()
│    │    ├─ UserDatabase::list_users()
│    │    ├─ UserDatabase::get_user_by_id()
│    │    ├─ UserDatabase::create_recharge()
│    │    ├─ UserDatabase::update_balance()
│    │    ├─ UserDatabase::list_recharges()
│    ├─ FILE: crates/database/src/database.rs
│    │    ├─ Database::kind()
│    │    ├─ Database::query()
│    │    ├─ DatabaseConnection::pool()
│    │    ├─ Database::fetch_one()
│    │    ├─ Database::fetch_all()
│    ├─ FILE: crates/installer/src/bundle.rs
│    │    ├─ BundleVerifier::verify()
│    └─ FILE: crates/server/src/api/response.rs
│    │    ├─ ok()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
│

▼
END
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ burncloud user login
```

## 返回结果示例

> 以下为构造的典型终端输出示例；真实 ID、路径、金额、模型、版本与状态以实际 CLI 执行为准。

```text
$ burncloud user login
Login successful
username=demo_user
client state saved
```





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `main()` | BurnCloud process bootstrap / top-level dispatch | PROCESS |
| 2 | `src/cli/commands.rs` | `command(), CLI dispatch` | Clap command tree + subcommand dispatch | ARGV |
| 3 | `src/cli/user.rs` | `handle_user_command()` | User CLI implementation | CLI → UserService |
| 4 | `crates/service/crates/user/src/lib.rs` | `UserService::*` | User/auth business service | SERVICE |
| 5 | `crates/database/crates/user/src/lib.rs` | `UserDatabase::*` | User/role/recharge persistence | READ/WRITE user state |
| 6 | `crates/database/src/database.rs` | `Database::fetch_all(), Database::fetch_one(), Database::kind(), Database::query(), DatabaseConnection::pool()` | 由 UserDatabase::init() 直接调用 | CALL / runtime-specific |
| 7 | `crates/installer/src/bundle.rs` | `BundleVerifier::verify()` | 由 cmd_user_login() 直接调用 | CALL / runtime-specific |
| 8 | `crates/server/src/api/response.rs` | `ok()` | 由 cmd_user_list() 直接调用；由 cmd_user_recharges() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
