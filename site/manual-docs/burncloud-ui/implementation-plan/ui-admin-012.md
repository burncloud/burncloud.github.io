---
title: "UI-ADMIN-012：实现 Admin Billing"
slug: /burncloud-ui/implementation-plan/ui-admin-012/
---

# UI-ADMIN-012：实现 Admin Billing

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin / Billing**  
**功能依赖：UI-003、UI-007、UI-008 + Customer Billing / Recharge / Invoice / Policy / Audit contracts**

**Canonical Production Route：`/console/admin/billing`**

### TL;DR

Admin Billing 回答“整个平台客户是如何被收费、充值、欠费和结算账单的”。它不回答平台赚了多少，也不负责给 Supplier 付款。

```text
Admin Billing
= Customer Billing Operations

Admin Revenue
= Revenue / Cost / Margin

Admin Settlements
= Supplier Payable / Payout
```

三者必须保持独立。

### 背景与动机（Why）

Buyer 已有自己的 `/console/buyer/billing`，用于自己的余额、充值、交易与 Invoice。Admin 同样需要平台级 Billing，但它是对所有 Customer Billing 状态、充值订单、欠费、账务异常和 Billing Policy 的管理视图，因此不能复用 Buyer 页面，也不能塞进 Revenue 或 Settlements。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Customer billing account state | 不显示 Buyer-only workspace |
| Recharge / top-up orders | 不计算平台 Gross Margin |
| Invoice / transaction oversight | 不执行 Supplier payout |
| Delinquency / billing anomaly | 不创建前端 ledger |
| Billing policy / limits（有 backend owner 时） | 不绕过 Human Gate / audit |

### 审批者关注点（Reviewer Focus）

1. Admin Billing 是否明确区别于 Revenue 与 Settlements？
2. 所有金额/状态是否来自 authoritative ledger/service？
3. 高风险充值修正、账务调整、Policy 操作是否被授权和审计？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立 `/console/admin/billing`，作为平台 Customer Billing 的 authoritative operations view。

### 2. Evidence

- STATIC CONFIRMED — current production 已有 UserService、balance、admin funding/top-up 等真实能力片段。
- STATIC CONFIRMED — current Billing 页面主要是 authenticated user spend/usage summary，不能直接作为 Admin Billing。
- STATIC CONFIRMED — Admin Customers 已有真实 customer + balance + funding 复用入口。
- UNKNOWN — canonical Customer Billing ledger、recharge order、invoice oversight、delinquency/anomaly、Billing Policy contract 是否完整存在；实现前必须重新 Evidence Audit。

### 3. Entry / Starting Point

```text
crates/client/src/critical_pages/customers_portable.rs
crates/client/src/functional_pages/analytics.rs (evidence/pattern only)
crates/client/src/backend.rs
UserService / Billing / Recharge endpoints
UI-003
UI-007
UI-008
```

### 4. Reuse Targets / Do Not Recreate

Reuse：authoritative User/Balance/Billing/Recharge/Invoice services、existing admin funding authorization、shared financial UI components。

Do Not Recreate：frontend ledger、client billing policy engine、Buyer Billing page copy、Revenue calculator、Supplier Settlement engine。

### 5. Scope

Allowed：Admin customer billing list/detail、recharge orders、transactions/invoices、delinquency/anomaly state、approved billing policy controls、audit/result display。

Avoid：Revenue/Cost/Margin analytics、Supplier payout、payment-provider architecture、ledger redesign。

### 6. Behavior Contract

**Inputs**：Admin identity + customer billing account/ledger/recharge/invoice/policy/audit facts。  
**Outputs**：platform billing state, filters, drilldown, approved high-risk billing actions/results。  
**Ownership**：Billing/User/Payment/Policy services own truth；UI composes。  
**Side Effects**：only explicitly authorized billing operations with audit/verification。

### 7. Failure / Forbidden Fallbacks

- Unknown balance/order/invoice state remains Unknown。
- mutation submission success ≠ ledger applied success；must verify authoritative result。
- partial financial service failure preserves unaffected facts。
- no client-computed debt/revenue/margin。

Forbidden：frontend ledger、optimistic financial success、direct payment-provider call、un-audited balance correction、Revenue/Settlement scope expansion。

### 8. Impact / Invariants

High-risk financial admin surface。Admin authorization + tenant/customer scope + audit required。

保持：

```text
Admin Billing ≠ Admin Revenue ≠ Admin Settlements
Buyer Billing ≠ Admin Billing
Submitted ≠ Applied ≠ Settled
```

### 9. Dependencies

UI-003、UI-007、UI-008 + authoritative Customer Billing / Recharge / Invoice / Policy / Audit contracts。

### 10. Stop Conditions

```text
STOP IF:
- billing truth must be client-computed
- implementation requires reusing Buyer page as Admin authority
- revenue/margin or Supplier payout must be bundled
- high-risk billing mutation lacks audit/verify
- protected path cannot remain /console/admin/billing
- missing backend contracts would be replaced by mock
```

---

## 第三层：验收层（Definition of Done）

- [ ] canonical route = `/console/admin/billing`。
- [ ] Admin WorkspaceGate + Backend Authorization verified。
- [ ] customer billing facts come from authoritative sources。
- [ ] recharge/order/transaction/invoice states are truthful。
- [ ] delinquency/anomaly state does not rely on frontend heuristic unless explicitly approved contract says so。
- [ ] high-risk billing changes are authorized/audited/verified。
- [ ] no Buyer Billing UI reused as permission source。
- [ ] no Revenue/Gross Margin computation introduced。
- [ ] no Supplier Settlement/Payout logic introduced。
- [ ] Loading/Empty/Partial Failure/Error/Recovered covered。
- [ ] i18n/locale-aware financial formatting follows UI-007。
- [ ] branch + PR。
