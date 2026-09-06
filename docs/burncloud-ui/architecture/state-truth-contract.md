---
title: "State Truth Contract"
slug: /burncloud-ui/architecture/state-truth-contract/
---

# State Truth Contract

UI 必须明确区分：

```text
Server Truth
UI Projection
Ephemeral UI State
```

### Server Truth

余额、Paid、Settled、READY、Healthy、权限、Revenue、Verified Cost 等只能由 authoritative backend fact 决定。

### UI Projection

格式化、排序、聚合展示、可视化标签可以在客户端完成，但不能产生新的业务真相。

### Ephemeral UI State

Dialog open、filter、selected tab、loading indicator、draft input 等属于纯 UI state。

## Forbidden Truth Promotion

```text
HTTP 200      → Paid          FORBIDDEN
process spawned → READY       FORBIDDEN
missing metric → 0            FORBIDDEN
unknown       → Healthy       FORBIDDEN
client sum    → authoritative Balance  FORBIDDEN
```

写操作成功后，涉及关键真相的页面应重新读取 authoritative state，而不是仅靠本地 optimistic mutation 宣称完成。