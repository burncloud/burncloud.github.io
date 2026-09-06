---
title: "API Boundary"
slug: /burncloud-ui/architecture/api-boundary/
---

# API Boundary

页面不能直接拥有 HTTP 细节。

正确链路：

```text
Page
 ↓
Action
 ↓
Typed API module
 ↓
Management API
 ↓
Backend Authorization
```

禁止：

```text
page.rs → reqwest
page.rs → "/console/api/..."
page.rs → Database
page.rs → Service
page.rs → Provider
```

## Target API Layout

```text
api/
├── client.rs
├── error.rs
├── request.rs
├── response.rs
├── buyer/
├── supplier/
├── admin/
└── shared/
```

业务 API 必须按角色语义分离。即使底层数据库相同，Buyer/Admin 的 DTO、授权和数据暴露范围仍可不同。

API URL、认证 header、错误解析、retry policy、transport policy 应集中管理，不能散落页面。