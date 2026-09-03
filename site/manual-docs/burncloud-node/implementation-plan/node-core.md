---
title: "类别一：Node Core"
slug: /burncloud-node/implementation-plan/node-core/
---

# 类别一：Node Core

Node Core 只负责把现有 BurnCloud 能力组合成一个 Node 运行形态，不重新实现已有业务组件。

同时，Node 产品文档已经把 Local API Gateway 与 Protocol Routing 定义为核心用户能力，因此 Node Core 类别必须有一条独立 Compatibility Gate，证明 Node 模式继续正确复用 existing Server / Router / Raw Proxy / Translator，而不是仅凭“代码已经存在”默认它不会回归。

## Issue

| ID | 功能 | 依赖 | 状态 |
|---|---|---|---|
| [NODE-001](./node-001) | 建立 Node 启动入口与生命周期 | 无 | PLANNED |
| [NODE-002](./node-002) | 建立 Node 配置与共享上下文 | NODE-001 | PLANNED |
| [NODE-003](./node-003) | 组合现有 Server / Router 为 Node 模式 | NODE-001, NODE-002 | PLANNED |
| [NODE-004](./node-004) | Gateway / Protocol Routing Compatibility Gate | NODE-003 | PLANNED |

NODE-004 **不是**第二个 Gateway / Router 的实现 Issue。它只负责把以下已批准产品合同变成可验收的 compatibility matrix：

```text
URL / Path → Protocol Detection
model_id   → existing ModelRouter
same protocol      → Raw Proxy First
different protocol → Protocol Translator
```

完成本类别后，BurnCloud 应能够以明确的 Node Profile 启动和关闭，并证明 Node 模式继续使用统一数据面入口与协议边界；本类别仍不要求自动准备或运行本地模型。
