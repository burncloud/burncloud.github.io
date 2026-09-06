---
title: "Code Ownership and Modification Scope"
slug: /burncloud-ui/architecture/code-ownership/
---

# Code Ownership and Modification Scope

所有 UI Task Contract 必须声明 **Allowed Paths / Conditional Paths / Forbidden Paths**。

## Modification Levels

| Level | 区域 | 默认权限 |
|---|---|---|
| L1 | `domains/<role>/<page>/**` | 页面 Issue 可修改 |
| L2 | role-level `api/<role>/**`, `navigation.rs`, `routes.rs` | Issue 明确声明后可修改 |
| L3 | `shared/**`, `i18n/**`, `design/**` | 必须说明跨页面复用理由 |
| L4 | `app/router/**`, `auth/**`, `api/client.rs`, global shell/platform boundary | 需要独立 Architecture/Foundation Issue |

## Example: UI-BUYER-006

Default Allowed：

```text
crates/client/src/domains/buyer/billing/**
crates/client/src/api/buyer/billing.rs
相关页面测试
```

Conditional：

```text
shared/ui/**
shared/states/**
i18n/locales/**
```

Forbidden unless separately authorized：

```text
app/router/**
auth/**
design/**
domains/admin/**
domains/supplier/**
api/admin/**
api/supplier/**
database/**
router/**
server/**
billing core/**
```

## Protected Architecture Zone

默认 L4：

```text
crates/client/src/app/**
crates/client/src/auth/**
crates/client/src/api/client.rs
crates/client/src/design/**
crates/client/src/shared/layout/**
```

发现页面必须修改 Protected Zone 时，正确动作是 STOP + Architecture Dependency，不是扩大当前 PR。