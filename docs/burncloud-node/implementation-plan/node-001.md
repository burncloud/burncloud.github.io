---
title: "NODE-001：建立 Node 启动入口与生命周期"
slug: /burncloud-node/implementation-plan/node-001/
---

# NODE-001：建立 Node 启动入口与生命周期

**状态：PLANNED**  
**类别：Node Core**  
**依赖：无**

## 目标

建立明确的 BurnCloud Node 运行入口，使 Node 成为现有 BurnCloud 的一种运行形态，而不是第二套程序体系。

## 当前事实

- `STATIC CONFIRMED`：现有 `server` 与 `router` CLI 最终共享 Server startup。
- `STATIC CONFIRMED`：统一 Axum Server 已组合 management plane 与 data-plane fallback。

## 期望行为

Node 有明确的 initialize / start / shutdown 生命周期，并能承载后续 Hardware、Resolver、Runtime 等组件初始化。

## 范围

**Allowed**：CLI 启动入口、`crates/node` 编排接口、生命周期合同。  
**Avoid**：新建第二个 HTTP Server、重写 Router、改变 Auth / Billing 语义。

## Invariants

- `INV-RUNTIME-001`
- `INV-RUNTIME-002`

## 验证

- Node 模式可以独立启动和正常退出。
- 现有 `server` / `router` 行为保持回归通过。

## Done When

存在一个稳定 Node 生命周期入口；后续组件可以挂载在 Node Core，而不需要再次发明启动体系。