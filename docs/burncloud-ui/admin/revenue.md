---
title: "Admin Revenue"
slug: /burncloud-ui/admin/revenue/
---

# Admin Revenue

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Revenue 解释平台 Revenue、Verified Cost 与 Gross Margin 的来源，并允许按 Model / Tier / Customer Segment / 时间下钻。成本不完整时禁止展示虚假精确 Margin。

### Primary Question
> **平台收入、成本和毛利来自哪里？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Revenue | 虚假精确 Margin |
| Verified Cost | Buyer Credential |
| Gross Margin | 未确认成本当 Final |
| Model/Tier Economics | 无权限 Supplier Secret Terms |

### Reviewer Focus
1. Revenue / Cost / Margin 是否分别有来源？
2. Estimated 与 Final 是否清楚区分？
3. External capacity cost 是否能解释对 Margin 的影响？

---

## 第二层：机器执行层
- Revenue ← Billing / revenue ledger
- Cost ← verified Provider / local / external compute cost
- Gross Margin ← 仅在 required cost complete 时计算
- Usage ← metering

Revenue 页面默认观察与分析；价格、商业政策和重大成本策略修改必须进入单独 Product / Business Gate。

---

## 第三层：Definition of Done
- [ ] Revenue / Cost / Margin 语义不混用。
- [ ] 成本不完整时不显示虚假 Margin。
- [ ] Estimated / Final 可区分。
- [ ] 金额带币种和时间范围。
- [ ] 通过分支 + Pull Request 合并。
