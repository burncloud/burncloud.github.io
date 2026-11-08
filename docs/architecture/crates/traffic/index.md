---
title: "traffic"
slug: /architecture/crates/traffic/
---

# `crates/traffic`

继承 [基础规则](/architecture/foundation/)。

本页是 Traffic 的目录规则。下面的目录是职责划分，不是 `burncloud/burncloud` main 的逐文件清单。当前 main 上的数据面实现在 `crates/traffic/router`，和下面的 gateway、routing、execution 等规则目录不是同名对照。

## 负责什么

负责请求进入之后的数据面：Gateway、Routing、Dispatch、Execution、Rate Limit、Retry、Failover、Streaming。也就是请求如何被调度和交付。

## 不负责什么

不拥有 Provider 主数据，不拥有用户身份，不负责价格、账单和结算，不负责审计证明规则本身。

## 依赖

可以依赖 `kernel`，并通过 `identity`、`supply`、`commerce`、`trust` 的公开契约获取身份上下文、可用供给和其他协作事实。需要通用基础设施时使用 `platform` 的公开能力。

禁止直接访问其他领域的表、Repository、Credential 存储或内部 Adapter。禁止形成 `traffic` 与 `commerce` 的循环依赖。

## 目录

Gateway、Routing、Execution、Failover 等只有在形成真实独立职责后才向下拆分。“谁是 Provider”与“请求怎么执行”必须分清归属。

```text
traffic/
├── gateway/
├── routing/
├── execution/
├── rate_limit/
└── failover/
```

## 代码要求

入口、选择、执行和返回保持清楚分段。请求路径要显式表达超时、取消、重试和失败传播。不得用隐藏副作用改变 Commerce、Identity 等其他领域状态。

## 可复用规则

Rust 代码引用 [Rust 通用规则](/architecture/reusable-rules/rust/)。Streaming、HTTP API、P2P 等能力按实际引用对应规则。测试由具体子目录决定。

## 测试

重点覆盖路由选择、失败切换、超时、取消、重试边界、流式中断和无可用供给。

## 正确与错误

正确：Traffic 通过 `supply` 的公开契约查询可用 Provider，使用候选执行自己的路由策略，执行后发布用量事实。

错误：

```text
traffic 直接读取 supply/provider 数据表       ❌
traffic 直接修改 billing balance              ❌
traffic 把 Provider Credential 复制到自己维护  ❌
Traffic 复制 Commerce 的价格公式后自行扣费     ❌
```

## 子目录

- [Gateway](./gateway.md)
- [Routing](./routing.md)
- [Execution](./execution.md)
- [Rate Limit](./rate-limit.md)
- [Failover](./failover.md)
