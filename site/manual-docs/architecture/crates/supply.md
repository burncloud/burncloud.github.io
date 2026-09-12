---
title: "Supply规则"
slug: /architecture/crates/supply/
sidebar_label: "Supply"
---

# Supply 总体规则

继承：[基础规则](/architecture/base-rules/)。

## 1. 负责什么

负责模型、Provider、Channel、Credential、区域、容量和可供给能力等“系统有什么资源可以提供”。

## 2. 不负责什么

不负责请求如何路由和执行，不负责计量、价格、账单和结算，不负责外部 HTTP/UI 展示。

## 3. 可以依赖什么

默认依赖 `kernel`；需要通用基础设施时只使用 `platform` 的公开能力。其他业务依赖必须在更下级规则中明确说明。

## 4. 禁止依赖什么

禁止依赖 `traffic` 的内部执行逻辑、`commerce` 的内部计费逻辑或 `interfaces` 的入口实现。

## 5. 目录和文件

Provider、Model、Channel 等只有在真实职责独立后才向下拆分；Provider 身份/能力与请求执行逻辑不得混为同一职责。

## 6. 代码要求

Supply 描述“有什么、由谁提供、可否使用”，不决定具体请求怎么跑。

## 7. 可复用规则

Rust 代码引用 [Rust通用规则](/architecture/reusable/rust/)；涉及 Database、P2P 等能力时按实际引用对应规则。

## 8. 独有测试

重点覆盖供给资源的有效性、状态变化、Credential 权限边界和能力查询。

## 9. 正确示例

```text
AWS Provider 的身份、Credential、Region、支持模型 → supply
```

## 10. 错误示例

```text
Bedrock 请求重试和流式响应实现 → supply   ❌
Billing 价格计算 → supply                  ❌
```