---
title: "类别二：Hardware Profile"
slug: /burncloud-node/implementation-plan/hardware-profile/
---

# 类别二：Hardware Profile

Hardware Profile 是 Node 内唯一权威硬件事实。Resolver、Runtime、诊断和未来 UI 必须读取同一份 Profile，禁止各模块独立探测 GPU 后形成不同判断。

## Issue

| ID | 功能 | 依赖 | 状态 |
|---|---|---|---|
| NODE-101 | 定义 canonical HardwareProfile | NODE-002 | PLANNED |
| NODE-102 | 检测 NVIDIA GPU / VRAM / Driver | NODE-101 | PLANNED |
| NODE-103 | 生成 Runtime Compatibility 与资源快照 | NODE-101, NODE-102 | PLANNED |

本类别优先扩展现有 Monitor 能力，不建立第二套 CPU / RAM / Disk 监控。