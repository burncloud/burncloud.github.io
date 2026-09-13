---
title: "kernel"
slug: /architecture/crates/kernel/
---

# `crates/kernel`

## 负责什么

保存全系统最小、最稳定、没有单一业务领域归属的基础语义，例如强类型 ID、Money、Currency 和时间抽象。

## 不负责什么

不保存 User、Provider、Route、Invoice、Billing、Audit 等具体业务；不成为新的 `common` 或 `utils`。

## 依赖

只能依赖 Rust 标准库和极少数经过批准的基础库，不能依赖其他 BurnCloud 业务领域。

## 目录

按稳定基础概念组织，例如：

```text
kernel/
├── identifiers/
├── money/
├── time/
└── error/
```

## 代码与测试

类型必须小、无 IO、无数据库、无网络副作用。测试聚焦转换、边界值和类型不变量。

## 正确与错误

正确：`TenantId`、`Money`。  
错误：`BillingService`、`ProviderRepository`、万能 `helpers.rs`。
