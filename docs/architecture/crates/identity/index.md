---
title: "identity"
slug: /architecture/crates/identity/
---

# `crates/identity`

继承 [基础规则](/architecture/foundation/)。

本页是 Identity 的目录规则。下面的目录是职责划分，不是 `burncloud/burncloud` main 的逐文件清单。

## 负责什么

负责 User、Account、Organization、Tenant、Authentication、Authorization、Role、Permission、身份关系和用户 API Key：谁在使用系统，拥有什么权限。

## 不负责什么

不负责模型或 Provider 供给，不负责 Provider Credential，不负责请求路由和执行，不负责价格、账单、结算，不负责审计证明。

## 依赖

默认依赖 `kernel`；需要通用基础设施时只使用 `platform` 的公开能力。其他领域只能通过 Identity 公开契约取得身份与权限结论。跨业务领域依赖必须在更下级规则中明确说明。

禁止依赖其他领域内部实现、数据库表、Repository 或 Adapter。禁止通过 `interfaces` 反向获取业务能力。

## 目录

按身份领域的真实功能向下组织。认证、授权、用户、组织等只有在形成独立职责后才拆分。

```text
identity/
├── user/
├── organization/
├── authentication/
├── authorization/
└── api_key/
```

## 代码要求

密码、Session、角色和权限判断留在 Identity。身份判断和权限判断必须有唯一业务归属，不要把权限规则散落到 HTTP Handler、UI 或其他领域。

## 可复用规则

Rust 代码引用 [Rust 通用规则](/architecture/reusable-rules/rust/)。涉及数据库或 HTTP 时按实际需要引用对应规则。

## 测试

必须覆盖授权边界、Tenant 隔离、无权限访问、身份状态变化和敏感数据。

## 正确与错误

正确：Traffic 通过 Identity 的公开能力询问“当前用户是否有权操作该 Tenant”，或询问某 Credential 对应哪个 Tenant。

错误：

```text
HTTP Handler 自己复制一套角色判断      ❌
commerce 直接查询 identity 的用户表    ❌
UI 隐藏按钮就当作完成授权              ❌
Traffic 自己读取用户表并重新计算权限    ❌
```

## 子目录

当前没有已单独成页的 Identity 子规则。下级职责出现独立边界后再增加页面，不在这里预写空页。
