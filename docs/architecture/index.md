---
title: "工程架构"
slug: /architecture/
sidebar_label: "工程架构（必读）"
description: "BurnCloud 仓库级工程架构规则：领域归属、目录边界、依赖治理与代码 Ownership。"
---

# BurnCloud 工程架构

BurnCloud 的工程架构首先解决四个问题：

> **代码属于谁？负责什么？边界在哪里？其他模块应该如何调用它？**

目录只是架构的外在表现。真正长期稳定的是 **Ownership、职责边界和依赖方向**。

BurnCloud 当前采用以下最小原则：

> **领域决定归属。**  
> **功能决定目录。**  
> **复杂度决定层级。**  
> **接口决定边界。**

## `crates/` 一级领域

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

这些目录不是为了枚举未来所有功能，而是为了提供长期稳定的“归属空间”。普通新功能默认向下生长，不直接增加 `crates/` 一级目录。

## 用公司的部门来理解

可以把 BurnCloud 看成一家大型公司，每个一级目录对应一个长期存在的“一级部门”。

| 目录 | 公司部门类比 | 核心问题 |
| --- | --- | --- |
| `kernel` | 公司章程 / 董事会基本制度 | 全公司共同遵守的最小规则是什么？ |
| `identity` | 人力资源部 + 门禁权限中心 | 谁在公司里？属于哪个组织？有什么权限？ |
| `supply` | 采购部 + 供应链部 | 公司有哪些可用资源？由谁提供？通过什么渠道获得？ |
| `traffic` | 生产调度中心 + 运营指挥中心 | 一个订单/请求应该发给谁、怎么执行、失败后怎么办？ |
| `commerce` | 财务部 + 商务结算部 | 用了多少？多少钱？怎么记账和结算？ |
| `trust` | 法务部 + 审计部 + 风控部 | 事情是否真实、合规、可追溯、可证明？ |
| `platform` | IT 基础设施部 + 运维平台部 | 数据库、网络、缓存、监控等公共基础设施如何提供？ |
| `interfaces` | 前台 / 客服窗口 / 对外接待部门 | 外部客户和系统通过什么入口与 BurnCloud 交互？ |

这个类比只用于理解“职责归属”，不是要求软件照搬企业行政层级。

例如：

- `commerce/billing` 相当于财务部里的账单职能；
- `traffic/routing` 相当于调度中心里的路由决策职能；
- `supply/provider` 相当于供应链里的供应商管理；
- `identity/auth` 相当于门禁与身份认证；
- `platform/networking` 相当于公司的网络基础设施团队。

一个部门可以使用另一个部门提供的能力，但不能直接进入对方内部修改实现。软件里对应的规则就是：**跨领域通过公开接口协作，不穿透内部边界。**

## 为什么不再按 Service / Database 分目录

技术分层回答的是“代码怎么实现”，而领域分包先回答“代码属于哪个业务”。

例如 Billing 不应该被拆成：

```text
service/billing
database/billing
server/billing
common/pricing
```

而应该先有唯一业务归属：

```text
commerce/
└── billing/
```

Billing 内部需要数据库、缓存或 HTTP 时，再在自己的边界内组织实现。

## 文档

- [目录规则](/architecture/directory-rules/)：定义目录归属、增长、测试和跨领域边界。

后续依赖规则、Code Ownership、crate 拆分标准等仓库级规范都放在本栏目。