---
title: "Interfaces规则"
slug: /architecture/crates/interfaces/
sidebar_label: "Interfaces"
---

# Interfaces 总体规则

继承：[基础规则](/architecture/base-rules/)。

## 1. 负责什么

负责 HTTP、Web UI、CLI、SDK、Webhook、WebSocket 等外部入口与协议适配，把外部输入转换成业务模块可理解的请求，再把结果转换成对外输出。

## 2. 不负责什么

不拥有 Identity、Supply、Traffic、Commerce、Trust 的核心业务规则，不直接维护这些领域的数据。

## 3. 可以依赖什么

可以依赖业务模块的 Public API / Contract，以及 `kernel`；需要通用技术能力时使用 `platform` 的公开能力。

## 4. 禁止依赖什么

禁止依赖其他模块的 `internal`、Adapter、Repository、数据库 Row；禁止为了页面或接口方便复制核心业务规则。

## 5. 目录和文件

按真实入口类型组织。HTTP、Web UI、CLI、WebSocket 等形成独立职责后再向下拆分；协议层与业务逻辑保持分离。

## 6. 代码要求

入口层负责解析、校验协议格式、认证上下文传递、调用公开业务能力和响应映射；业务决策必须下沉到所属领域。

## 7. 可复用规则

按实际引用 [Rust通用规则](/architecture/reusable/rust/)、[UI规则](/architecture/reusable/ui/)、[HTTP API规则](/architecture/reusable/http-api/)、Streaming 等复用规则。

## 8. 独有测试

重点覆盖协议转换、输入边界、错误映射、鉴权上下文和公开业务接口的连接；业务规则本身由所属领域测试。

## 9. 正确示例

```text
HTTP Handler 解析请求 → commerce::public → 映射 HTTP Response
```

## 10. 错误示例

```text
HTTP Handler 直接 UPDATE billing 表        ❌
Web UI 自己实现最终价格计算                 ❌
CLI 直接构造 supply 的内部 Repository       ❌
```