---
title: "BurnCloud 规则文档"
slug: /architecture/
sidebar_label: "规则文档"
description: "从基础规则出发，沿 BurnCloud 目标 crates 目录逐级定义代码规则。"
---

# BurnCloud 规则文档

这里只定义规则文档：**不设计 Harness，不建立独立规则数据文件，不讨论自动检查。**

全部规则只有三部分：

```text
规则文档
├── 基础规则
├── 可复用规则
└── Crates 目录规则
```

## 阅读方法

1. 所有代码先遵守[基础规则](./foundation.md)。
2. 根据代码类型选择需要的[可复用规则](./reusable-rules/index.md)。
3. 从 [`crates/` 目录规则](./crates/index.md)进入所属领域。
4. 如果领域下面还有独立职责，继续向下读取。

例如：

```text
commerce/billing/invoice/download

实际规则 = 基础规则
         + Commerce 规则
         + Billing 规则
         + Invoice 规则
         + Download 可复用规则
         + Invoice Download 独有规则
```

## 继承原则

- 上级写共同要求，下级只写新增和不同。
- 同一条规则实际重复两三次后，再提取到最近的共同上级。
- 技术方法可以复用，业务事实必须留在自己的领域。
- 下级可以增加限制，不能悄悄取消上级规则。
- 只有出现独立职责、不同依赖、不同写法或不同测试时，目录规则才继续下钻。

## 唯一规则来源

所有新的架构规则正文都归入本目录。原来的 `/burncloud-ui/architecture/` URL 继续保留，但只作为兼容入口；其中的通用 UI 规则已经进入[可复用 UI 规则](./reusable-rules/ui/index.md)，BurnCloud Web UI 专属规则已经进入 [`interfaces/web-ui`](./crates/interfaces/web-ui/index.md)。

## 八个一级领域

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

这是一套目标目录契约。现有代码迁入该结构时，应通过独立 Issue 逐步完成，不能只修改文档就声称源码已经符合。

> **从基础规则开始，沿目录逐级向下；共同规则只写一次，具体 crate 只写自己的差异。**
