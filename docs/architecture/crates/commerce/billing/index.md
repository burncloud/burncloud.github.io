---
title: "commerce / billing"
slug: /architecture/crates/commerce/billing/
---

# Billing

继承 [Commerce规则](../index.md)。

## 独有职责

根据确认Usage和Price形成账单事实，管理账单状态与调整。不负责执行请求或管理用户身份。

## 独有要求

- 同一计费事实只能进入一次账单。
- 账单状态只能通过明确业务动作改变。
- 已结算账单不能直接覆盖金额。
- 修正使用Adjustment或其他明确记录，不抹掉历史。

## 目录

```text
billing/
├── invoice/
├── adjustment/
└── statement/
```

## 子目录

- [Invoice](./invoice/index.md)

正确：用新的调整记录修正错误账单。  
错误：直接修改已结算账单金额而不留痕迹。
