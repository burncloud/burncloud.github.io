---
title: "identity"
slug: /architecture/crates/identity/
---

# `crates/identity`

## 负责什么

负责 User、Account、Organization、Tenant、Authentication、Authorization、Role、Permission 和用户 API Key。

## 不负责什么

不负责 Provider Credential、请求路由、价格、账单和审计证明。

## 依赖

可以依赖 Kernel 和所需 Platform Port；其他领域只能通过 Identity 公开契约取得身份与权限结论。

## 目录

```text
identity/
├── user/
├── organization/
├── authentication/
├── authorization/
└── api_key/
```

## 代码与测试

密码、Session、角色和权限判断留在 Identity；测试聚焦身份、隔离、授权和敏感数据。

## 正确与错误

正确：Traffic 询问 Identity 某 Credential 对应哪个 Tenant。  
错误：Traffic 自己读取用户表并重新计算权限。
