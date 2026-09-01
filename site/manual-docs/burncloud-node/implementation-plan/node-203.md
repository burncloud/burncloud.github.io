---
title: "NODE-203：根据 Hardware / Runtime 选择 Variant"
slug: /burncloud-node/implementation-plan/node-203/
---

# NODE-203：根据 Hardware / Runtime 选择 Variant

**状态：PLANNED**  
**类别：Model Resolver**  
**依赖：NODE-101~103, NODE-201~202**

## 目标

根据 canonical model、HardwareProfile、compatibility 与 Manifest，在多个 Variant 中选择当前机器可执行的候选。

## 期望行为

选择必须可解释、可测试；没有可运行 Variant 时返回结构化原因，不静默降级到随机文件。

## 范围

**Allowed**：selection policy、resource fit checks。  
**Avoid**：下载、进程启动、修改 Router。

## Invariants

- Candidate：Resolver 只选择，不执行副作用。

## 验证

覆盖显存充足/不足、CPU fallback（若 Manifest 允许）、多个可行 Variant、完全不兼容。

## Done When

给定固定输入时 Variant 选择是确定且可解释的。