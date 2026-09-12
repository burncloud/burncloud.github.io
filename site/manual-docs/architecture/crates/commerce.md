---
title: "Commerce规则"
slug: /architecture/crates/commerce/
sidebar_label: "Commerce"
---

# Commerce 总体规则

继承：[基础规则](/architecture/base-rules/)。

## 1. 负责什么

负责 Metering、Quota、Pricing、Balance、Billing、Ledger、Invoice、Settlement 等“用了多少、多少钱、怎么记账和结算”的能力。

## 2. 不负责什么

不负责用户认证，不负责 Provider 供给，不负责请求路由和执行，不负责审计证明本身。

## 3. 可以依赖什么

默认依赖 `kernel`；需要身份上下文时只使用 `identity` 的公开契约，需要通用基础设施时使用 `platform` 的公开能力。流量结果优先通过公开事件/契约输入 Commerce。

## 4. 禁止依赖什么

禁止直接读取 `traffic`、`supply`、`identity` 的内部表、Repository 或 Adapter；禁止把账务状态交给其他领域直接修改。

## 5. 目录和文件

Metering、Pricing、Balance、Billing、Settlement 等只有在真实目录和职责确认后才逐级建立规则，不在总体页提前复制各自细节。

## 6. 代码要求

- 所有金额必须使用统一的 `Money` 类型或 Commerce 明确定义的等价金额值对象，禁止业务代码直接用裸浮点数表示金额。
- 价格精度、舍入和币种规则必须由 Commerce 统一定义，不能由调用方自行决定。
- 账务状态必须通过所属业务能力修改，不允许跨模块直接更新余额、账单或结算记录。

## 7. 可复用规则

Rust 代码引用 [Rust通用规则](/architecture/reusable/rust/)；涉及 Database、Migration 等能力时按实际引用对应规则。

## 8. 独有测试

涉及金额、额度、计量、账单和结算的行为必须覆盖边界值、重复处理、精度和状态变化。

## 9. 正确示例

```text
Traffic 发布用量事实 → Commerce Metering 处理
Money + 明确币种/精度 → Pricing/Billing
```

## 10. 错误示例

```text
f64 直接保存金额                         ❌
traffic 直接 UPDATE balance               ❌
HTTP Handler 自己计算最终账单价格          ❌
```