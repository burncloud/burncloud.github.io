---
title: "interfaces / websocket"
slug: /architecture/crates/interfaces/websocket/
---

# WebSocket

继承 [Interfaces规则](./index.md)，流式消息同时引用 [Streaming规则](../../reusable-rules/streaming.md)。

## 独有职责

负责连接、消息协议、订阅和实时输出边界。

## 独有要求

- 连接身份和每次消息权限都要明确。
- 消息类型和版本不能靠自由字符串猜测。
- 断开、取消和重连不应留下永久任务。
- 慢客户端不能无限占用内存。

正确：每条消息通过明确类型进入公开用例。  
错误：连接建立一次后永久相信所有后续消息。
