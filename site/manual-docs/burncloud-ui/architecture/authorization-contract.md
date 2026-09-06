---
title: "Authorization Contract"
slug: /burncloud-ui/architecture/authorization-contract/
---

# Authorization Contract

权限分四层：

```text
Request
  ↓
AuthGate              Who are you?
  ↓
WorkspaceGate         Buyer / Supplier / Admin authorized?
  ↓
CapabilityGate        Specific action allowed?
  ↓
Page / API
  ↓
Backend Authorization Final authority
```

## Core Rules

```text
URL              != permission
Sidebar visibility != permission
Hidden button     != permission denial
Role Switcher     != permission grant
localStorage      != permission grant
Locale            != permission grant
```

Frontend capability 只用于 UX：显示、禁用、导航和解释。Backend 必须独立验证 identity、role、capability、tenant。

## Capability Direction

未来权限应能表达具体能力，例如：

```text
admin.billing.read
admin.billing.write
admin.customer.read
admin.customer.balance.adjust
admin.settlement.approve
admin.settings.write
```

不得把 `Admin` 永久等价于“所有操作都允许”。

## return_to

登录后只允许返回经过验证的内部 `/console/*` 路径；必须重新验证 workspace/capability，禁止 open redirect。