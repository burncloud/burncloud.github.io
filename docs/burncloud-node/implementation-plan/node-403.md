---
title: "NODE-403：Readiness / Health 状态机"
slug: /burncloud-node/implementation-plan/node-403/
---

# NODE-403：Readiness / Health 状态机

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**依赖：NODE-402**

## 目标

建立模型进程从 STARTING 到 READY / FAILED / UNHEALTHY 的明确状态机。

## 期望行为

只有 readiness 成功的 Runtime 才可被 Local Channel 注册；启动超时、health failure 必须可诊断。

## 范围

**Allowed**：readiness polling、health checks、timeouts、state transitions。  
**Avoid**：在健康检查中修改 Router 数据模型。

## Invariants

- Candidate：`Process Spawned != Model READY`。

## 验证

正常 ready、超时、进程提前退出、健康转坏均覆盖。

## Done When

上层可以只依赖 READY 状态决定是否暴露本地模型。