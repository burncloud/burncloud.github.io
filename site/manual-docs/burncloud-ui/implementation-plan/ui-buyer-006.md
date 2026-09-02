---
title: "UI-BUYER-006：实现 Buyer Billing"
slug: /burncloud-ui/implementation-plan/ui-buyer-006/
---

# UI-BUYER-006：实现 Buyer Billing

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Buyer**  
**功能依赖：UI-003、UI-007、UI-008 + Balance / Transactions / Payment / Invoice contracts**

> 产品合同：[/burncloud-ui/buyer/billing/](/burncloud-ui/buyer/billing/)  
> Canonical production route：`/console/buyer/billing`

### TL;DR
Buyer Billing 管理余额、充值、交易、发票和支持的 spend controls。它不等于 current `/billing` 的 spend analytics，因此 legacy `/billing` 不能在 semantic parity 前直接重定向到本页。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| balance/transactions/invoices | 不拿 Usage 页面当 ledger |
| explicit Add Funds | 不自动 top-up without contract |
| payment result truth | 不用 Admin topup 伪装 Buyer payment |
| currency-aware formatting | 不猜汇率/币种 |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/buyer/billing` 的 Buyer financial management surface。

### 2. Evidence
- STATIC CONFIRMED — current Billing 页面读取 user-scoped billed spend/usage，语义偏 analytics。
- STATIC CONFIRMED — Admin customer funding/topup 能力不等同 Buyer payment flow。
- UNKNOWN — Buyer payment methods/transactions/invoices/auto-topup contracts。

### 3. Entry / Starting Point
existing billing summary patterns、future authoritative financial services、UI-003/007/008；legacy `/billing` 由 UI-005/008 管理。

### 4. Reuse Targets / Do Not Recreate
Reuse：authoritative balance/ledger/payment/invoice services、shared money formatter。  
Do Not Recreate：client ledger、fake payment method、Admin topup as Buyer payment。

### 5. Scope
Allowed：balance/transactions/invoices/payment actions supported by backend。  
Avoid：ledger/payment provider architecture、usage metering semantics、admin funding workflow。

### 6. Behavior Contract
**Inputs**：Buyer identity + financial ledger/payment facts + explicit user action + locale。  
**Outputs**：balance/history/invoices and verified payment result。  
**Ownership**：Financial services own money/state。  
**Side Effects**：explicit payment/funding actions only when authoritative contract exists。

### 7. Failure / Forbidden Fallbacks
Payment submit/HTTP 200 != settled funds；failed transaction 不 optimistic balance。禁止 client balance math、fake payment、legacy `/billing` silent semantic rewrite。

### 8. Impact / Invariants
Financial high-risk；currency/finality explicit；route `/console/buyer/billing`。

### 9. Dependencies
UI-003、007、008 + Buyer financial contracts；UI-005 handles legacy migration after parity。

### 10. Stop Conditions
STOP IF Buyer payment 必须复用 Admin topup 无审计、余额需前端计算、或 current legacy `/billing` 被要求直接等价本页。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] balance/transaction/invoice 有 authoritative source。
- [ ] payment result/finality truthful。
- [ ] unauthorized tenant/account access denied。
- [ ] USD/CNY/date/time 使用 UI-007 formatter。
- [ ] legacy `/billing` 在 UI-005 前不强制改语义。
- [ ] branch + PR + financial failure tests。
