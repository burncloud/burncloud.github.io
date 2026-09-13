---
title: "traffic"
slug: /architecture/crates/traffic/
---

# `crates/traffic`

## 负责什么

负责请求进入、路由、调度、执行、限流、Failover、Retry 和 Streaming 返回。

## 不负责什么

不拥有用户身份、Provider目录、价格、账单或审计证明规则。

## 依赖

通过 Identity、Supply、Commerce、Trust 的公开契约协作；不能进入它们的内部实现或数据表。

## 目录

```text
traffic/
├── gateway/
├── routing/
├── execution/
├── rate_limit/
└── failover/
```

## 代码与测试

入口、选择、执行和返回保持清楚分段；测试由具体子 crate 决定，并按需引用 Streaming 规则。

## 正确与错误

正确：Traffic 使用 Supply 候选并执行自己的路由策略。  
错误：Traffic 复制 Commerce 的价格公式后自行扣费。

## 子目录

- [Gateway](./gateway.md)
- [Routing](./routing.md)
- [Execution](./execution.md)
- [Rate Limit](./rate-limit.md)
- [Failover](./failover.md)
