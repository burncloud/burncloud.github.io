---
title: "NODE-101：定义 canonical HardwareProfile"
slug: /burncloud-node/implementation-plan/node-101/
---

# NODE-101：定义 canonical HardwareProfile

**状态：PLANNED**  
**类别：Hardware Profile**  
**依赖：NODE-002**

## 目标

定义 Node 内唯一权威硬件画像合同 `HardwareProfile`。

## 当前事实

现有 Monitor 已提供 CPU / Memory / Disk 等基础监控，但 Node 的 Resolver / Runtime 仍缺统一 GPU 级输入合同。

## 期望行为

HardwareProfile 至少可表达 OS、CPU、RAM、磁盘、GPU vendor/model/count、VRAM、Driver 与兼容性相关字段；未知值必须可显式表达。

## 范围

**Allowed**：数据结构、序列化、Monitor 到 Profile 的适配。  
**Avoid**：在 Resolver/Runtime 内重新探测硬件。

## Invariants

- Candidate：Node 内只有一份 canonical HardwareProfile。

## 验证

CPU/RAM/Disk 已有数据可映射；缺失 GPU 信息时不会伪造默认硬件。

## Done When

所有后续硬件判断都有统一输入类型，且不需要复制硬件探测逻辑。