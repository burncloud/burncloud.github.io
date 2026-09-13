---
title: "commerce / metering"
slug: /architecture/crates/commerce/metering/
---

# Metering

继承 [Commerce规则](./index.md)。

## 独有职责

把Traffic提交的执行事实转换为可计量用量，例如输入、输出、缓存和媒体用量。

## 独有要求

- 原始执行数据与确认后的Usage分开。
- 单位、来源和RequestId必须明确。
- 缺失用量不能暗自当作零。
- 同一执行事实不能重复形成多份用量。

正确：确认Usage后交给Pricing。  
错误：Metering根据销售折扣直接修改客户余额。
