---
title: "commerce / pricing"
slug: /architecture/crates/commerce/pricing/
---

# Pricing

继承 [Commerce规则](./index.md)。

## 独有职责

根据模型、用量、价格表和有效政策计算价格。

## 独有要求

- 使用Money和明确精度，禁止浮点随意计算。
- 价格版本、生效时间、币种和折扣来源必须可说明。
- 同一请求使用已经确定的价格版本，不在流程中途悄悄改变。
- Pricing只计算价格，不直接执行结算。

正确：输入Usage和PriceBook，输出可追溯Quote。  
错误：从UI传入最终金额并直接相信。
