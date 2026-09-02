---
title: "Admin Demand"
slug: /burncloud-ui/admin/demand/
---

# Admin Demand

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Demand 展示 Requests、Tokens、Concurrency 和增长趋势，并按 Model / Tier / Region 下钻，为 Capacity Prediction 和 Autopilot 提供可解释输入。

### Primary Question
> **哪些模型需求正在上涨，未来哪里会缺容量？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Demand Trend | Buyer Private Prompt |
| Model/Tier Breakdown | API Key Secret |
| Growth / Peak | 逐 GPU 状态 |
| Forecast / Confidence | Supplier Payout |

### Reviewer Focus
1. Demand 与 Capacity 是否使用同一个 Model/Tier 语义？
2. Forecast 是否区分事实和预测？
3. 异常增长是否能自然下钻到 Capacity？

---

## 第二层：机器执行层
- Requests / Tokens / Concurrency ← Request + Usage aggregation
- Model / Tier ← canonical product identities
- Forecast ← demand prediction service
- Region ← routing/serving geography（如产品支持）

Prediction 可以自动运行；由 Forecast 触发的大额外租等高风险动作由 Capacity / Operations 负责 Human Gate。

---

## 第三层：Definition of Done
- [ ] Actual 与 Forecast 清楚分离。
- [ ] Model/Tier breakdown 与 Usage/Capacity 一致。
- [ ] Buyer private data 默认不暴露。
- [ ] Demand risk 可链接到 Capacity。
- [ ] 通过分支 + Pull Request 合并。
