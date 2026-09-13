---
title: "commerce"
slug: /architecture/crates/commerce/
---

# `crates/commerce`

## 负责什么

负责 Metering、Pricing、Balance、Billing、Ledger、Invoice 和 Settlement。

## 不负责什么

不执行模型请求，不选择 Provider，不验证用户密码，也不决定证据是否真实。

## 依赖

通过公开契约接收 Identity 主体和 Traffic 执行事实；需要基础设施时依赖 Platform Port。

## 目录

```text
commerce/
├── metering/
├── pricing/
├── balance/
├── billing/
└── settlement/
```

## 代码与测试

金额统一使用 Money，精度、单位和币种必须明确。每个财务事实只有一个 Owner，测试聚焦自己的金额和状态不变量。

## 正确与错误

正确：Traffic 提交实际 Token，Commerce 决定如何计量和收费。  
错误：Traffic、Server、UI 各自维护一套价格算法。

## 子目录

- [Metering](./metering.md)
- [Pricing](./pricing.md)
- [Balance](./balance.md)
- [Billing](./billing/index.md)
- [Settlement](./settlement.md)
