---
title: "类别一：Node Core"
slug: /burncloud-node/implementation-plan/node-core/
---

# 类别一：Node Core

Node Core 只负责把现有 BurnCloud 能力组合成一个 Node 运行形态，不重新实现已有业务组件。

## Issue

| ID | 功能 | 依赖 | 状态 |
|---|---|---|---|
| NODE-001 | 建立 Node 启动入口与生命周期 | 无 | PLANNED |
| NODE-002 | 建立 Node 配置与共享上下文 | NODE-001 | PLANNED |
| NODE-003 | 组合现有 Server / Router 为 Node 模式 | NODE-001, NODE-002 | PLANNED |

完成本类别后，BurnCloud 应能够以明确的 Node Profile 启动和关闭，但还不要求自动准备或运行本地模型。