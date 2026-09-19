---
title: "interfaces"
slug: /architecture/crates/interfaces/
---

# `crates/interfaces`

## 负责什么

负责 HTTP、Web UI、CLI、WebSocket、SDK 和 Webhook 等外部协议入口。

## 不负责什么

不拥有核心业务规则，不直接成为跨领域数据库入口。

## 依赖

通过业务领域的公开契约调用能力；业务领域不得反向依赖具体 UI、HTTP 或 CLI。

## 目录

```text
interfaces/
├── http/
├── web_ui/
├── cli/
└── websocket/
```

## 代码与测试

负责协议解析、输入验证、调用和输出转换；具体测试由接口类型决定。

## 正确与错误

正确：HTTP Handler 把请求转换成 Commerce Command。  
错误：HTTP Handler 自己计算金额并直接修改账单表。

## 子目录

- [HTTP](./http.md)
- [Web UI](./web-ui/index.md)
- [CLI](./cli.md)
- [WebSocket](./websocket.md)
