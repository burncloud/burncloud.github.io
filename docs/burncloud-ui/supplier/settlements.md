---
title: "Supplier Settlements"
slug: /burncloud-ui/supplier/settlements/
---

# Supplier Settlements

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Settlements 负责告诉 Supplier：**哪些收益已经可结算、哪些正在处理、哪些已经支付、哪些失败。** Payable、Processing、Paid、Failed 必须由真实 Settlement / Payout 状态决定。

### Primary Question
> **哪些收益可以结算？哪些已经支付？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Payable Amount | Buyer Billing |
| Settlement Period | Platform Margin |
| Processing / Paid / Failed | 其它 Supplier Payout |
| Payout Method Summary | 前端乐观 Paid |

### Reviewer Focus
1. Payable 与 Paid 是否严格分离？
2. Failed 是否说明原因与下一步？
3. 金额和结算周期是否可审计？

---

## 第二层：机器执行层
- Settlement ← Settlement ledger
- Payable ← finalized Supplier earnings
- Payout Status ← payout provider / financial backend
- Statement / Receipt ← settlement document source

### Financial Truth
API 成功提交付款不等于 Paid。只有 payout/ledger 确认后才能显示 Paid。Unknown/Delayed 不能转成成功。

高风险金融操作按商业规则进入 Human Gate；Supplier 不能修改其它 Supplier 的 Settlement。

---

## 第三层：Definition of Done
- [ ] Estimated / Payable / Processing / Paid / Failed 状态完整。
- [ ] Paid 只来自真实 payout result。
- [ ] 金额、币种、周期明确。
- [ ] 跨 Supplier 数据隔离通过。
- [ ] 通过分支 + Pull Request 合并。
