---
title: "UI-ADMIN-007：实现 Admin Revenue"
slug: /burncloud-ui/implementation-plan/ui-admin-007/
---

# UI-ADMIN-007：实现 Admin Revenue

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003 + Platform Revenue Ledger / Verified Cost / Attribution**

> 产品合同：[/burncloud-ui/admin/revenue/](/burncloud-ui/admin/revenue/)

### TL;DR

Revenue 解释平台 Revenue、Verified Cost、Gross Margin 从哪里来，并按 Model/Tier/Customer Segment/时间下钻。Cost 不完整时必须显示 Unknown/Estimated，不能制造虚假精确毛利。

### 背景与动机（Why）

Buyer billing summary 是用户消费事实，不等于平台 Revenue；Router log cost 是成本证据片段，也不自动等于 verified total cost。Admin Revenue 必须建立在独立 authoritative economics facts 上。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Revenue / Verified Cost | 不把 Buyer spend 当平台 ledger |
| Gross Margin | 不猜 local/provider cost |
| Model/Tier/Segment drilldown | 不显示无权限 Supplier secret terms |
| Estimated / Final | 不前端写 margin engine |

### 审批者关注点（Reviewer Focus）
1. Revenue/Cost/Margin 是否分别有 source？
2. cost completeness 是否决定能否显示 final Margin？
3. External capacity cost 是否能解释 margin impact？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 authoritative platform economics analysis，不在 UI 合成 Revenue/Cost/Margin truth。

### 2. Evidence

- STATIC CONFIRMED — current `/api/billing/summary` 是 user-scoped spend/cost，不是 platform Revenue ledger。
- STATIC CONFIRMED — router logs 有 request cost components，但不等于完整 verified Provider/local/external cost。
- TARGET CONFIRMED — cost incomplete 时禁止 precise Gross Margin。
- UNKNOWN — platform Revenue ledger、verified cost ledger、customer-segment economics attribution。

### 3. Entry / Starting Point

UI-003 Admin workspace；Metering/Billing evidence fragments；future Revenue/Cost/Economics services。

### 4. Reuse Targets / Do Not Recreate

Reuse：authoritative metering/revenue facts + verified compute/provider costs。  
Do Not Recreate：frontend ledger、Buyer spend summation as revenue、guessed local GPU cost、client final margin engine。

### 5. Scope

Allowed：Revenue page/filter/drilldown/completeness/finality presentation。  
Avoid：Revenue/Cost ledger engine、pricing policy mutation、Supplier settlement/payment actions。

### 6. Behavior Contract

**Inputs**：Admin + Revenue ledger + verified Cost + attribution + completeness/finality metadata。  
**Outputs**：Revenue/Cost/Margin totals/trends/drilldowns。  
**Ownership**：Economics backend owns financial facts；UI presents。  
**Side Effects**：read-only；pricing/business change 属于单独 Product/Business Gate。

### 7. Failure / Forbidden Fallbacks

Incomplete cost → Margin Unknown/Estimated with reason；Revenue source failure 不 fallback Buyer spend；禁止 unauthorized Supplier terms 和 client cost formula。

### 8. Impact / Invariants

Read-only high-value financial analytics；Revenue ≠ Cost ≠ Margin；Estimated ≠ Final；Margin only if cost completeness supports it。

### 9. Dependencies

UI-003 + platform Revenue ledger + verified Provider/local/external Cost + completeness/finality + Model/Tier/Segment attribution。

### 10. Stop Conditions

STOP IF platform Revenue 必须从 Buyer page 重建、cost 需要猜测、final Margin 缺完整 verified costs，或 sensitive commercial details 无授权。

---

## 第三层：验收层（Definition of Done）

- [ ] Revenue/Cost/Margin separate authoritative sources。
- [ ] incomplete cost never fake precise Margin。
- [ ] Estimated/Final explicit。
- [ ] currency/time explicit。
- [ ] drilldowns reconcile totals。
- [ ] external capacity cost impact explainable safely。
- [ ] branch + PR。
