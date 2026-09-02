---
title: "UI-BUYER-005：实现 Buyer Usage"
slug: /burncloud-ui/implementation-plan/ui-buyer-005/
---

# UI-BUYER-005：实现 Buyer Usage

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Buyer**  
**功能依赖：UI-003 + Tier/API Key/Date attribution + Buyer Logs**

> 产品合同：[/burncloud-ui/buyer/usage/](/burncloud-ui/buyer/usage/)

### TL;DR

Usage 解释 Buyer 的 Requests、Tokens、Cost 到底用在哪里，并按 Model/Tier/API Key/时间下钻。它不是 GPU、Supplier 或 Provider Cost 分析页。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Requests/Tokens/Cost | 不算 GPU utilization |
| Model/Tier/API Key breakdown | 不显示 Supplier earnings |
| Date/Search/Filter | 不显示 provider cost |
| drilldown to Logs | 不在前端重算 billing |

### 审批者关注点（Reviewer Focus）
1. total 与 breakdown 是否 reconcile？
2. currency/time/Estimated/Final 是否明确？
3. API Key 维度是否只用 metadata？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 Buyer-scoped authoritative consumption analysis 与安全 drilldown。

### 2. Evidence

- STATIC CONFIRMED — `billing_summary` 提供 user-scoped model-level requests/tokens/cost。
- STATIC CONFIRMED — `user_usage` 与 current Billing page 已消费真实 metering。
- UNKNOWN — authoritative Tier attribution。
- UNKNOWN — Buyer-safe API-key usage attribution。
- UNKNOWN — 所需 date-range semantics 是否完整。

### 3. Entry / Starting Point

`functional_pages/analytics.rs::Billing`、`backend::billing_summary`、`backend::user_usage`、Buyer Logs。

### 4. Reuse Targets / Do Not Recreate

Reuse：existing metering/billing、canonical model identity、safe API key metadata。  
Do Not Recreate：client final totals、client pricing engine、admin logs summation、secret display。

### 5. Scope

Allowed：Usage page、authoritative read adapters、filter/date/drilldown。  
Avoid：pricing/billing semantics、Provider/Supplier cost、admin observability access。

### 6. Behavior Contract

**Inputs**：Buyer + time/filter + authoritative usage/billing breakdown。  
**Outputs**：totals/breakdowns + Logs links。  
**Ownership**：Metering/Billing own values；UI owns presentation。  
**Side Effects**：read-only。

### 7. Failure / Forbidden Fallbacks

Breakdown failure 不清空 confirmed total；Unknown attribution 不 client-infer；sorting/filtering 不改金额/token 语义。

### 8. Impact / Invariants

Read-only analytics；tenant scoped；Estimated ≠ Final；API key = metadata only。

### 9. Dependencies

UI-003 + Tier/API-key/date attribution + Buyer Logs destination。

### 10. Stop Conditions

STOP IF final totals 必须从 admin logs client-side 重建，breakdown 无 authoritative owner，或页面必须暴露 provider/supplier costs/secrets。

---

## 第三层：验收层（Definition of Done）

- [ ] Requests/Tokens/Cost authoritative。
- [ ] Model/Tier/API Key/time breakdown reconcile。
- [ ] currency/time/Estimated/Final explicit。
- [ ] partial failure preserves confirmed totals。
- [ ] anomaly can drill to Buyer Logs。
- [ ] no GPU/Supplier/Provider cost data。
- [ ] branch + PR。
