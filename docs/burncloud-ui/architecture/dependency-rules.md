---
title: "Dependency Rules"
slug: /burncloud-ui/architecture/dependency-rules/
---

# Dependency Rules

依赖方向必须单向、可解释、可被 CI 检查。

## Allowed

```text
app → auth/shared/domains/platform
domains/* → api/shared/design/i18n
domains/buyer → api/buyer
domains/supplier → api/supplier
domains/admin → api/admin
shared → design/i18n
api/* → api/client
```

## Forbidden

```text
shared → domains/*
buyer → supplier/admin
supplier → buyer/admin
admin → buyer/supplier private modules
page → reqwest/raw HTTP client
page → database/service/router/provider crates
page → environment secret
```

如果两个角色需要相同概念，先判断它是否真的具有相同业务语义。相同 UI 形状不代表相同 Domain。

例如：

```text
Buyer Billing != Admin Billing
Buyer Logs    != Admin Logs
Supplier Settlements != Admin Settlements
```

只有无业务身份的视觉/交互 primitive 才能进入 `shared/`。