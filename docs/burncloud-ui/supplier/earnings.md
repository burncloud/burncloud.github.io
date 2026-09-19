---
title: "Supplier Earnings"
slug: /burncloud-ui/supplier/earnings/
---

# Supplier Earnings

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Earnings 解释 Supplier 收入从哪里来，并允许按 **Revenue → Model → Usage → Cluster / Node** 下钻。页面必须区分 Compute Contribution、Revenue Share、Estimated Earnings 与 Final Earnings。

### Primary Question
> **这些收入是怎么来的？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Period Earnings | Buyer private data |
| Contribution | Platform Gross Margin |
| Revenue Share | 其它 Supplier 商业比例 |
| Model / Resource breakdown | 未结算金额伪装 Paid |

### Reviewer Focus
1. Contribution 与 Revenue Share 是否分离？
2. Estimated 与 Final 是否分离？
3. 收益能否追溯真实 usage / contribution？

---

## 第二层：机器执行层
- Earnings ← Supplier earnings ledger
- Contribution ← Contribution engine
- Revenue Share ← authorized supplier commercial config
- Model / Usage / Resource breakdown ← metering + contribution facts

UI 不自行计算最终 payout，不用前端公式替代账本。Revenue Share 属于商业配置，普通 Supplier 页面只读展示。

---

## 第三层：Definition of Done
- [ ] Earnings 可追溯到 Contribution。
- [ ] Revenue Share / Contribution 语义不混用。
- [ ] Estimated / Final 明确区分。
- [ ] 金额带币种和时间范围。
- [ ] 通过分支 + Pull Request 合并。
