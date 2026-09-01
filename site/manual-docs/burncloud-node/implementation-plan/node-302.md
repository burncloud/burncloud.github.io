---
title: "NODE-302：复用下载系统完成 Prepare / 去重"
slug: /burncloud-node/implementation-plan/node-302/
---

# NODE-302：复用下载系统完成 Prepare / 去重

**状态：PLANNED**  
**类别：Model Preparation**  
**依赖：NODE-301**

## 目标

使用现有 Model Service / Download Manager 把 ResolvedModel 准备成本地 Artifact，并避免相同 Artifact 并发重复下载。

## 范围

**Allowed**：Node Preparation orchestration、existing downloader adapter。  
**Avoid**：NodeDownloader、第一次 inference 请求无限阻塞等待大模型下载。

## Invariants

- Candidate：下载技术属于现有 Download Manager，Node 只编排。

## 验证

同一 Artifact 并发 prepare 只产生一个实际下载任务；已有完整文件可直接复用。

## Done When

ResolvedModel 可以进入 READY Artifact 状态且不重复造下载能力。