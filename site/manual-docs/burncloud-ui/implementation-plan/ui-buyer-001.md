---
title: "UI-BUYER-001：实现 Buyer Overview"
slug: /burncloud-ui/implementation-plan/ui-buyer-001/
---

# UI-BUYER-001：实现 Buyer Overview

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Buyer**  
**功能依赖：UI-003、UI-007、UI-008 + Buyer Balance / Availability contracts**

> 产品合同：[/burncloud-ui/buyer/overview/](/burncloud-ui/buyer/overview/)  
> Canonical production route：`/console/buyer/overview`（以 UI-008 为最终事实源）

### TL;DR

Buyer 首页只回答“今天花了多少、还有多少余额、API 是否稳定、今天用了多少 Token”。不让 Buyer 理解 GPU、Supplier、Provider 或内部 Route。

### 背景与动机（Why）

current Overview 已能读取真实 usage/billing/logs/channels/tokens/system metrics，但它是混合 operator/setup dashboard。Buyer Overview 必须重组成消费与服务结果视角。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Today Spend / Balance | 不显示 GPU/IDC/Supplier |
| API Availability / Tokens Today | 不显示 Provider/Route config |
| Models in Use / Recent Activity | 不在前端推导账本 |
| localized truthful states | 不让 locale 改权限/路径 |

### 审批者关注点（Reviewer Focus）
1. 四个指标是否都是 Buyer 自己的数据？
2. Unknown 是否不会显示成 `$0`？
3. `/console/buyer/overview` 是否只对 backend-authorized Buyer workspace 可见？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 Buyer-only Overview composition，首屏优先 `today_spend / balance / api_availability / tokens_today`。

### 2. Evidence
- STATIC CONFIRMED — current Overview 已读取 user-scoped usage/billing 等真实数据。
- STATIC CONFIRMED — user account 存在 balance fields。
- UNKNOWN — Buyer-safe current balance read contract 是否满足目标页面。
- UNKNOWN — authoritative Buyer-facing API availability contract。

### 3. Entry / Starting Point
`critical_pages/dashboard.rs::Overview`、`backend::billing_summary`、`backend::user_usage`、UI-003/007/008。Route 必须来自 UI-008。

### 4. Reuse Targets / Do Not Recreate
Reuse：existing billing/usage resources、overview state patterns、auth context、shared i18n/formatter。  
Do Not Recreate：client ledger、Provider-derived availability、mock dashboard、page-local formatter。

### 5. Scope
Allowed：Buyer Overview composition、read-only Buyer APIs、canonical navigation。  
Avoid：payment backend、billing semantics、Router/Provider changes、Supplier/Admin metrics。

### 6. Behavior Contract
**Inputs**：authenticated + Buyer-authorized identity、scoped usage/billing/balance/availability、locale。  
**Outputs**：四核心指标、models/activity、low-balance action state。  
**Ownership**：backend domain services own facts；UI composes/localizes。  
**Side Effects**：read-only/navigation。

### 7. Failure / Forbidden Fallbacks
Loading 不先显示 0；source failure 只影响对应 metric；missing backend contract 阻塞而不是读 raw Provider/GPU。禁止 URL/locale 获权。

### 8. Impact / Invariants
Read-only Buyer data；tenant scope server-side；route `/console/buyer/overview`；machine identifiers 不翻译。

### 9. Dependencies
UI-003、UI-007、UI-008；Buyer-safe Balance；Buyer-facing Availability。

### 10. Stop Conditions
STOP IF metric 必须由 Provider/GPU/client formula 推导、tenant isolation 不能 server-side 验证、route 需要绕过 UI-008、或缺失事实只能靠 mock。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Buyer workspace authorization 与 API tenant scope 均验证。
- [ ] Today Spend / Balance / Availability / Tokens Today 有 authoritative source。
- [ ] GPU/Supplier/IDC/Runtime/Provider config 不出现。
- [ ] Loading/Empty/Partial Failure/Error/Recovered truthful。
- [ ] 用户可见文案走 UI-007；金额/数字使用 locale formatter。
- [ ] locale 不改变 route/permission。
- [ ] branch + PR。
