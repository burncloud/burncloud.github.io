---
title: "burncloud-client"
slug: /cli/workspace-binaries/burncloud-client
hide_table_of_contents: true
---

# burncloud-client

**树路径：** `BurnCloud → CLI / Executables → Workspace Binaries → burncloud-client`

> **中文解释：** 启动 Dioxus 客户端/桌面或 Web 入口。
>
> **源码基线：** `burncloud/burncloud@aa54e21393c6d46a6b09555ffd3661c1f22484f3`

## End-to-End Request Flow + ICFG

```text
START
│
├─ OS launches executable
│    └─ burncloud-client
│
▼
FILE: crates/client/src/main.rs
│
├─ main()
├─ initialize executable-specific runtime
├─ DECISION: platform / arguments / initialization valid?
│    ├─ NO  → error / unsupported branch
│    └─ YES → run binary purpose
│
▼
END
```


## 返回结果示例

> 以下为构造的典型进程/终端结果示例；真实日志、端口、平台与数据会随运行环境变化。

```text
BurnCloud Client
ui=initialized
route=/
status=running
```

## 穿过的源码文件

| 顺序 | 文件 |
|---|---|
| 1 | `crates/client/src/main.rs` |
| 2 | `crates/client/src/app.rs` |

**Execution classification: STATIC CONFIRMED** — 本页只描述当前源码可以直接确认的入口、分支与调用；动态 Provider/运行时状态会明确标为动态边界。
