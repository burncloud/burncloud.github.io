---
title: "UI 状态与业务真相"
slug: /architecture/reusable-rules/ui/state/
---

# UI 状态与业务真相

UI 必须区分三类状态：

```text
Server Truth       服务端最终业务事实
UI Projection      排序、格式化和展示标签
Ephemeral UI State 对话框、筛选、选中项和输入草稿
```

余额、Paid、Settled、READY、Healthy、权限和 Revenue 只能来自对应业务 Owner。写操作成功后，关键事实应重新读取，不能只靠本地乐观修改宣布完成。

每个页面根据实际情况覆盖：Loading、Success、Empty、Error、Partial Failure、Forbidden、Unknown 和 Pending。

正确：付款请求返回后重新读取 Invoice，由 Billing 返回 `Paid`。  
错误：看到 HTTP 200 就在客户端把 Invoice 改成 `Paid`。
