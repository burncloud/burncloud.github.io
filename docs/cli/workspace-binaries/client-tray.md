---
title: "client-tray"
slug: /cli/workspace-binaries/client-tray
hide_table_of_contents: true
---

# client-tray

**树路径：** `BurnCloud → CLI / Executables → Workspace Binaries → client-tray`

> **中文解释：** Windows tray 可执行入口；非 Windows 为不支持分支。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ [PHASE 00] OS process launch
│    ├─ executable: client-tray
│    ├─ argv / cwd / environment inherited from OS
│    └─ DECISION: executable can be loaded/launched?
│         ├─ NO → OS-level error → END
│         └─ YES → main()
│
▼
FILE: crates/client/crates/client-tray/src/main.rs
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
$ client-tray
```

## 返回结果示例

> 以下为构造的典型进程/终端结果示例；真实日志、端口、平台与数据会随运行环境变化。

```text
BurnCloud tray initialized
platform=windows
status=running
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/client/crates/client-tray/src/main.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
