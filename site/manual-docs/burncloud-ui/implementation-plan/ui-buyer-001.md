---
title: "UI-BUYER-001：实现 Buyer Overview"
slug: /burncloud-ui/implementation-plan/ui-buyer-001/
---

# UI-BUYER-001：实现 Buyer Overview

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Buyer**  
**功能依赖：UI-003 + Buyer Balance / Availability contracts**

> 产品合同：[/burncloud-ui/buyer/overview/](/burncloud-ui/buyer/overview/)

### TL;DR

Buyer 首页只回答“今天花了多少、还有多少余额、API 是否稳定、今天用了多少 Token”。不让 Buyer 理解 GPU、Supplier、Provider 或内部 Route。

### 背景与动机（Why）

current Overview 已经能读取真实 usage/billing/logs/channels/tokens/system metrics，但它是混合 operator/setup dashboard。Buyer Overview 必须重新组合成消费与服务结果视角，而不是把当前首页改个标题。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Today Spend / Balance | 不显示 GPU/IDC/Supplier |
| API Availability / Tokens Today | 不显示 Provider/Route config |
| Models in Use / Recent Activity | 不在前端推导账本 |
| Partial Failure truth | 不自动 Top Up |

### 审批者关注点（Reviewer Focus）
1. 四个指标是否都是 Buyer 自己的数据？
2. Unknown 是否不会显示成 `$0`？
3. low balance 是否只有一个清晰、真实的 Top Up 入口？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立 Buyer-only Overview composition，首屏优先 `today_spend / balance / api_availability / tokens_today`。

### 2. Evidence

- STATIC CONFIRMED — `critical_pages/dashboard.rs::Overview` 已读取 user-scoped usage/billing 等真实数据。
- STATIC CONFIRMED — `/api/billing/summary` 由 server `claims.sub` scope。
- STATIC CONFIRMED — user account 存在 balance fields。
- UNKNOWN — Buyer-safe current balance read contract 是否满足页面需求。
- UNKNOWN — authoritative Buyer-facing API availability contract。

### 3. Entry / Starting Point

`critical_pages/dashboard.rs::Overview`、`backend::billing_summary`、`backend::user_usage`、UI-003 Buyer workspace。

### 4. Reuse Targets / Do Not Recreate

Reuse：existing billing/usage resources、overview state patterns、auth context。  
Do Not Recreate：client ledger、Provider-derived availability、mock dashboard。

### 5. Scope

Allowed：Buyer Overview composition、read-only Buyer APIs、navigation。  
Avoid：payment backend、billing semantics、Router/Provider changes、Supplier/Admin metrics。

### 6. Behavior Contract

**Inputs**：authenticated Buyer + scoped usage/billing/balance/availability。  
**Outputs**：四核心指标、models/activity、low-balance action state。  
**Ownership**：domain services own facts；page composes。  
**Side Effects**：read-only/navigation；Top Up 只能显式用户发起。

### 7. Failure / Forbidden Fallbacks

Loading 不先显示 0；source failure 只将受影响 metric 显示 Unavailable；missing backend contract 阻塞而不是读 raw Provider/GPU table。

### 8. Impact / Invariants

Read-only Buyer data。Tenant scope 必须 server-side。Buyer mental model = product consumption/service result。

### 9. Dependencies

UI-003；Buyer-safe balance；Buyer-facing availability；实现前 re-audit current source。

### 10. Stop Conditions

STOP IF metric 必须由 Provider/GPU/client formula 推导，tenant isolation 不能 server-side 验证，或缺失事实只能靠 mock 填充。

---

## 第三层：验收层（Definition of Done）

- [ ] Today Spend / Balance / API Availability / Tokens Today 均有 authoritative source。
- [ ] Buyer tenant isolation 验证。
- [ ] GPU/Supplier/IDC/Runtime/Provider config 不出现在首屏。
- [ ] Loading/Empty/Partial Failure/Error/Recovered truthful。
- [ ] low-balance CTA 不伪装 payment success。
- [ ] existing Billing/Usage semantics 回归通过。
- [ ] branch + PR。
