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
├─ Shell input
│    ├─ command: burncloud tiered add-tier <model>
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
FILE: src/cli/price.rs
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
FILE: crates/database/crates/billing/src/billing_tiered_price.rs
│
└─ BillingTieredPriceModel operation → DB result
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
│    ├─ FILE: src/cli/price.rs
│    │    ├─ handle_price_command()
│    │    │    └─ CALL → BillingPriceModel::list() @ crates/database/crates/billing/src/billing_price.rs
│    │    │    └─ CALL → from_nano() @ src/cli/price.rs
│    │    │    └─ CALL → to_nano() @ src/cli/price.rs
│    │    │    └─ CALL → BillingPriceModel::upsert() @ crates/database/crates/billing/src/billing_price.rs
│    │    │    └─ CALL → BillingPriceModel::delete_by_region() @ crates/database/crates/billing/src/billing_price.rs
│    │    │    └─ CALL → BillingPriceModel::delete_all_for_model() @ crates/database/crates/billing/src/billing_price.rs
│    │    │    └─ CALL → BillingPriceModel::get() @ crates/database/crates/billing/src/billing_price.rs
│    │    │    └─ CALL → BillingPriceModel::get_all_currencies() @ crates/database/crates/billing/src/billing_price.rs
│    │    │    └─ CALL → BillingTieredPriceModel::has_tiered_pricing() @ crates/database/crates/billing/src/billing_tiered_price.rs
│    │    │    └─ CALL → BillingTieredPriceModel::get_tiers() @ crates/database/crates/billing/src/billing_tiered_price.rs
│    │    ├─ from_nano()
│    │    │    └─ CALL → nano_to_dollars() @ crates/common/src/price_u64.rs
│    │    ├─ to_nano()
│    │    │    └─ CALL → dollars_to_nano() @ crates/common/src/price_u64.rs
│    ├─ FILE: crates/database/crates/billing/src/billing_price.rs
│    │    ├─ BillingPriceModel::list()
│    │    ├─ BillingPriceModel::upsert()
│    │    ├─ BillingPriceModel::delete_by_region()
│    │    ├─ BillingPriceModel::delete_all_for_model()
│    │    ├─ BillingPriceModel::get()
│    │    ├─ BillingPriceModel::get_all_currencies()
│    ├─ FILE: crates/database/crates/billing/src/billing_tiered_price.rs
│    │    ├─ BillingTieredPriceModel::has_tiered_pricing()
│    │    ├─ BillingTieredPriceModel::get_tiers()
│    │    │    └─ CALL → adapt_sql() @ crates/database/src/placeholder.rs
│    │    ├─ BillingTieredPriceModel::list_all()
│    │    ├─ BillingTieredPriceModel::upsert_tier()
│    │    │    └─ CALL → adapt_sql() @ crates/database/src/placeholder.rs
│    ├─ FILE: crates/common/src/pricing_config.rs
│    │    ├─ PricingConfig::from_json()
│    │    │    └─ CALL → version_major() @ crates/common/src/pricing_config.rs
│    │    ├─ version_major()
│    ├─ FILE: crates/common/src/price_u64.rs
│    │    ├─ nano_to_dollars()
│    │    ├─ dollars_to_nano()
│    └─ FILE: crates/database/src/placeholder.rs
│    │    ├─ adapt_sql()
│
├─ 规则：只展开能够解析到 BurnCloud 仓库内部真实函数定义的调用；第三方库调用保留在主 E2E 中，不伪造源码目标文件
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





## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `src/main.rs` | `main()` | BurnCloud process bootstrap / top-level dispatch | PROCESS |
| 2 | `src/cli/commands.rs` | `command(), CLI dispatch` | Clap command tree + subcommand dispatch | ARGV |
| 3 | `src/cli/price.rs` | `handle_price_command() / tiered pricing branches` | Price and tiered-pricing CLI implementation | CLI → billing DB |
| 4 | `crates/database/crates/billing/src/billing_tiered_price.rs` | `BillingTieredPriceModel::*` | Tiered price persistence | READ/WRITE tiered prices |
| 5 | `crates/database/crates/billing/src/billing_price.rs` | `BillingPriceModel::delete_all_for_model(), BillingPriceModel::delete_by_region(), BillingPriceModel::get(), BillingPriceModel::get_all_currencies(), BillingPriceModel::list(), BillingPriceModel::upsert()` | 由 handle_price_command() 直接调用 | CALL / runtime-specific |
| 6 | `crates/common/src/pricing_config.rs` | `PricingConfig::from_json(), version_major()` | 由 PricingConfig::from_json() 直接调用；由 handle_price_command() 直接调用 | CALL / runtime-specific |
| 7 | `crates/common/src/price_u64.rs` | `dollars_to_nano(), nano_to_dollars()` | 由 from_nano() 直接调用；由 to_nano() 直接调用 | CALL / runtime-specific |
| 8 | `crates/database/src/placeholder.rs` | `adapt_sql()` | 由 BillingTieredPriceModel::get_tiers() 直接调用；由 BillingTieredPriceModel::upsert_tier() 直接调用 | CALL / runtime-specific |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
