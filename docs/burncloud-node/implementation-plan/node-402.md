---
title: "NODE-402：内部端口分配与 Process Spawn"
slug: /burncloud-node/implementation-plan/node-402/
---

# NODE-402：内部端口分配与 Process Spawn

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**依赖：NODE-401**

## 目标

Process Manager 接收 ProcessSpec，安全分配内部端口并启动模型进程。

## 期望行为

用户不需要手工指定 PID 或内部端口；端口冲突和 spawn failure 有明确错误。

## 范围

**Allowed**：port allocation、child process ownership、PID/handle state。  
**Avoid**：把 spawn success 标记为 READY、直接注册 Router。

## Invariants

- `INV-WORKSPACE-002`
- Candidate：Spawned 与 Ready 是不同状态。

## 验证

端口冲突、进程无法执行、正常 spawn/stop 基础路径均覆盖。

## Done When

Process Manager 能稳定启动并持有进程，但模型尚需 NODE-403 才能进入 READY。