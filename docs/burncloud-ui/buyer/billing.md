---
title: "Buyer Billing"
slug: /burncloud-ui/buyer/billing/
---

# Buyer Billing

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Billing 负责 Balance、Top Up、Transactions、Invoices 和适用的 Spend Controls。资金状态必须以 Billing Ledger / Payment Result 为最终真相，不能在前端乐观更新成 Paid。

### Primary Question
> **我的余额、充值和账单现在是什么状态？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Balance | Supplier Settlement |
| Top Up / Transactions | Platform Revenue |
| Invoices / Receipts | Provider Cost |
| Spend Limit | 假支付成功 |

### Reviewer Focus
1. Balance 是否来自后端账本，而不是前端 state？
2. Top Up 是否始终由 Buyer 主动发起？
3. Pending / Paid / Failed 是否使用真实支付结果？

---

## 第二层：机器执行层

### Production Mapping
- Balance / Transactions ← Billing ledger
- Top Up state ← Payment flow
- Invoice / Receipt ← Invoice service
- Spend Limit ← Backend policy

### Financial Truth
- 金额必须带币种。
- Pending 不等于 Paid。
- Payment API 返回 200 不自动等于到账。
- Partial Failure 时，Balance 成功加载就继续显示；Invoice 子服务失败只标对应部分不可用。

### Human Gate
充值、支付和高风险消费控制是用户资金动作，不由 Autopilot 自行执行。

---

## 第三层：Definition of Done
- [ ] Balance 与账本一致。
- [ ] Top Up failure 不显示到账。
- [ ] Pending / Paid / Failed 已验证。
- [ ] 金额、币种、时间范围明确。
- [ ] React `setBalance()` 等 mock 行为已消失。
- [ ] 通过分支 + Pull Request 合并。
