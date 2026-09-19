---
title: "supply"
slug: /architecture/crates/supply/
---

# `crates/supply`

## 负责什么

负责 Model、Provider、Channel、Upstream Credential、Capacity 和可供应资源。

## 不负责什么

不负责本次请求最终选择、客户计费、余额和来源证明结论。

## 依赖

可以依赖 Kernel、Identity 的稳定标识和 Platform Port。Traffic 通过 Supply 公开契约取得候选供应能力。

## 目录

```text
supply/
├── model/
├── provider/
├── channel/
├── credential/
└── capacity/
```

## 代码与测试

供应事实与运行时选择分开；凭证默认不可见。测试聚焦模型能力、Provider配置、Channel关系和容量状态。

## 正确与错误

正确：Supply 返回符合模型能力的候选 Channel。  
错误：Supply 根据客户余额决定最终请求路由。
