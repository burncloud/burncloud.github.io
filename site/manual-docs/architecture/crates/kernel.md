---
title: "Kernel规则"
slug: /architecture/crates/kernel/
sidebar_label: "Kernel"
---

# Kernel 总体规则

继承：[基础规则](/architecture/base-rules/)。

## 1. 负责什么

`kernel` 只负责全局最小、稳定、与具体业务无关的基础类型和契约。

## 2. 不负责什么

不放用户、Provider、Routing、Billing、Audit 等业务规则；不放数据库、网络、缓存等基础设施实现；不成为新的 `common`。

## 3. 可以依赖什么

只依赖语言标准能力和确有必要的通用第三方能力。

## 4. 禁止依赖什么

禁止依赖 `identity`、`supply`、`traffic`、`commerce`、`trust`、`platform`、`interfaces`。

## 5. 目录和文件

只按真实的最小职责拆分。某个类型如果只有一个领域使用，应留在该领域，不上提到 `kernel`。

## 6. 代码要求

API 必须极小、稳定、业务中立；新增内容必须能说明为什么多个领域都需要它。

## 7. 可复用规则

Rust 代码引用 [Rust通用规则](/architecture/reusable/rust/)。

## 8. 独有测试

重点验证基础类型的不变量和公开契约；不得通过测试引入业务依赖。

## 9. 正确示例

```text
多个领域共同使用、没有业务归属的稳定 Value Type → kernel
```

## 10. 错误示例

```text
BillingPrice → kernel     ❌
ProviderConfig → kernel   ❌
“暂时不知道放哪” → kernel ❌
```