---
title: "UI-BUYER-006：实现 Buyer Billing"
slug: /burncloud-ui/implementation-plan/ui-buyer-006/
---

# UI-BUYER-006：实现 Buyer Billing

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Buyer**  
**功能依赖：UI-003 + Balance/Payment/Transaction/Invoice contracts**

> 产品合同：[/burncloud-ui/buyer/billing/](/burncloud-ui/buyer/billing/)

### TL;DR

Buyer Billing 管余额、充值、交易、发票和支持的消费控制。账本和 payment result 是唯一金融真相；HTTP 200、前端 state 或 admin balance-mint endpoint 都不能代表 Buyer 已付款。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Balance / Transactions | 不做 Supplier Settlement |
| user-initiated Top Up | 不用 admin topup 模拟支付 |
| Invoices / Receipts | 不 optimistic Paid |
| Spend Controls（若支持） | 不前端记账 |

### 审批者关注点（Reviewer Focus）
1. Pending/Paid/Failed 是否来自真实 payment/ledger？
2. Buyer 是否始终主动发起资金动作？
3. admin topup 是否仍保持 Admin-only？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立 Buyer-safe financial page，显示真实 Balance/Payment/Transactions/Documents。

### 2. Evidence

- STATIC CONFIRMED — current Billing page 是 billed usage analytics，不是 wallet/payment page。
- STATIC CONFIRMED — `/api/billing/summary` 不等于完整 Balance/Payment contract。
- STATIC CONFIRMED — user accounts 有 balance fields。
- STATIC CONFIRMED — security test 证明 normal user 禁止 `/console/api/user/topup`，该 endpoint 不能复用作 Buyer payment。
- UNKNOWN — Buyer payment/provider result、transaction ledger、invoice、spend-control contracts。

### 3. Entry / Starting Point

`functional_pages/analytics.rs::Billing`（pattern only）、billing summary、user account balance evidence、future Buyer payment services。

### 4. Reuse Targets / Do Not Recreate

Reuse：authoritative ledger structures / billed summary / financial UI states。  
Do Not Recreate：frontend wallet ledger、admin topup payment、client payment processor、fake invoice。

### 5. Scope

Allowed：Buyer Billing page + approved Buyer-safe financial clients。  
Avoid：payment/ledger architecture、Admin/Supplier settlements、direct DB balance mutation。

### 6. Behavior Contract

**Inputs**：Buyer + explicit Top Up/control action + ledger/payment/document facts。  
**Outputs**：Balance/transaction/payment/document state。  
**Ownership**：financial backend owns truth；UI owns human intent/confirmation。  
**Side Effects**：real user-initiated financial action only when backend exists。

### 7. Failure / Forbidden Fallbacks

Payment submission failure 不改余额；Pending/Delayed/Unknown 不显示 Paid；invoice failure 不覆盖 ledger facts。禁止 admin topup、optimistic state、client receipt。

### 8. Impact / Invariants

Direct financial surface；tenant scoped；Pending ≠ Paid；Autopilot 不发起资金动作。

### 9. Dependencies

UI-003 + Balance read + Buyer payment + transaction + invoice + supported spend controls。

### 10. Stop Conditions

STOP IF admin topup 被提议当 payment，Paid 只能从 HTTP 200 推断，financial data 无 backend owner，或需要 UI direct DB mutation。

---

## 第三层：验收层（Definition of Done）

- [ ] Balance matches authoritative ledger。
- [ ] Top Up uses real Buyer payment flow。
- [ ] Pending/Paid/Failed authoritative。
- [ ] Transactions/Invoices authoritative。
- [ ] currency/time/status explicit。
- [ ] cross-tenant denied。
- [ ] admin topup security invariant preserved。
- [ ] branch + PR。
