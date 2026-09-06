---
title: "Platform Contract"
slug: /burncloud-ui/architecture/platform-contract/
---

# Platform Contract

BurnCloud UI 可运行于 Web、Desktop、LiveView，但产品语义和 Route/Auth/API 合同只有一份。

```text
platform/
├── web.rs
├── desktop.rs
└── liveview.rs
```

Platform adapter 可以处理窗口、tray、WebSocket glue、平台生命周期和 transport glue；不得复制 Buyer/Supplier/Admin 业务逻辑。

必须保持：

```text
Web Page Contract
= Desktop Page Contract
= LiveView Page Contract
```

平台差异只能发生在平台能力边界，不得产生第二套路由、权限、Billing 或业务状态真相。