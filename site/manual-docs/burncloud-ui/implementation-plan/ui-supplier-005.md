---
title: "UI-SUPPLIER-005：实现 Supplier Earnings"
slug: /burncloud-ui/implementation-plan/ui-supplier-005/
---

# UI-SUPPLIER-005：实现 Supplier Earnings

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003 + Earnings Ledger / Contribution / Revenue Share Attribution**

> 产品合同：[/burncloud-ui/supplier/earnings/](/burncloud-ui/supplier/earnings/)

### TL;DR

Earnings 解释 Supplier 收入从哪里来：Contribution、Revenue Share、Estimated Earnings、Final Earnings 必须分开，并可按 Model/Usage/Cluster/Node 下钻。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Period Earnings | 不显示 Buyer private data |
| Contribution | 不显示 Platform Margin |
| Revenue Share read-only | 不显示 other Supplier terms |
| Estimated / Final | 不前端算 payout |

### 审批者关注点（Reviewer Focus）
1. Contribution ≠ Revenue Share ≠ Earnings 是否清楚？
2. Estimated/Final 是否严格区分？
3. earnings 是否能追溯真实 contribution/metering？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 explainable Supplier earnings drilldown，不在 UI 定义 payout/commercial formula。

### 2. Evidence

- TARGET CONFIRMED — Compute Contribution / Revenue Share / Estimated / Final 是不同概念。
- TARGET CONFIRMED — page 不计算 final payout。
- UNKNOWN — Supplier earnings ledger、Contribution engine、authorized Revenue Share config。

### 3. Entry / Starting Point

UI-003；Earnings/Contribution/commercial config/metering services。

### 4. Reuse Targets / Do Not Recreate

Reuse：authoritative metering + future contribution/ledger。  
Do Not Recreate：frontend payout formula、client revenue-share rules、Buyer-cost inference。

### 5. Scope

Allowed：earnings page/time/currency/drilldown。  
Avoid：Contribution engine、Settlement/Payout、Revenue Share modification、platform economics。

### 6. Behavior Contract

**Inputs**：Supplier scope + ledger + contribution + authorized commercial config + attribution。  
**Outputs**：period earnings/explanation/drilldown。  
**Ownership**：backend domains own values；UI presents。  
**Side Effects**：none。

### 7. Failure / Forbidden Fallbacks

Estimated 不变 Final；missing contribution/config => Unknown；禁止 Buyer private data、platform margin、client payout formula。

### 8. Impact / Invariants

Read-only financial surface；Contribution ≠ Revenue Share ≠ Earnings ≠ Paid；final truth ledger-owned。

### 9. Dependencies

UI-003 + Earnings Ledger + Contribution + Revenue Share + resource/model attribution。

### 10. Stop Conditions

STOP IF final earnings 需要 frontend calculation、Buyer private data、或 commercial terms 无 authorization owner。

---

## 第三层：验收层（Definition of Done）

- [ ] earnings trace Contribution。
- [ ] Contribution/Revenue Share separated。
- [ ] Estimated/Final explicit。
- [ ] currency/time explicit。
- [ ] drilldown reconciles totals。
- [ ] Supplier isolation verified。
- [ ] branch + PR。
