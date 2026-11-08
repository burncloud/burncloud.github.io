---
title: "commerce"
slug: /architecture/crates/commerce/
---

# `crates/commerce`

继承 [基础规则](/architecture/foundation/)。

本页是 Commerce 的目录规则。下面的目录是职责划分，不是 `burncloud/burncloud` main 的逐文件清单。

## 负责什么

负责 Metering、Quota、Pricing、Balance、Billing、Ledger、Invoice、Settlement 等“用了多少、多少钱、怎样记账和结算”。

## 不负责什么

不负责用户认证，不验证用户密码，不负责 Provider 供给，不选择 Provider，不执行模型请求，不负责请求路由，也不决定证据是否真实。

## 依赖

默认依赖 `kernel`；需要身份上下文时只使用 `identity` 的公开契约，需要通用基础设施时使用 `platform` 的公开能力。通过公开契约接收 Identity 主体和 Traffic 执行事实。流量结果优先通过公开事件或契约进入 Commerce。

禁止直接读取 `traffic`、`supply`、`identity` 的内部表、Repository 或 Adapter。禁止把账务状态交给其他领域直接修改。禁止形成让 Traffic 直接修改余额的依赖。

## 目录

Metering、Pricing、Balance、Billing、Settlement 只有在真实目录和职责确认后才逐级建立规则，不在本页提前复制各自细节。

```text
commerce/
├── metering/
├── pricing/
├── balance/
├── billing/
└── settlement/
```

## 代码要求

- 所有金额必须使用统一的 `Money` 类型或 Commerce 明确定义的等价金额值对象，禁止业务代码直接用裸浮点数表示金额。
- 价格精度、舍入、单位和币种规则必须由 Commerce 统一定义，不能由调用方自行决定。
- 账务状态必须通过所属业务能力修改，不允许跨模块直接更新余额、账单或结算记录。
- 每个财务事实只有一个 Owner。

## 可复用规则

Rust 代码引用 [Rust 通用规则](/architecture/reusable-rules/rust/)。涉及 Database、Migration 等能力时按实际引用对应规则。

## 测试

涉及金额、额度、计量、账单和结算的行为必须覆盖边界值、重复处理、精度和状态变化。测试聚焦自己的金额和状态不变量。

## 正确与错误

正确：Traffic 提交实际 Token 或发布用量事实，Commerce 决定如何计量和收费。`Money` 带明确币种和精度后进入 Pricing 或 Billing。

错误：

```text
f64 直接保存金额                         ❌
traffic 直接 UPDATE balance               ❌
HTTP Handler 自己计算最终账单价格          ❌
Traffic、Server、UI 各自维护一套价格算法    ❌
```

## 子目录

- [Metering](./metering.md)
- [Pricing](./pricing.md)
- [Balance](./balance.md)
- [Billing](./billing/index.md)
- [Settlement](./settlement.md)
