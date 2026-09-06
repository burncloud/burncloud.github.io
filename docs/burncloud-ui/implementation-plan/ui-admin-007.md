---
title: "UI-ADMIN-007：实现 Admin Revenue"
slug: /burncloud-ui/implementation-plan/ui-admin-007/
---

# UI-ADMIN-007：实现 Admin Revenue

<!-- UI-ARCHITECTURE-DEPENDENCY: REQUIRED -->
> **Mandatory Architecture Dependency（强制）**
>
> 本实施单元必须遵守 [BurnCloud UI Architecture Contract](/burncloud-ui/architecture/)。Architecture Contract 是本页、READY Engineering Issue、Task Contract 与 Production Dioxus 实现的上位约束。
>
> - 实施前必须读取 [Directory Contract](/burncloud-ui/architecture/directory-contract/)、[Authorization Contract](/burncloud-ui/architecture/authorization-contract/)、[API Boundary](/burncloud-ui/architecture/api-boundary/) 与 [Code Ownership](/burncloud-ui/architecture/code-ownership/) 中适用规则；
> - Task Contract 必须明确 `Allowed Paths / Conditional Paths / Forbidden Paths`；
> - 本页只能增加更严格的限制，**不能放宽 Architecture Contract**；
> - 若页面需求与 Architecture Contract 冲突，必须 `STOP → Architecture Dependency / Foundation Issue`，不得由 AI/Codex 自行扩大 scope 或修改 Protected Architecture Zone。
>
> `Implementation convenience != architecture authority`；`CI green != permission to violate the Architecture Contract`。
<!-- UI-ARCHITECTURE-DEPENDENCY: END -->

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003、UI-007、UI-008 + Revenue / Verified Cost / Completeness contracts**

> 产品合同：[/burncloud-ui/admin/revenue/](/burncloud-ui/admin/revenue/)  
> Canonical production route：`/console/admin/revenue`

### TL;DR
Revenue 展示平台 Revenue、Verified Cost、Gross Margin，并明确 currency/time/finality/completeness。缺成本时不能显示假精确 Margin。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| revenue/cost/margin | 不把 Buyer spend 直接当 platform revenue |
| model/tier/segment drilldown | 不猜 local GPU cost |
| Estimated/Final/completeness | 不显示不完整精确 margin |
| currency/time formatting | 不泄露 unauthorized Supplier terms |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/admin/revenue` 的 authoritative platform economics view。

### 2. Evidence
- STATIC CONFIRMED — current billing/logs have financial evidence fragments but not full platform economics ledger。
- UNKNOWN — platform Revenue ledger、verified Provider/local/external cost、completeness metadata。

### 3. Entry / Starting Point
future Revenue/Cost services、existing metering/billing evidence、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：ledger revenue facts、verified cost facts、product identity、shared financial formatter。  
Do Not Recreate：client margin engine、cost guesses。

### 5. Scope
Allowed：read-only economics totals/trends/drilldowns/completeness explanation。  
Avoid：pricing policy、ledger engine、Supplier payout。

### 6. Behavior Contract
**Inputs**：Admin identity + revenue/cost/completeness/finality + locale。  
**Outputs**：Revenue/Cost/Margin analytics。  
**Ownership**：Finance services own values。  
**Side Effects**：read-only。

### 7. Failure / Forbidden Fallbacks
Incomplete cost → Margin unavailable/estimated, never fake precise。禁止 Buyer-spend proxy、local GPU cost guess。

### 8. Impact / Invariants
Financial read-only；route `/console/admin/revenue`；Revenue != Cost != Margin；Estimated != Final。

### 9. Dependencies
UI-003、007、008 + Revenue/Verified Cost/completeness contracts。

### 10. Stop Conditions
STOP IF revenue/cost must be reconstructed client-side、required costs incomplete but precise margin expected、or supplier secrets exposed。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Revenue/Cost separate authoritative sources。
- [ ] incomplete cost never yields fake precise Margin。
- [ ] Estimated/Final/currency/time explicit。
- [ ] locale formatting via UI-007；ledger/reference IDs stable。
- [ ] branch + PR。
