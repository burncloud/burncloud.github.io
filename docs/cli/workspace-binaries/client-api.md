---
title: "client-api"
slug: /cli/workspace-binaries/client-api
hide_table_of_contents: true
---

# client-api

**树路径：** `BurnCloud → CLI / Executables → Workspace Binaries → client-api`

> **中文解释：** 独立 ApiManagement 客户端 shell。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ OS process launch
│    ├─ executable: client-api
│    ├─ argv / cwd / environment inherited from OS
│    └─ DECISION: executable can be loaded/launched?
│         ├─ NO → OS-level error → END
│         └─ YES → main()
│
▼
FILE: crates/client/crates/client-api/src/main.rs
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
$ client-api
```

## 返回结果示例

> 以下为构造的典型进程/终端结果示例；真实日志、端口、平台与数据会随运行环境变化。

```text
client-api initialized
status=running
```




## 穿过的源码文件（详细）

| 顺序 | 源码文件 | 关键函数 / 符号 | 为什么会经过 | 状态 / 副作用 |
|---:|---|---|---|---|
| 1 | `crates/client/crates/client-api/src/main.rs` | `page/service component implementation` | Feature-specific client crate reached from page wrapper | UI effects/state |

> Source Traversal V4：区分“启动时执行”“请求时执行”“只注册不执行”。只有源码确认会进入的文件才加入；Handler 被 Router 注册不等于 Server 启动时执行 Handler。

**Execution classification: STATIC CONFIRMED + CONSERVATIVE STATIC CALL EXPANSION** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
