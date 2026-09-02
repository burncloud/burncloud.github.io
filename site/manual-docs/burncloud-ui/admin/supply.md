---
title: "Admin Supply"
slug: /burncloud-ui/admin/supply/
---

# Admin Supply

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Supply 用 Supplier / Node / GPU 视角回答平台当前拥有多少可靠算力、质量如何、哪里在增长或流失。默认先展示系统级结论，再允许下钻具体资源。

### Primary Question
> **我们现在拥有多少可靠算力供应？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Online Supply | 日常逐进程管理 |
| Supplier / Node Health | Buyer Billing Detail |
| Trust / Reliability | Prompt 内容 |
| GPU Capacity / Region | 无结论硬件信息墙 |

### Reviewer Focus
1. Supply 是否能按 Supplier、Region、GPU Type 下钻？
2. Trust/Verification 是否有明确来源？
3. 页面是否避免变成逐台机器操作面板？

---

## 第二层：机器执行层
- Suppliers ← Supplier registry
- Nodes ← Node inventory
- Hardware ← canonical HardwareProfile
- Reliability ← Reliability service
- Verification / Level ← identity/resource verification facts

常规接入、检测和 health 由 BurnCloud 自动管理；身份、信任等级和重要商业状态变更进入适用 Human Gate。

---

## 第三层：Definition of Done
- [ ] Supply 总量与 Node inventory 一致。
- [ ] Supplier / Node / GPU 下钻保持同一事实语义。
- [ ] Verification / Reliability 可解释。
- [ ] 无逐 PID 日常控制。
- [ ] 通过分支 + Pull Request 合并。
