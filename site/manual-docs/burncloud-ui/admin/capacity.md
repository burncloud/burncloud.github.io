---
title: "Admin Capacity"
slug: /burncloud-ui/admin/capacity/
---

# Admin Capacity

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Capacity 围绕 **Model / Tier** 展示 Available Capacity、Headroom、Utilization 和 Risk，并解释 BurnCloud 已采取、正在采取或建议采取的恢复动作。

### Primary Question
> **哪些模型/层级快没有安全容量？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Model/Tier Capacity | 默认逐 GPU 调度 |
| Headroom / Utilization | 手工端口 |
| Capacity Risk | PID 控制 |
| Recovery Action | Supplier Secret |

### Reviewer Focus
1. 风险是否以 Model/Tier 业务视角表达？
2. Local / Provider / External Capacity 是否能解释但不要求手工调度？
3. 高成本动作是否显示成本和 Margin 影响后再进入 Human Gate？

---

## 第二层：机器执行层
- Capacity ← Capacity aggregation
- Demand / Forecast ← Demand service
- Local readiness ← BurnCloud Node managed runtime state
- Provider capacity ← existing Provider/Channel availability
- Economics ← verified compute/provider cost and expected margin

### Autopilot Contract
```text
Observe → Predict → Decide → Act → Verify → Report
```
低风险扩容/恢复自动执行；大额外租或显著 Margin 影响才进入明确 Proposal + Approve/Reject。

---

## 第三层：Definition of Done
- [ ] Model/Tier Capacity 有真实来源。
- [ ] Headroom / Risk 可解释。
- [ ] 自动动作有 Verify 结果。
- [ ] 高风险 Proposal 有成本/收益/影响范围。
- [ ] 无逐 GPU 手工调度成为默认流程。
- [ ] 通过分支 + Pull Request 合并。
