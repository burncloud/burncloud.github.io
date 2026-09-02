---
title: "UI-ADMIN-008：实现 Admin Settlements"
slug: /burncloud-ui/implementation-plan/ui-admin-008/
---

# UI-ADMIN-008：实现 Admin Settlements

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003、UI-ADMIN-006 + Final Supplier Earnings / Settlement / Payout**

> 产品合同：[/burncloud-ui/admin/settlements/](/burncloud-ui/admin/settlements/)

### TL;DR

Admin Settlements 管 Supplier Payable、Settlement Batch、Processing/Paid/Failed。付款属于高风险动作，必须先明确对象、数量、总额、影响，再进入 Proposal Approve/Reject；最终 Paid 只能来自真实 payout/ledger Verify。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Total Payable / Supplier / Period | 不 client-compute payable |
| Settlement Batch preview | 不 silent bulk payment |
| Proposal Approve/Reject | 不 API 200 = Paid |
| Payout Verify/Audit | 不直接调 provider 绕过 gate |

### 审批者关注点（Reviewer Focus）
1. batch 是否有 count/amount/impact preview？
2. Approve/Reject 是否审计 actor/time/input？
3. Partial payout failure 是否保持真实状态？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立高风险 Supplier settlement review/execution transparency，并复用 Operations Human Gate。

### 2. Evidence

- TARGET CONFIRMED — Payable/Processing/Paid/Failed 分离。
- TARGET CONFIRMED — batch payment 需要 preview、approval、audit、provider Verify。
- UNKNOWN — Settlement ledger、final Supplier Earnings、Batch service、payout-provider result、Proposal approval/audit contracts。

### 3. Entry / Starting Point

UI-003；UI-ADMIN-006 Operations；final Supplier Earnings；Settlement ledger/Batch；Payout result。

### 4. Reuse Targets / Do Not Recreate

Reuse：final earnings、settlement ledger、Operations Proposal/audit、payment result。  
Do Not Recreate：client payable formula、unaudited bulk payment、direct provider call、optimistic Paid。

### 5. Scope

Allowed：Admin settlement list/batch review/proposal decision/result。  
Avoid：payment provider integration、ledger engine、Earnings engine、generic Operations engine。

### 6. Behavior Contract

**Inputs**：Admin + payable/settlement/batch/proposal/approval/provider result。  
**Outputs**：batch/payment state + audit trail。  
**Ownership**：Settlement/Payout own execution/truth；Operations/Policy own gate；UI presents explicit decision。  
**Side Effects**：authorized Proposal Approve/Reject only。

### 7. Failure / Forbidden Fallbacks

HTTP 200 != Paid；partial batch failure stays partial/failed/processing；no retry unless backend semantics explicitly allow it。禁止 client ledger/direct payment/silent bulk action。

### 8. Impact / Invariants

High-risk financial transaction surface；Payable ≠ Processing ≠ Paid；Human by Exception；Verify mandatory。

### 9. Dependencies

UI-003 + UI-ADMIN-006 + final Supplier Earnings + Settlement ledger/Batch + Payout result。

### 10. Stop Conditions

STOP IF payable 需 client-compute、payment bypasses Proposal/audit、Paid 无 provider/ledger verification、或 retry semantics 不明确。

---

## 第三层：验收层（Definition of Done）

- [ ] Payable/Processing/Paid/Failed separated。
- [ ] batch preview count/amount/impact complete。
- [ ] Approve/Reject authorized/audited。
- [ ] Paid only after verified payout result。
- [ ] partial/failed batch truthful。
- [ ] no silent payment path。
- [ ] branch + PR。
