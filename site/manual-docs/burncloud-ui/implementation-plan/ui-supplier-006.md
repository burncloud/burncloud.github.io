---
title: "UI-SUPPLIER-006：实现 Supplier Settlements"
slug: /burncloud-ui/implementation-plan/ui-supplier-006/
---

# UI-SUPPLIER-006：实现 Supplier Settlements

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003 + Final Earnings / Settlement Ledger / Payout Result**

> 产品合同：[/burncloud-ui/supplier/settlements/](/burncloud-ui/supplier/settlements/)

### TL;DR

Supplier 必须能区分 Estimated、Payable、Processing、Paid、Failed。Payment API 提交成功不等于 Paid，只有 payout/ledger 真实确认才能变 Paid。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Payable/Processing/Paid/Failed | 不显示 Buyer Billing |
| Settlement Period | 不前端算 Payable |
| Payout Method Summary | 不 optimistic Paid |
| Statement/Receipt | 不看 other Supplier payout |

### 审批者关注点（Reviewer Focus）
1. Payable 与 Paid 是否完全分离？
2. Failed 是否有原因/下一步？
3. payout result 是否可审计？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 Supplier-scoped authoritative settlement status/history。

### 2. Evidence

- TARGET CONFIRMED — Payable/Processing/Paid/Failed + period + payout summary。
- TARGET CONFIRMED — API success ≠ Paid。
- UNKNOWN — Settlement ledger、finalized earnings、payout-provider state、statement/receipt source。

### 3. Entry / Starting Point

UI-003；final earnings；settlement ledger；payout provider；document source。

### 4. Reuse Targets / Do Not Recreate

Reuse：authoritative financial ledger/results。  
Do Not Recreate：frontend settlement ledger、client-computed payable、Buyer billing semantics。

### 5. Scope

Allowed：settlement list/detail/status/documents。  
Avoid：payout integration、ledger implementation、Admin batch payment。

### 6. Behavior Contract

**Inputs**：Supplier scope + finalized earnings + settlement/payout/document facts。  
**Outputs**：settlement states/history。  
**Ownership**：financial backend owns truth；UI presents。  
**Side Effects**：none by default；任何 payout action 必须独立 Human Gate。

### 7. Failure / Forbidden Fallbacks

Unknown/delayed != Paid；document failure 不重写 settlement state；禁止 client payable/optimistic payment/other Supplier records。

### 8. Impact / Invariants

Financial read surface；Estimated ≠ Payable ≠ Processing ≠ Paid；Paid requires verified result。

### 9. Dependencies

UI-003 + finalized earnings + settlement ledger + payout result + document source。

### 10. Stop Conditions

STOP IF payable/Paid 必须 client-derived、payout 不能 verify、或 cross-Supplier isolation 不是 server-side。

---

## 第三层：验收层（Definition of Done）

- [ ] all financial states authoritative。
- [ ] Paid only follows verified result。
- [ ] currency/period explicit。
- [ ] failure/next step truthful。
- [ ] cross-Supplier isolation verified。
- [ ] document partial failure safe。
- [ ] branch + PR。
