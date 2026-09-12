---
title: "Identity规则"
slug: /architecture/crates/identity/
sidebar_label: "Identity"
---

# Identity 总体规则

继承：[基础规则](/architecture/base-rules/)。

## 1. 负责什么

负责用户、组织、Tenant、认证、授权、身份关系和 API Key 等“谁在使用系统、拥有什么权限”的能力。

## 2. 不负责什么

不负责模型/Provider 供给，不负责请求路由和执行，不负责价格、账单、结算，不负责审计证明。

## 3. 可以依赖什么

默认依赖 `kernel`；需要通用基础设施时只使用 `platform` 的公开能力。跨业务领域依赖必须在更下级规则中明确说明。

## 4. 禁止依赖什么

禁止依赖其他领域内部实现、数据库表、Repository 或 Adapter；禁止通过 `interfaces` 反向获取业务能力。

## 5. 目录和文件

按身份领域的真实功能向下组织；认证、授权、用户、组织等只有在形成独立职责后才拆分。

## 6. 代码要求

身份判断和权限判断必须有唯一业务归属；不要把权限规则散落到 HTTP Handler、UI 或其他领域。

## 7. 可复用规则

Rust 代码引用 [Rust通用规则](/architecture/reusable/rust/)；涉及数据库或 HTTP 时按实际需要引用对应复用规则。

## 8. 独有测试

必须覆盖授权边界、Tenant 隔离、无权限访问和身份状态变化等关键行为。

## 9. 正确示例

```text
“当前用户是否有权操作该 Tenant？” → identity 的公开能力
```

## 10. 错误示例

```text
HTTP Handler 自己复制一套角色判断      ❌
commerce 直接查询 identity 的用户表    ❌
UI 隐藏按钮就当作完成授权              ❌
```