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
├─ Shell / Terminal
│    └─ burncloud protocol show <id>
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
FILE: src/cli/protocol.rs
│
├─ Execute command-specific DB / service / filesystem / HTTP logic
├─ DECISION: operation successful?
│    ├─ NO  → print/return error
│    └─ YES → print result / start requested runtime
│
▼
END
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

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `src/main.rs` |
| 2 | `src/cli/commands.rs` |
| 3 | `src/cli/protocol.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
