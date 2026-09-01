---
title: "NODE-401：llama.cpp Runtime Adapter 与 ProcessSpec"
slug: /burncloud-node/implementation-plan/node-401/
---

# NODE-401：llama.cpp Runtime Adapter 与 ProcessSpec

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**依赖：NODE-103, NODE-204, NODE-303**

## 目标

把现有 llama-server 启动知识收敛为 Runtime Adapter，并输出无副作用的 `ProcessSpec`。

## 当前事实

现有 InferenceService 已有 llama-server 路径、参数构造和启动原型，但职责混合。

## 期望行为

Runtime Adapter 根据 ResolvedModel + HardwareProfile 生成 binary、args、env、working dir、health semantics 等 ProcessSpec，不持有 PID。

## 范围

**Allowed**：llama.cpp adapter、参数验证。  
**Avoid**：实际 spawn、Router registration、多 Runtime 抽象扩张。

## Invariants

- Candidate：Runtime 决定如何运行，Process Manager 决定如何管理进程。

## Done When

ProcessSpec 可以独立测试，且不启动真实进程。