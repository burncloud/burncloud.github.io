---
title: "commerce / balance"
slug: /architecture/crates/commerce/balance/
---

# Balance

继承 [Commerce规则](./index.md)。

## 独有职责

维护预付、赠送、冻结、信用等可用资金状态，并给出消费授权结论。

## 独有要求

- 每次余额变化有唯一业务原因和关联标识。
- 并发修改不能造成未授权负数或重复扣减。
- 查询余额与改变余额是不同能力。
- 其他领域只能通过公开契约申请授权或变更。

正确：Traffic申请消费授权，Balance返回明确结果。  
错误：Traffic直接执行 `UPDATE balances`。
