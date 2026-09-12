---
title: "Traffic规则"
slug: /architecture/crates/traffic/
sidebar_label: "Traffic"
---

# Traffic 总体规则

继承：[基础规则](/architecture/base-rules/)。

## 1. 负责什么

负责请求入口后的数据面：Gateway、Routing、Dispatch、Execution、Rate Limit、Retry、Failover、Streaming 等“请求如何被调度和交付”。

## 2. 不负责什么

不拥有 Provider 主数据，不拥有用户身份，不负责价格、账单和结算，不负责审计合规规则本身。

## 3. 可以依赖什么

可以依赖 `kernel`，并通过 `identity`、`supply` 的公开契约获取身份上下文和可用供给；需要通用基础设施时使用 `platform` 的公开能力。

## 4. 禁止依赖什么

禁止直接访问其他领域的表、Repository、Credential 存储或内部 Adapter；禁止形成 `traffic ↔ commerce` 等循环依赖。

## 5. 目录和文件

Gateway、Routing、Execution、Failover 等只有在形成真实独立职责后才向下拆分；“谁是 Provider”与“请求怎么执行”必须分清归属。

## 6. 代码要求

请求路径要显式表达超时、取消、重试和失败传播；不得用隐藏副作用改变 Commerce、Identity 等其他领域状态。

## 7. 可复用规则

Rust 代码引用 [Rust通用规则](/architecture/reusable/rust/)；Streaming、HTTP API、P2P 等能力按实际引用对应规则。

## 8. 独有测试

重点覆盖路由选择、失败切换、超时、取消、重试边界、流式中断和无可用供给等行为。

## 9. 正确示例

```text
traffic → supply::public 查询可用 Provider
traffic 执行请求后发布 UsageRecorded 事件
```

## 10. 错误示例

```text
traffic 直接读取 supply/provider 数据表       ❌
traffic 直接修改 billing balance              ❌
traffic 把 Provider Credential 复制到自己维护  ❌
```