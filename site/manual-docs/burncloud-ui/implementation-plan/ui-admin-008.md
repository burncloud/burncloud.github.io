---
title: "UI-ADMIN-008：实现 Admin Settlements"
slug: /burncloud-ui/implementation-plan/ui-admin-008/
---

# UI-ADMIN-008：实现 Admin Settlements

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003、UI-007、UI-008 + Operations Human Gate + Settlement / Payout contracts**

> 产品合同：[/burncloud-ui/admin/settlements/](/burncloud-ui/admin/settlements/)  
> Canonical production route：`/console/admin/settlements`

### TL;DR
Admin Settlements 管 Supplier Payable、Settlement Batch、Processing/Paid/Failed 和 payout Human Gate。付款提交不等于 Paid，部分失败必须保持真实。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| payable/batch/processing/paid/failed | 不 client-compute payable |
| batch preview/approve/reject | 不绕过 Operations audit |
| payout provider verification | 不 HTTP 200=Paid |
| partial failure | 不静默 bulk action |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/admin/settlements` 的 audited settlement/payout decision surface。

### 2. Evidence
- STATIC CONFIRMED — Target requires explicit batch preview, Human Gate and verified provider result。
- UNKNOWN — finalized Supplier earnings、settlement batch/ledger、payout result contracts。

### 3. Entry / Starting Point
UI-ADMIN-006 Operations、future settlement/payout services、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：finalized earnings、settlement ledger、proposal/audit、provider result。  
Do Not Recreate：client payable engine、direct payment provider integration。

### 5. Scope
Allowed：batch review/proposal decision/payment result。  
Avoid：payment engine、earnings computation、unaudited bulk action。

### 6. Behavior Contract
**Inputs**：Admin identity + payable/batch/proposal/provider result + explicit decision + locale。  
**Outputs**：audited settlement lifecycle。  
**Ownership**：Finance/Settlement/Operations services own execution/state。  
**Side Effects**：authorized payout approval/rejection only。

### 7. Failure / Forbidden Fallbacks
Paid requires verified provider/ledger result；partial failures remain partial。禁止 optimistic paid、client payable、direct provider call。

### 8. Impact / Invariants
High-risk financial；route `/console/admin/settlements`；Human Gate/audit mandatory。

### 9. Dependencies
UI-003、007、008 + Admin Operations + finalized earnings/settlement/payout contracts。

### 10. Stop Conditions
STOP IF payable client-computed、batch bypasses Proposal/audit、or Paid lacks verified result。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Admin action authorization/audit verified。
- [ ] Payable/Processing/Paid/Failed distinct。
- [ ] batch preview count/amount/impact explicit。
- [ ] provider result required for Paid。
- [ ] currency/date/status i18n via UI-007；tx IDs stable。
- [ ] branch + PR。
