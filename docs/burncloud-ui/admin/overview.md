---
title: "Admin Overview"
slug: /burncloud-ui/admin/overview/
---

# Admin Overview

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Admin Overview 是 **Business + Infrastructure Command Center**。顶部固定回答 Today Revenue、Gross Margin、Online GPU Capacity、API Availability，并主动指出 Supply、Demand、Capacity 和 Economics 中最值得关注的风险。

### Primary Question
> **平台今天赚钱吗？容量和 API 是否健康？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Revenue / Margin | 逐 PID 操作 |
| Online Capacity | 大面积原始 GPU 表 |
| API Availability | 无结论 KPI 墙 |
| Needs Attention | Buyer Secret |

### Reviewer Focus
1. 首页是否先给结论而不是原始基础设施数据？
2. Needs Attention 是否说明原因、影响和 BurnCloud 已做什么？
3. Gross Margin 是否只在成本事实完整时显示？

---

## 第二层：机器执行层
- Revenue ← Revenue ledger
- Gross Margin ← Revenue + verified cost；成本不完整时显示 Unknown/Estimated
- Online GPU Capacity ← Capacity aggregation
- API Availability ← serving observability
- Needs Attention ← Supply / Capacity / Demand / Operations risk summaries

### Autopilot
低风险容量恢复自动执行并报告结果；大额外租、支付、安全和危险数据操作进入 Human Gate。

---

## 第三层：Definition of Done
- [ ] 四个核心指标可追溯真实来源。
- [ ] Gross Margin 不产生虚假精确值。
- [ ] Needs Attention 有原因/影响/动作/结果。
- [ ] Admin 不被迫逐 GPU 日常操作。
- [ ] 通过分支 + Pull Request 合并。
