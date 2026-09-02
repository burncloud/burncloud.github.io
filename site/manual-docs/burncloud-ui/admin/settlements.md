---
title: "Admin Settlements"
slug: /burncloud-ui/admin/settlements/
---

# Admin Settlements

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Admin Settlements 统一管理 Supplier Payable、Processing、Paid、Failed 和 Settlement Batch。涉及付款的动作必须对明确 Proposal 做审批，并完整记录 actor、time、amount、input 和 result。

### Primary Question
> **平台需要向哪些 Supplier 支付多少钱？状态如何？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Total Payable | 假 Paid 状态 |
| Settlement Batches | 无审计批量支付 |
| Supplier / Period | Buyer Payment Secret |
| Failed / Payout Result | 未授权 Supplier Terms |

### Reviewer Focus
1. Payable / Processing / Paid 是否严格分离？
2. 批量付款前是否明确选择数量、总金额与影响？
3. 执行后是否有真实 Verify，而不是 API 200 即 Success？

---

## 第二层：机器执行层
- Settlement batches ← Settlement ledger
- Final supplier earnings ← Earnings / Contribution engine
- Payout result ← payment provider
- Approval / actor / audit ← audit trail

### Human Gate
付款属于高风险动作：必须显示对象、总额、原因、影响范围、是否可撤销，并记录 Approve/Reject 与最终 payout result。

---

## 第三层：Definition of Done
- [ ] Payable / Processing / Paid / Failed 状态完整。
- [ ] 批量操作有 count / amount / impact preview。
- [ ] Payment result 可验证。
- [ ] Approval audit 完整。
- [ ] 通过分支 + Pull Request 合并。
