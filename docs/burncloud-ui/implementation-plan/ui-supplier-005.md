---
title: "UI-SUPPLIER-005：实现 Supplier Earnings"
slug: /burncloud-ui/implementation-plan/ui-supplier-005/
---

# UI-SUPPLIER-005：实现 Supplier Earnings

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003、UI-007、UI-008 + Contribution / Earnings Ledger contract**

> 产品合同：[/burncloud-ui/supplier/earnings/](/burncloud-ui/supplier/earnings/)  
> Canonical production route：`/console/supplier/earnings`

### TL;DR
Earnings 解释 Supplier 的 Contribution 如何形成收入，并区分 Gross Contribution Value、Revenue Share、Estimated Earnings、Finalized Earnings；不在 UI 用 GPU 时长乘一个价格算钱。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| earnings totals/trends | 不 client-compute payout |
| by node/model/period | 不把 payable 当 paid |
| Estimated vs Final | 不猜 revenue share |
| currency-aware formatting | 不显示其他 Supplier terms |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/supplier/earnings` 的 authoritative earnings explanation。

### 2. Evidence
- STATIC CONFIRMED — Target 要求 Contribution、Revenue Share、Earnings、Settlement 分离。
- UNKNOWN — current-main Supplier contribution/earnings ledger contracts。

### 3. Entry / Starting Point
future Contribution/Earnings services、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：Contribution facts、earnings ledger、settlement references、shared money/date formatter。  
Do Not Recreate：client earnings engine、GPU-hour formula、settlement ledger。

### 5. Scope
Allowed：earnings read analytics/explanations/export where supported。  
Avoid：payout execution、commercial policy design、Admin financial details。

### 6. Behavior Contract
**Inputs**：Supplier identity + contribution/earnings records + finality + locale。  
**Outputs**：earnings totals/trends/breakdown/finality。  
**Ownership**：Finance/Contribution services own values。  
**Side Effects**：read/export only。

### 7. Failure / Forbidden Fallbacks
Missing finality → Estimated/Unknown；Payable/Paid 不得由 UI 推导。禁止 client formula、cross-supplier data。

### 8. Impact / Invariants
Financial read-only；route `/console/supplier/earnings`；Estimated != Final。

### 9. Dependencies
UI-003、007、008 + Contribution/Earnings ledger。

### 10. Stop Conditions
STOP IF earnings requires client math、revenue share guessed、or authoritative finality unavailable。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Supplier-only financial scope。
- [ ] Contribution/Earnings/Payable/Paid concepts separated。
- [ ] Estimated/Final explicit。
- [ ] currency/date/number use UI-007 formatter。
- [ ] no client payout formula。
- [ ] branch + PR。
