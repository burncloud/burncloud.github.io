---
title: "NODE-202：建立 Canonical Model ID 与 Alias 解析"
slug: /burncloud-node/implementation-plan/node-202/
---

# NODE-202：建立 Canonical Model ID 与 Alias 解析

**状态：PLANNED**  
**类别：Model Resolver**  
**依赖：NODE-201**

## 目标

把用户请求的模型名称稳定解析到 canonical model ID，并消除 alias 导致的多套身份。

## 期望行为

Alias 只映射身份，不决定具体 Artifact；未知模型得到明确 `MODEL_NOT_FOUND` 类诊断。

## 范围

**Allowed**：registry/manifest lookup、alias normalization。  
**Avoid**：Provider 身份推断、硬件选择、下载。

## Invariants

- Candidate：Model ID 不是 Provider identity。
- Candidate：Alias 解析后进入唯一 canonical ID。

## 验证

canonical、alias、冲突 alias、未知模型都有确定行为。

## Done When

后续 Resolver 逻辑只处理 canonical model ID。