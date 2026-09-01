---
title: "NODE-103：生成 Runtime Compatibility 与资源快照"
slug: /burncloud-node/implementation-plan/node-103/
---

# NODE-103：生成 Runtime Compatibility 与资源快照

**状态：PLANNED**  
**类别：Hardware Profile**  
**依赖：NODE-101, NODE-102**

## 目标

从 HardwareProfile 形成 Resolver/Runtime 可消费的资源与兼容性视图，而不是让它们各自解释原始硬件数据。

## 期望行为

能够表达可用 RAM/VRAM、GPU backend 条件和已知兼容性；动态可用资源与静态硬件身份保持区分。

## 范围

**Allowed**：resource snapshot、compatibility facts。  
**Avoid**：在此 Issue 实现模型 Variant 选择策略。

## Invariants

- Candidate：Detection 产生事实，Resolver 才做模型选择。

## 验证

资源不足和兼容性未知能够被明确表示。

## Done When

NODE-203 不需要重新读取操作系统或 GPU 工具即可完成选择判断。