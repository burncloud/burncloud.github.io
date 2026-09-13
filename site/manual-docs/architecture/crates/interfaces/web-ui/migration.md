---
title: "Web UI 迁移规则"
slug: /architecture/crates/interfaces/web-ui/migration/
---

# Web UI 迁移规则

继承 [Migration 可复用规则](../../../reusable-rules/migration.md)。迁移必须小步完成，不能一次重写 Router、Auth、全部页面、API Client、CSS 和多平台 Adapter。

推荐顺序：

```text
锁定规则
→ 建立唯一 Route 与 Auth/Workspace 边界
→ 建立 Typed API
→ 建立 buyer/supplier/admin 页面域
→ 每个角色迁移一个 Golden Page
→ 逐页迁移
→ 行为一致后删除旧实现
```

每一步必须明确 Allowed、Conditional、Forbidden Paths，保留可回退边界，并验证迁移前后的用户行为。目录整洁本身不是拆 Cargo crate 的理由。
