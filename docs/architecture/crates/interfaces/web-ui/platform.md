---
title: "Web UI 多平台边界"
slug: /architecture/crates/interfaces/web-ui/platform/
---

# Web UI 多平台边界

Web、Desktop 和 LiveView 可以有不同 Adapter，但产品语义、Route、Authorization 和 API 契约只有一份。

```text
platform/
├── web.rs
├── desktop.rs
└── liveview.rs
```

Platform Adapter 可以处理窗口、Tray、WebSocket Glue、平台生命周期和 Transport Glue；不能复制 Buyer、Supplier、Admin 的业务逻辑。

正确：Desktop Adapter 调用与 Web 相同的 Route 和 API Contract。  
错误：LiveView 单独维护另一套路由、权限和 Billing 状态。
