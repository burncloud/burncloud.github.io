---
title: "Web UI 修改范围"
slug: /architecture/crates/interfaces/web-ui/change-scope/
---

# Web UI 修改范围

继承[基础规则的变更原则](../../../foundation.md#10-变更原则)。每个 UI Issue 必须声明 Allowed、Conditional 和 Forbidden Paths。

| Level | 目录 | 默认规则 |
| --- | --- | --- |
| L1 | `domains/<role>/<page>/**` | 页面 Issue 可以修改 |
| L2 | `api/<role>/**`、该角色的 `navigation.rs` 和 `routes.rs` | Issue 明确声明后可以修改 |
| L3 | `shared/**`、`i18n/**`、`design/**` | 必须说明跨页面复用理由 |
| L4 | `app/router/**`、`auth/**`、`api/client.rs`、全局 Shell 和 Platform Boundary | 必须建立独立 Architecture/Foundation Issue |

Web UI Protected Zone：

```text
crates/client/src/app/**
crates/client/src/auth/**
crates/client/src/api/client.rs
crates/client/src/design/**
crates/client/src/shared/layout/**
```

页面 Issue 如果必须修改 Protected Zone，应该停止并建立依赖 Issue，不能扩大当前 PR。

还必须停止的情况：新增第二套路由、认证或 API 真相；跨 Buyer、Supplier、Admin 私有域依赖；页面直接访问 Database、Service 或 Provider；把 Unknown、Pending、Failed 伪装成 Success；顺手修改无关页面。

正确：Buyer Billing Issue 只修改 Buyer Billing 页面、对应 Typed API 和测试。  
错误：为了完成一个页面，顺便重写 Router、Auth、Design Token 和 Admin Billing。
