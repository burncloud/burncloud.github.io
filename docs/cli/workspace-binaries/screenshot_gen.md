---
title: "screenshot_gen"
slug: /cli/workspace-binaries/screenshot_gen
hide_table_of_contents: true
---

# screenshot_gen

**树路径：** `BurnCloud → CLI / Executables → Workspace Binaries → screenshot_gen`

> **中文解释：** 开发辅助二进制：创建 VirtualDom 并生成页面 SSR/screenshot 相关输出。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ OS process launch
│    ├─ executable: screenshot_gen
│    ├─ argv / cwd / environment inherited from OS
│    └─ DECISION: executable can be loaded/launched?
│         ├─ NO → OS-level error → END
│         └─ YES → main()
│
▼
FILE: crates/client/src/bin/screenshot_gen.rs
│
├─ main() initialization
│    ├─ initialize executable-specific runtime/services
│    ├─ parse any supported arguments
│    └─ DECISION: platform/arguments/initialization valid?
│         ├─ NO → print/return error → process exit
│         └─ YES → continue
│
├─ Runtime work
│    ├─ create client/download/loop/tray structures as applicable
│    ├─ start event loop or execute one-shot job
│    └─ DECISION: long-running executable?
│         ├─ YES → enter event/service loop
│         └─ NO → produce output and exit
│
├─ Error boundary
│    └─ runtime error → log/return non-success according to executable implementation
│
▼
END / RUNNING LOOP
```


## 输入示例

> CLI 的输入就是进程参数/子命令；下面给出与本页入口对应的典型终端调用。

```text
$ screenshot_gen
```

## 返回结果示例

> 以下为构造的典型进程/终端结果示例；真实日志、端口、平台与数据会随运行环境变化。

```text
VirtualDom rendered
output=screenshot.html
status=success
```



## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/client/src/bin/screenshot_gen.rs` | `entry-specific function(s) shown in E2E` | 当前入口在该文件执行的直接调用点 | runtime-specific |

> Source Traversal 只记录真实执行/调用链；单纯类型定义、未调用模块或“可能会经过”的文件不加入。

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
