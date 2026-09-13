---
title: "traffic / execution"
slug: /architecture/crates/traffic/execution/
---

# Execution

继承 [Traffic规则](./index.md)，流式调用同时引用 [Streaming规则](../../reusable-rules/streaming.md)。

## 独有职责

把选定路由转换为实际上游调用，处理响应、取消和执行事实。不负责最终账单规则。

## 独有要求

- Provider Adapter 负责协议差异。
- 超时、取消和上游错误保持可区分。
- 执行成功事实与计费成功事实分开。
- 敏感Credential不能进入日志和返回值。

正确：执行完成后把事实交给 Commerce。  
错误：上游返回成功后由 Execution 自己修改客户余额。
