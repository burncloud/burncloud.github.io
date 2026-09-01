---
title: "NODE-303：Artifact 校验、失败状态与恢复"
slug: /burncloud-node/implementation-plan/node-303/
---

# NODE-303：Artifact 校验、失败状态与恢复

**状态：PLANNED**  
**类别：Model Preparation**  
**依赖：NODE-302**

## 目标

在 Artifact 进入 READY 前完成必要完整性校验，并让中断、损坏和失败具有可恢复状态。

## 期望行为

文件存在不等于 Artifact READY；只有满足 Manifest 指定完整性条件才可交给 Runtime。

## 范围

**Allowed**：checksum/size/manifest verification、失败恢复。  
**Avoid**：模型语义推理、Runtime health check。

## Invariants

- Candidate：READY Artifact 必须可验证。

## 验证

损坏文件、部分下载、校验失败、恢复成功均有测试。

## Done When

Runtime Manager 永远只接收已通过 Preparation 验证的 Artifact。