---
title: "traffic / gateway"
slug: /architecture/crates/traffic/gateway/
---

# Gateway

继承 [Traffic规则](./index.md)，并按入口类型引用 [HTTP API](../../reusable-rules/http-api.md)或 [Streaming](../../reusable-rules/streaming.md)规则。

## 独有职责

接收数据面请求、识别协议、建立请求上下文并进入 Traffic 流程。不负责 Provider 最终选择和价格计算。

## 独有要求

- 原始协议请求与内部标准请求分开。
- RequestId、Tenant身份和取消信号贯穿后续流程。
- 未知协议、无效输入和超限请求在边界处明确拒绝。

正确：Gateway 完成协议准入后交给 Routing。  
错误：Gateway 同时查询价格、选择 Provider、写账单。
