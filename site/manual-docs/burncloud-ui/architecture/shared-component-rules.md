---
title: "Shared Component Rules"
slug: /burncloud-ui/architecture/shared-component-rules/
---

# Shared Component Rules

`shared/` 是最容易腐化架构的目录，因此采用 fail-closed 原则。

允许：

```text
Button
Card
Badge
Table shell
Dialog
Input
Select
Tabs
Tooltip
Skeleton
Loading / Empty / Error primitives
Console layout primitives
```

不允许因为“两个页面都用了”就共享业务组件。

例如：

```text
shared/customer_balance.rs       BAD
domains/admin/customers/components/balance.rs GOOD
```

判断标准：删除 Buyer/Supplier/Admin 其中一个角色后，这个组件是否仍然具有自然、无业务身份的含义？如果答案是否，则它不属于 shared。

`shared/` 禁止 import `domains/*`。