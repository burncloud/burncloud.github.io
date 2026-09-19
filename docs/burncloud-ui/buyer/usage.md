---
title: "Buyer Usage"
slug: /burncloud-ui/buyer/usage/
---

# Buyer Usage

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Usage 负责解释 Buyer 的 API 消耗：Requests、Tokens、Cost，以及按 Model、Tier、API Key、时间的 breakdown。它是消费分析页，不是 GPU 或 Supplier 分析页。

### Primary Question
> **我的 API 到底用在了哪里？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Tokens / Requests | GPU Utilization |
| Cost / Time Range | Supplier Earnings |
| Model / Tier breakdown | Platform Gross Margin |
| API Key breakdown | Provider Cost |

### Reviewer Focus
1. 金额是否明确币种和时间范围？
2. Estimated / Final 是否分离？
3. 异常 Usage 是否能自然下钻到 Logs？

---

## 第二层：机器执行层

### Production Mapping
- Requests / Tokens ← Usage metering
- Cost ← Billing ledger / pricing
- Model ← canonical model identity
- Tier ← product tier
- API Key ← credential metadata only

### Interaction Contract
默认提供 Search / Filter / Date Range；下钻顺序建议：Total → Model → Tier → API Key → Request Logs。

### State Contract
- Loading 不能先显示 0。
- Empty 解释“所选时间没有调用”。
- Partial Failure 保留已确认总量，失败 breakdown 显示 Unknown。
- 排序/过滤不得改变金额或 token 语义。

---

## 第三层：Definition of Done
- [ ] 总量与 breakdown 对得上。
- [ ] 金额有币种/时间范围。
- [ ] Estimated / Final 不混用。
- [ ] Buyer 不看到 GPU / Supplier / Provider 成本。
- [ ] 可从异常 Usage 跳到 Logs。
- [ ] 通过分支 + Pull Request 合并。
