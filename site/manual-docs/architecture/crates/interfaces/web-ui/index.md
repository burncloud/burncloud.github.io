---
title: "interfaces / web-ui"
slug: /architecture/crates/interfaces/web-ui/
---

# Web UI

继承 [Interfaces 规则](../index.md)、[基础规则](../../../foundation.md)和 [UI 可复用规则](../../../reusable-rules/ui/index.md)。

## Owner 与职责

Owner 是 Interfaces / Web UI Maintainer。负责 Production UI 的页面、路由、交互、UI 状态，以及对业务公开契约的调用和展示。

## 不负责与业务真相

不拥有身份、权限、价格、余额、账单、路由结果、运行状态和审计结论。Web UI 只投影各业务 Owner 返回的事实，不能建立第二套真相。

## 公开契约

对用户提供稳定页面和交互；对内部只使用统一 Route、Authorization、Typed API 和 Platform Adapter。页面组件不是跨领域公开业务契约。

## 依赖

Web UI 可以依赖 Interfaces 公共能力、UI 可复用规则和各业务领域公开契约。业务领域不得反向依赖 Web UI。

禁止页面直接依赖 Database、Repository、Provider、后端 Service、裸 HTTP Client 或环境密钥。

## 目录、代码与复用

页面按用户任务组织，不按数据库表组织。页面负责组合，Action 负责编排，Typed API 负责传输，服务端 Owner 负责最终授权和业务判断。

使用 UI 状态、共享组件、Design System、i18n、CSS 和 UI 测试规则。

## 独有测试

除 UI 通用状态外，还要验证 Route、Workspace、Capability、后端 403、API Namespace，以及 Web、Desktop、LiveView 中实际支持的平台行为。

## 正确与错误

正确：Billing 页面调用类型化 Commerce API，并展示后端返回的 Invoice 状态。  
错误：页面隐藏付款按钮后，就认为用户已经失去服务端付款权限。

## 子规则

- [目录结构](./directory.md)
- [依赖规则](./dependencies.md)
- [Route](./route.md)
- [Authorization](./authorization.md)
- [API Boundary](./api-boundary.md)
- [多平台边界](./platform.md)
- [修改范围](./change-scope.md)
- [迁移规则](./migration.md)
