---
title: "Supplier Overview"
slug: /burncloud-ui/supplier/overview/
---

# Supplier Overview

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Supplier 首页先回答两件事：**我的机器正常吗？今天赚了多少？** 顶部建议固定 Today Earnings、Online GPUs、GPU Utilization、Inference Today，下面优先 Needs Attention、Revenue Trend、Resource Health。

### Primary Question
> **我的机器正常吗？今天贡献和收入怎么样？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Today Earnings | Buyer identity |
| Online GPUs | Router 配置 |
| GPU Utilization | 手工模型部署 |
| Needs Attention | Platform Margin |

### Reviewer Focus
1. 是否先显示结果而不是硬件参数墙？
2. 真正需要 Supplier 行动的异常是否优先？
3. 自动恢复成功是否保持安静而非制造红色告警？

---

## 第二层：机器执行层
- Earnings ← Supplier earnings ledger
- Online GPU / Utilization ← Node telemetry / HardwareProfile
- Inference Today ← Usage / contribution metrics
- Needs Attention ← Reliability / Node health actionable events

正常部署、模型切换和恢复由 BurnCloud 自动执行。Supplier 只在机器、网络、维护等需要自身处理时收到明确动作建议。

### State Contract
Unknown earnings 不得显示 `$0`；部分 Node telemetry 失败时保留已确认收入与在线资源；Recovered 必须说明自动恢复结果。

---

## 第三层：Definition of Done
- [ ] 四个顶部指标有真实来源。
- [ ] Supplier 不看到 Buyer 私有信息或 Router 控制。
- [ ] Needs Attention 只包含真正需要行动的问题。
- [ ] Partial Failure / Recovered 已验证。
- [ ] 通过分支 + Pull Request 合并。
