---
title: "UI规则"
slug: /architecture/reusable/ui/
sidebar_label: "UI规则"
---

# UI 规则

适用于所有 UI 功能；继承 [基础规则](/architecture/base-rules/)。

- 页面必须明确处理 Loading、Empty、Error 和正常状态。
- 组件职责要单一；业务规则不应藏在纯展示组件中。
- UI 只通过公开接口使用业务能力，不直接访问数据库或业务内部实现。
- 权限控制不能只依赖“隐藏按钮”；服务端仍必须执行真实授权。

具体页面只补充自己的交互和业务限制。