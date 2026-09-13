---
title: "commerce / settlement"
slug: /architecture/crates/commerce/settlement/
---

# Settlement

继承 [Commerce规则](./index.md)。

## 独有职责

把已经确认的账务事实进入客户、供应商或合作方结算过程。

## 独有要求

- 结算对象、周期、币种、汇率版本和金额来源明确。
- 已完成结算不能无记录地重复执行。
- 部分失败必须知道哪些项目已经完成。
- 结算调整不能覆盖原始账务事实。

正确：每次结算有唯一标识和可追溯明细。  
错误：失败重试时把已经结算的项目再次付款。
