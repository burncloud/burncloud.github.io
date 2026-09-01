---
title: "类别五：Runtime 与 Process"
slug: /burncloud-node/implementation-plan/runtime-process/
---

# 类别五：Runtime 与 Process

Runtime Manager 决定“怎么运行”；Process Manager 负责“实际运行”。v0.1 只把 `GGUF + llama.cpp / llama-server` 做完整。

## Issue

| ID | 功能 | 依赖 | 状态 |
|---|---|---|---|
| NODE-401 | llama.cpp Runtime Adapter 与 ProcessSpec | NODE-103, NODE-204, NODE-303 | PLANNED |
| NODE-402 | 内部端口分配与 Process Spawn | NODE-401 | PLANNED |
| NODE-403 | Readiness / Health 状态机 | NODE-402 | PLANNED |
| NODE-404 | Stop / Crash / Restart / Logs | NODE-403 | PLANNED |

必须保持：`spawn success != READY`。