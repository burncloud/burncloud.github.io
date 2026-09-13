---
title: "traffic / failover"
slug: /architecture/crates/traffic/failover/
---

# Failover

继承 [Traffic规则](./index.md)。

## 独有职责

决定一次执行失败后是否以及怎样尝试下一个合格候选。

## 独有要求

- 明确哪些错误可以Failover，哪些必须立即返回。
- 重试和切换次数必须有限。
- 已经产生不可重复副作用的请求不能盲目重放。
- 每次尝试的执行事实分别记录，最终只形成正确的业务结果。

正确：可重试的临时Provider错误触发有限切换。  
错误：所有4xx、余额不足和无效输入都不断换Provider重试。
