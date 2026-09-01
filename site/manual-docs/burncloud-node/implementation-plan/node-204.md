---
title: "NODE-204：定义 ResolvedModel 与失败诊断合同"
slug: /burncloud-node/implementation-plan/node-204/
---

# NODE-204：定义 ResolvedModel 与失败诊断合同

**状态：PLANNED**  
**类别：Model Resolver**  
**依赖：NODE-203**

## 目标

把 Resolver 输出固定成 `ResolvedModel`，作为 Preparation 与 Runtime 的稳定边界。

## 期望行为

ResolvedModel 至少包含 canonical ID、variant、format、quantization、artifact reference、runtime requirement、resource requirement；失败返回语义化诊断。

## 范围

**Allowed**：输出合同与错误类型。  
**Avoid**：在合同中塞入 PID、动态端口或下载进度。

## Invariants

- Candidate：Artifact selection 与 Process state 分离。

## 验证

ResolvedModel 可独立单元测试和序列化（若需要），错误不依赖字符串匹配。

## Done When

NODE-301 和 NODE-401 都只依赖 ResolvedModel，而无需了解 Resolver 内部决策。