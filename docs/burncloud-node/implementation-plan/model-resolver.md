---
title: "类别三：Model Resolver"
slug: /burncloud-node/implementation-plan/model-resolver/
---

# 类别三：Model Resolver

Model Resolver 负责把用户声明的逻辑 `model` 转换成**本机可执行的模型事实**。

```text
model=qwen-4b
   ↓
Canonical ID / Alias
   ↓
Curated Model Manifest
   ↓
Hardware + Resource + Runtime facts
   ↓
ResolvedModel
   或
结构化 ResolutionFailure
```

关键原则：

> **Resolver 只选择并诊断，不下载、不启动、不路由。**

本类别包括：

- **NODE-201**：Model Manifest + v0.1 curated model catalog；
- **NODE-202**：Canonical Model ID / Alias；
- **NODE-203**：根据 Hardware / Runtime 自动选择 Variant，并给出结构化 reject reason；
- **NODE-204**：稳定 `ResolvedModel` / `ResolutionFailure` 合同。

Demand-driven Node 不允许用户自己挑 GGUF。显存、内存或 Runtime 不满足时，Resolver 必须给后续 Reconciler 可机器处理的原因，而不是自由文本或模糊的“模型不存在”。
