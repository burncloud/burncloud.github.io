---
title: "NODE-102：检测 NVIDIA GPU / VRAM / Driver"
slug: /burncloud-node/implementation-plan/node-102/
---

# NODE-102：检测 NVIDIA GPU / VRAM / Driver

**状态：PLANNED**  
**类别：Hardware Profile**  
**依赖：NODE-101**

## 目标

在支持的 NVIDIA 主机上，把 GPU 型号、数量、显存和 Driver 信息写入 canonical HardwareProfile。

## 期望行为

检测失败必须得到明确的 unavailable / unknown 结果，而不是把“没有检测到”解释成“没有 GPU”。

## 范围

**Allowed**：Linux/NVIDIA detection adapter、解析和测试夹具。  
**Avoid**：Resolver 内调用 `nvidia-smi`；硬编码具体模型可运行哪些 LLM。

## Invariants

- Candidate：硬件探测与模型选择分离。

## 验证

覆盖有 GPU、无工具、命令失败、字段缺失、多 GPU 等情况。

## Done When

受支持 NVIDIA 环境可稳定产生结构化 GPU/VRAM/Driver 数据，失败状态可诊断。