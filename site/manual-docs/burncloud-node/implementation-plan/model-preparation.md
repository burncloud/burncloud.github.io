---
title: "类别四：Model Preparation"
slug: /burncloud-node/implementation-plan/model-preparation/
---

# 类别四：Model Preparation

Model Preparation 把 `ResolvedModel` 变成经过验证、可供 Runtime 使用的本地 Artifact。

## Issue

| ID | 功能 | 依赖 | 状态 |
|---|---|---|---|
| NODE-301 | 建立 Local Artifact State | NODE-204 | PLANNED |
| NODE-302 | 复用现有下载系统完成 Prepare / 去重 | NODE-301 | PLANNED |
| NODE-303 | Artifact 校验、失败状态与恢复 | NODE-302 | PLANNED |

本类别必须复用现有 Model Service / Download Manager，不创建 NodeDownloader。