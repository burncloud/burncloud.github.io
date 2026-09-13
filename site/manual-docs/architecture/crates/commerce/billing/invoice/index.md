---
title: "commerce / billing / invoice"
slug: /architecture/crates/commerce/billing/invoice/
---

# Invoice

继承 [Billing规则](../index.md)。

## 独有职责

负责Invoice编号、开具、作废、状态和Invoice文档身份。

## 独有要求

- Invoice编号必须唯一。
- 已开具Invoice不能直接删除；需要时使用作废状态。
- Invoice金额来自Billing事实，不能由下载或UI重新计算。
- 文档与Invoice身份绑定，不能通过任意路径访问。

## 子目录

- [Invoice Download](./download.md)

正确：作废保留原Invoice和操作记录。  
错误：开具后为了修正内容直接删除原记录。
