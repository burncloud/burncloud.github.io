---
title: "interfaces"
slug: /architecture/crates/interfaces/
---

# `crates/interfaces`

继承 [基础规则](/architecture/foundation/)。

本页是 Interfaces 的目录规则。下面的目录是职责划分，不是 `burncloud/burncloud` main 的逐文件清单。当前 main 上的 HTTP 服务和 Dioxus 客户端分别在 `crates/interfaces/server` 与 `crates/interfaces/client`，和下面按入口类型划分的规则目录不是同名对照。

## 负责什么

负责 HTTP、Web UI、CLI、SDK、Webhook、WebSocket 等外部入口与协议适配。把外部输入转换成业务模块可理解的请求，再把结果转换成对外输出。

## 不负责什么

不拥有 Identity、Supply、Traffic、Commerce、Trust 的核心业务规则，不直接维护这些领域的数据，也不成为跨领域数据库入口。

## 依赖

可以依赖业务模块的 Public API 或 Contract，以及 `kernel`。需要通用技术能力时使用 `platform` 的公开能力。业务领域不得反向依赖具体 UI、HTTP 或 CLI。

禁止依赖其他模块的 `internal`、Adapter、Repository、数据库 Row。禁止为了页面或接口方便复制核心业务规则。

## 目录

按真实入口类型组织。HTTP、Web UI、CLI、WebSocket 等形成独立职责后再向下拆分。协议层与业务逻辑保持分离。

```text
interfaces/
├── http/
├── web_ui/
├── cli/
└── websocket/
```

## 代码要求

入口层负责解析、校验协议格式、认证上下文传递、调用公开业务能力和响应映射。业务决策必须下沉到所属领域。具体测试由接口类型决定。

## 可复用规则

按实际引用 [Rust 通用规则](/architecture/reusable-rules/rust/)、[UI 规则](/architecture/reusable-rules/ui/)、[HTTP API 规则](/architecture/reusable-rules/http-api/) 和 [Streaming 规则](/architecture/reusable-rules/streaming/)。

## 测试

重点覆盖协议转换、输入边界、错误映射、鉴权上下文和公开业务接口的连接。业务规则本身由所属领域测试。

## 正确与错误

正确：HTTP Handler 解析请求，调用领域公开能力，再映射 HTTP Response。例如把请求转换成 Commerce Command。

错误：

```text
HTTP Handler 直接 UPDATE billing 表        ❌
HTTP Handler 自己计算金额并直接修改账单表    ❌
Web UI 自己实现最终价格计算                 ❌
CLI 直接构造 supply 的内部 Repository       ❌
```

## 子目录

- [HTTP](./http.md)
- [Web UI](./web-ui/index.md)
- [CLI](./cli.md)
- [WebSocket](./websocket.md)
