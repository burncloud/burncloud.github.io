---
title: "UI 共享组件"
slug: /architecture/reusable-rules/ui/shared-components/
---

# UI 共享组件

`shared/` 采用默认拒绝原则，只保存没有业务身份的视觉和交互原语，例如 Button、Card、Badge、Dialog、Input、Tabs、Tooltip、Skeleton 和通用状态外壳。

不能因为两个页面长得相似，就共享带有 Billing、Customer、Provider 等业务含义的组件。

判断方法：删除任意一个业务域后，这个组件是否仍有自然含义？如果没有，就应留在业务页面内部。

```text
shared/customer_balance.rs                       错误
domains/admin/customers/components/balance.rs    正确
```

`shared/` 禁止反向依赖具体业务页面或领域。
