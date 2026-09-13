---
title: "UI 测试"
slug: /architecture/reusable-rules/ui/testing/
---

# UI 测试

UI 测试只验证 UI 应该负责的事情，不复制后端业务测试。

每个页面至少验证 Loading、Success、Empty 和 Error。存在权限、部分失败或异步状态时，再验证 Forbidden、Partial Failure、Unknown 和 Pending。

受保护页面根据实际能力验证：未登录、错误 Workspace、缺少 Capability、服务端 403 和安全的登录返回路径。

关键测试必须证明失败状态不会伪装成成功，例如：

```text
Unknown != 0
Spawned != READY
HTTP 200 != Settled/Paid
Hidden Control != Authorization
```

发布前还应验证键盘与焦点、窄屏、主要语言文字溢出，以及所支持平台上的一致行为。
