---
title: "Web UI 依赖规则"
slug: /architecture/crates/interfaces/web-ui/dependencies/
---

# Web UI 依赖规则

允许的主要方向：

```text
app → auth / shared / domains / platform
domains/*/* → api / shared / design / i18n
domains/buyer → api/buyer
domains/supplier → api/supplier
domains/admin → api/admin
shared → design / i18n
api/* → api/client
```

禁止：

```text
shared → domains/*
buyer → supplier/admin private modules
supplier → buyer/admin private modules
admin → buyer/supplier private modules
page → raw HTTP client
page → Database / Repository / Service / Provider
page → environment secret
```

相同 UI 形状不代表相同业务语义。Buyer Billing、Admin Billing 和 Supplier Settlement 默认属于不同页面域；只有没有业务身份的视觉原语才能进入 `shared/`。
