---
title: "burncloud-loop"
slug: /cli/workspace-binaries/burncloud-loop
hide_table_of_contents: true
---

# burncloud-loop

**树路径：** `BurnCloud → CLI / Executables → Workspace Binaries → burncloud-loop`

> **中文解释：** Loop 工具入口，按子命令执行 jobs-aesthetic/css-optimize/gate/gates/list-gates。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ [PHASE 00] OS process launch
│    ├─ executable: burncloud-loop
│    ├─ argv / cwd / environment inherited from OS
│    └─ DECISION: executable can be loaded/launched?
│         ├─ NO → OS-level error → END
│         └─ YES → main()
│
▼
FILE: crates/loops/src/main.rs
│
├─ [PHASE 01] main() initialization
│    ├─ initialize executable-specific runtime/services
│    ├─ parse any supported arguments
│    └─ DECISION: platform/arguments/initialization valid?
│         ├─ NO → print/return error → process exit
│         └─ YES → continue
│
├─ [PHASE 02] Runtime work
│    ├─ create client/download/loop/tray structures as applicable
│    ├─ start event loop or execute one-shot job
│    └─ DECISION: long-running executable?
│         ├─ YES → enter event/service loop
│         └─ NO → produce output and exit
│
├─ [PHASE 03] Error boundary
│    └─ runtime error → log/return non-success according to executable implementation
│
▼
END / RUNNING LOOP
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ burncloud-loop
```

## 返回结果示例

> 以下为构造的典型进程/终端结果示例；真实日志、端口、平台与数据会随运行环境变化。

```text
burncloud-loop
subcommands: jobs-aesthetic | css-optimize | gate | gates | list-gates
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/loops/src/main.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
