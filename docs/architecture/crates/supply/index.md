---
title: "supply"
slug: /architecture/crates/supply/
---

# `crates/supply`

继承 [基础规则](/architecture/foundation/)。

本页是 Supply 的目录规则。下面的目录是职责划分，不是 `burncloud/burncloud` main 的逐文件清单。

## 负责什么

负责 Model、Provider、Channel、Upstream Credential、区域、Capacity 和可供给能力：系统有什么资源可以提供。

## 不负责什么

不负责本次请求最终选择，不负责请求如何路由和执行，不负责计量、价格、客户计费、余额、账单和结算，不负责来源证明结论，不负责外部 HTTP 或 UI 展示。

## 依赖

默认依赖 `kernel`。可以依赖 Identity 的稳定标识和 Platform Port。需要通用基础设施时只使用 `platform` 的公开能力。Traffic 通过 Supply 公开契约取得候选供应能力。其他业务依赖必须在更下级规则中明确说明。

禁止依赖 `traffic` 的内部执行逻辑、`commerce` 的内部计费逻辑或 `interfaces` 的入口实现。

## 目录

Provider、Model、Channel 等只有在真实职责独立后才向下拆分。Provider 身份和能力与请求执行逻辑不得混为同一职责。

```text
supply/
├── model/
├── provider/
├── channel/
├── credential/
└── capacity/
```

## 代码要求

Supply 描述“有什么、由谁提供、可否使用”，不决定具体请求怎么跑。供应事实与运行时选择分开。凭证默认不可见。

## 可复用规则

Rust 代码引用 [Rust 通用规则](/architecture/reusable-rules/rust/)。涉及 Database、P2P 等能力时按实际引用对应规则。

## 测试

重点覆盖供给资源的有效性、状态变化、Credential 权限边界、能力查询、模型能力、Provider 配置、Channel 关系和容量状态。

## 正确与错误

正确：Supply 返回符合模型能力的候选 Channel。AWS Provider 的身份、Credential、Region 和支持模型属于 Supply。

错误：

```text
Bedrock 请求重试和流式响应实现 → supply   ❌
Billing 价格计算 → supply                  ❌
Supply 根据客户余额决定最终请求路由         ❌
```

## 子目录

当前没有已单独成页的 Supply 子规则。下级职责出现独立边界后再增加页面，不在这里预写空页。
