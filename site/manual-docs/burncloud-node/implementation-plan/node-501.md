---
title: "NODE-501：READY Runtime 注册 Local Channel / Ability"
slug: /burncloud-node/implementation-plan/node-501/
---

# NODE-501：READY Runtime 注册 Local Channel / Ability

**状态：PLANNED**  
**类别：Local Channel Integration**  
**依赖：NODE-403**

## 目标

把 READY 的本地 Runtime 注册为现有 BurnCloud Router 能选择的 Local Channel / Channel Ability。

## 当前事实

现有 InferenceService 已有启动本地 llama-server 后创建 Channel / Ability 的原型路径。

## 期望行为

Router 不需要知道 Runtime 是 llama.cpp；它只消费已有 Channel 能力和 endpoint。

## 范围

**Allowed**：Local Channel adapter、Ability metadata。  
**Avoid**：NodeRouteEngine、LocalRouter、绕过现有 ModelRouter。

## Invariants

- `INV-ROUTER-001`
- Candidate：Local model 通过现有 Channel 进入数据面。

## 验证

READY 前不能注册；READY 后可被现有路由选择。

## Done When

本地 Runtime 成为现有 Router 的正常候选，而不是特殊旁路。