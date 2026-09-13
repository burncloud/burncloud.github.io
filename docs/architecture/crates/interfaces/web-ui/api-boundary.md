---
title: "Web UI API Boundary"
slug: /architecture/crates/interfaces/web-ui/api-boundary/
---

# Web UI API Boundary

页面不能直接拥有 HTTP 细节。正确链路是：

```text
Page → Action → Typed API → Management API → Backend Authorization
```

目标结构：

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

API URL、认证 Header、错误解析、Retry 和 Transport Policy 集中管理，不能散落在页面。

Buyer、Supplier、Admin 的 DTO、授权和数据暴露范围可以不同，即使它们最终读取同一业务领域。

正确：`page.rs` 调用 `api::buyer::billing::get_invoice()`。  
错误：`page.rs` 创建 `reqwest::Client` 并拼接 `/console/api/...`。
