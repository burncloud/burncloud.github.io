---
title: "Platform规则"
slug: /architecture/crates/platform/
sidebar_label: "Platform"
---

# Platform 总体规则

继承：[基础规则](/architecture/base-rules/)。

## 1. 负责什么

负责数据库连接、存储、缓存、网络、消息、配置、观测、下载基础能力、生命周期等不依赖 BurnCloud 业务语义的通用基础设施能力。

## 2. 不负责什么

不决定用户是否有权限，不决定 Provider 是否可售，不决定请求如何路由，不决定余额是否足够，不决定账单如何计算。

## 3. 可以依赖什么

只依赖 `kernel` 和通用外部库；具体基础设施实现之间如需依赖，必须保持职责清晰、无环。

## 4. 禁止依赖什么

禁止依赖 `identity`、`supply`、`traffic`、`commerce`、`trust`、`interfaces` 的业务实现。

## 5. 目录和文件

按 Database、Cache、Networking、Messaging、Configuration、Observability、Lifecycle 等真实基础设施职责向下组织；只有形成独立能力后再拆层级或 crate。

## 6. 代码要求

Platform 提供技术能力，不做业务决策。一个能力如果必须理解 Billing、Provider、Tenant 业务规则才能工作，它通常不属于 Platform。

## 7. 可复用规则

Rust 代码引用 [Rust通用规则](/architecture/reusable/rust/)；Database、Download、Migration、Background Job 等按真实功能引用。

## 8. 独有测试

重点验证基础设施契约、资源释放、异常恢复、并发和边界条件；不能用业务模块作为 Platform 测试依赖。

## 9. 正确示例

```text
提供 Redis Cache 能力 → platform
提供数据库连接池 → platform
```

## 10. 错误示例

```text
“余额不足是否允许调用” → platform    ❌
“某 Provider 应不应该被路由” → platform ❌
platform 反向调用 commerce            ❌
```