---
title: "NODE-003：组合现有 Server / Router 为 Node 模式"
slug: /burncloud-node/implementation-plan/node-003/
---

# NODE-003：组合现有 Server / Router 为 Node 模式

**状态：PLANNED**  
**类别：Node Core**  
**依赖：NODE-001, NODE-002**

## 目标

Node 模式直接复用现有 Server 与 Router 暴露稳定 AI API，不创建 NodeGateway 或 NodeRouter。

## 当前事实

- `STATIC CONFIRMED`：Server 是统一 Axum App。
- `STATIC CONFIRMED`：Router 提供 data-plane explicit routes + fallback。

## 期望行为

Node 启动后，`localhost:3000` 使用现有数据面处理请求；Node 只为本地执行链提供新的可路由目标。

## 范围

**Allowed**：Node profile 对现有 Server/Router 的组合方式。  
**Avoid**：重建 OpenAI Gateway、改变现有 Provider Routing、绕过 security boundary。

## Invariants

- `INV-RUNTIME-002`
- `INV-ROUTER-001`
- `INV-ROUTER-002`
- `INV-AUTH-002`

## 验证

现有 Provider 请求仍可工作；Node 模式不改变现有管理面/数据面安全语义。

## Done When

Node 可以通过现有 Server / Router 提供 AI API，并为 NODE-503 的本地 E2E 提供稳定入口。