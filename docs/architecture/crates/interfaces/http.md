---
title: "interfaces / http"
slug: /architecture/crates/interfaces/http/
---

# HTTP

继承 [Interfaces规则](./index.md)和 [HTTP API规则](../../reusable-rules/http-api.md)。

## 独有职责

提供HTTP路由、Request/Response、鉴权中间件和错误映射。

## 独有要求

- Public、Management和Internal入口清楚分开。
- DTO与领域模型分开。
- Handler只协调公开用例。
- API兼容变化在HTTP边界明确处理。

正确：调用Commerce公开Command并转换响应。  
错误：在Handler中直接操作Commerce数据库。
