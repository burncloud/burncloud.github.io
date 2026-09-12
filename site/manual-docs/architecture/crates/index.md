---
title: "Crates目录规则"
slug: /architecture/crates/
sidebar_label: "3. Crates目录规则"
description: "BurnCloud crates/ 一级领域职责与逐级规则入口。"
---

# Crates 目录规则

`crates/` 第一层只定义长期稳定的领域归属：

```text
crates/
├── kernel/
├── identity/
├── supply/
├── traffic/
├── commerce/
├── trust/
├── platform/
└── interfaces/
```

| 目录 | 核心职责 |
| --- | --- |
| `kernel` | 全局最小类型与契约 |
| `identity` | 用户、组织、Tenant、认证与授权 |
| `supply` | 模型、Provider、Channel、Credential、供给能力 |
| `traffic` | 请求、路由、调度、执行与失败恢复 |
| `commerce` | 用量、额度、价格、账单与结算 |
| `trust` | 审计、证明、合规与风控 |
| `platform` | 通用数据库、缓存、网络、消息、配置、观测等基础设施能力 |
| `interfaces` | HTTP、UI、CLI、SDK、Webhook 等对外入口 |

这些页面只写一级目录自己的新增规则，全部继承 [基础规则](/architecture/base-rules/)。

下一层只有在真实代码目录和职责确认后才创建。例如 Commerce 的 Metering、Pricing、Billing 等，必须先与实际目录一致，再逐级补规则；不在本页提前虚构未来子目录。