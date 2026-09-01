---
title: "NODE-301：建立 Local Artifact State"
slug: /burncloud-node/implementation-plan/node-301/
---

# NODE-301：建立 Local Artifact State

**状态：PLANNED**  
**类别：Model Preparation**  
**依赖：NODE-204**

## 目标

让 Node 明确知道 ResolvedModel 对应 Artifact 是否 absent / preparing / ready / failed，而不是仅检查某个路径是否存在。

## 当前事实

现有 BurnCloud 已有模型记录与下载状态能力，应优先复用。

## 范围

**Allowed**：本地 Artifact 状态映射、持久状态的最小扩展。  
**Avoid**：第二套模型数据库、Runtime state 混入 Artifact state。

## Invariants

- Candidate：Artifact state 与 Process state 独立。

## 验证

重启后可恢复必要状态；不存在文件不会被错误标记 READY。

## Done When

Preparation 可以基于状态安全决定复用、准备或失败。