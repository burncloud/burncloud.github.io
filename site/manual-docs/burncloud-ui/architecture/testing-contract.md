---
title: "Testing Contract"
slug: /burncloud-ui/architecture/testing-contract/
---

# Testing Contract

每个页面至少覆盖：

```text
Loading
Success
Empty
Error
Partial Failure（适用时）
Forbidden
Unknown / Pending（适用时）
```

受保护页面还必须覆盖：

```text
unauthenticated
wrong workspace
missing capability
backend 403
safe return_to
```

关键状态必须验证不会伪造成成功：

```text
Unknown != 0
Spawned != READY
HTTP 200 != Settled/Paid
Hidden control != authorization
```

Final Quality Gate 必须覆盖 keyboard/focus、窄屏、中文/英文溢出、Web/Desktop/LiveView，以及 `/console/api/*` / `/console/internal/*` 不被 UI catch-all 吞掉。