---
title: "platform"
slug: /architecture/crates/platform/
---

# `crates/platform`

## 负责什么

负责 Database、Storage、Cache、Networking、Messaging、Configuration、Observability 和 Lifecycle 等通用技术能力。

## 不负责什么

不拥有 User、Provider、Routing、Billing、Invoice 等业务决策。

## 依赖

可以依赖 Kernel。业务领域通过 Port 使用 Platform Adapter；Platform 不反向依赖具体业务实现。

## 目录

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

## 代码与测试

每种基础设施使用自己的可复用规则和 Adapter 测试，不把业务判断埋进技术实现。

## 正确与错误

正确：Platform 提供存储和消息能力。  
错误：Platform 根据客户等级决定是否允许扣费。
