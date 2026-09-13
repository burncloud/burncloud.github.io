---
title: "Web UI Authorization"
slug: /architecture/crates/interfaces/web-ui/authorization/
---

# Web UI Authorization

权限链路：

```text
Request
  ↓
AuthGate
  ↓
WorkspaceGate
  ↓
CapabilityGate
  ↓
Page / API
  ↓
Backend Authorization（最终裁决）
```

URL、侧栏可见、隐藏按钮、Role Switcher、Locale 和 `localStorage` 都不能授予或撤销服务端权限。前端 Capability 只负责显示、禁用、导航和解释。

权限应表达具体能力，例如 `admin.billing.read`、`admin.billing.write`，不能永久把 `Admin` 等同于全部权限。

登录返回地址只允许经过验证的内部 `/console/*` 路径，并且返回后必须重新检查 Workspace 和 Capability，禁止 Open Redirect。
