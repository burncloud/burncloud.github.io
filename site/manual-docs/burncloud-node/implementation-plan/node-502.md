---
title: "NODE-502：健康状态联动、摘除与注销"
slug: /burncloud-node/implementation-plan/node-502/
---

# NODE-502：健康状态联动、摘除与注销

**状态：PLANNED**  
**类别：Local Channel Integration**  
**依赖：NODE-404, NODE-501**

## 目标

让 Local Channel 的可路由状态始终跟随真实 Runtime 健康状态。

## 期望行为

进程 stop/crash/unhealthy 后，本地 Channel 不再接收流量；重新 READY 后按明确策略恢复。

## 范围

**Allowed**：channel availability linkage、unregister/remove。  
**Avoid**：改变 Provider failover 语义、修改 Billing/Auth。

## Invariants

- `INV-ROUTER-001`
- `INV-AUTH-002`
- `INV-BILLING-001`
- `INV-BILLING-002`

## 验证

Runtime 健康变化能够及时影响候选选择，同时 Provider 路由回归不受破坏。

## Done When

Router 不会把真实已失效的本地进程继续视为可用 Channel。