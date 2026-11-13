---
title: "platform"
slug: /architecture/crates/platform/
---

# `crates/platform`

继承 [基础规则](/architecture/foundation/)。

本页是 Platform 的目录规则。下面的目录是职责划分，不是 `burncloud/burncloud` main 的逐文件清单。

## 负责什么

负责数据库连接、存储、缓存、网络、消息、配置、观测、下载基础能力、生命周期等不依赖 BurnCloud 业务语义的通用基础设施能力。

## 不负责什么

不决定用户是否有权限，不决定 Provider 是否可售，不决定请求如何路由，不决定余额是否足够，不决定账单如何计算。不拥有 User、Provider、Routing、Billing、Invoice 等业务决策。

## 依赖

只依赖 `kernel` 和通用外部库。具体基础设施实现之间如需依赖，必须保持职责清晰、无环。业务领域通过 Port 使用 Platform Adapter。Platform 不反向依赖具体业务实现。

禁止依赖 `identity`、`supply`、`traffic`、`commerce`、`trust`、`interfaces` 的业务实现。

## 目录

按 Database、Cache、Networking、Messaging、Configuration、Observability、Lifecycle 等真实基础设施职责向下组织。只有形成独立能力后再拆层级或 crate。

```text
platform/
├── database/
├── storage/
├── cache/
├── networking/
├── messaging/
├── configuration/
├── observability/
└── lifecycle/
```

## 代码要求

Platform 提供技术能力，不做业务决策。一个能力如果必须理解 Billing、Provider、Tenant 业务规则才能工作，它通常不属于 Platform。每种基础设施使用自己的可复用规则和 Adapter 测试，不把业务判断埋进技术实现。

## 可复用规则

Rust 代码引用 [Rust 通用规则](/architecture/reusable-rules/rust/)。Database、Download、Migration、Background Job 等按真实功能引用。

## 测试

重点验证基础设施契约、资源释放、异常恢复、并发和边界条件。不能用业务模块作为 Platform 测试依赖。

## 正确与错误

正确：提供 Redis Cache、数据库连接池、存储和消息能力。

错误：

```text
“余额不足是否允许调用” → platform    ❌
“某 Provider 应不应该被路由” → platform ❌
platform 反向调用 commerce            ❌
Platform 根据客户等级决定是否允许扣费  ❌
```

## 已定义子规则

- [Cache 规则](/architecture/crates/platform/cache/)：负责通用缓存技术能力，不拥有被缓存的业务真相。
- [Configuration 规则](/architecture/crates/platform/configuration/)：负责配置来源、合并、解析与技术校验，不拥有业务策略。
