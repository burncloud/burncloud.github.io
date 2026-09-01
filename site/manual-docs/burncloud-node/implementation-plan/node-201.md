---
title: "NODE-201：定义 Model Manifest"
slug: /burncloud-node/implementation-plan/node-201/
---

# NODE-201：定义 Model Manifest

**状态：PLANNED**  
**类别：Model Resolver**  
**依赖：无**

## 目标

定义逻辑模型、Variant、Artifact 与 Runtime requirement 的声明式 Manifest。

## 期望行为

Manifest 可以描述 canonical model ID、aliases、format、quantization、artifact identity、runtime compatibility 与资源需求，而不把 Artifact 文件名当成模型身份。

## 范围

**Allowed**：Manifest schema、解析/校验、最小示例。  
**Avoid**：下载模型、启动 Runtime、自动扫描所有 Hugging Face 内容。

## Invariants

- Candidate：Model ID 是稳定逻辑身份，Artifact 是实现细节。

## 验证

非法/缺字段 Manifest 明确失败；相同逻辑模型可包含多个 Variant。

## Done When

Resolver 有稳定、可审查的模型事实输入，而不是通过文件名猜模型。