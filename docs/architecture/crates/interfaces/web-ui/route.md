---
title: "Web UI Route"
slug: /architecture/crates/interfaces/web-ui/route/
---

# Web UI Route

Canonical Namespace：

```text
PUBLIC          /  /login  /register
DATA PLANE      /v1/*
MANAGEMENT UI   /console/buyer/*  /console/supplier/*  /console/admin/*
MANAGEMENT API  /console/api/*  /console/internal/*
TRANSPORT       /ws
HEALTH          /health
```

需要 Authentication、Role、Tenant、Capability 或 Admin Authority 的 Production UI 必须位于 `/console/*`。

Production Route Definition 只能有一个事实来源，例如 `app/router/routes.rs`。Web、Desktop 和 LiveView 只能消费它，不能维护第二份页面列表。

`/console/api/*` 与 `/console/internal/*` 属于后端，UI Catch-all 不能吞掉。旧路由只能作为明确授权、无业务逻辑、限期删除的 Redirect。
