---
title: "UI-ADMIN-010：实现 Admin Customers"
slug: /burncloud-ui/implementation-plan/ui-admin-010/
---

# UI-ADMIN-010：实现 Admin Customers

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003 + Customer Risk/Limit / Activity / High-risk Audit**

> 产品合同：[/burncloud-ui/admin/customers/](/burncloud-ui/admin/customers/)

### TL;DR

Customers 让 Admin 看 Buyer Account、Usage、Balance、Risk、Limits、Recent Activity 并处理明确账户问题。现有页面已经有真实 UserService、余额和 Admin funding，可复用；目标新增 Risk/Activity/Human Gate 时不能靠前端启发式补齐。

### 背景与动机（Why）

这是少数已有较强 current production 能力的目标页。正确方向是演进现有 Customers，而不是重写数据库/账号体系；同时要把高风险 Freeze/Limit/Funding 与 secret/prompt privacy 约束补完整。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Customer Account / Balance | 不显示 API bearer secret |
| Usage / Spend / Recent Activity | 不默认显示 Prompt |
| Risk / Limits（backend-owned） | 不 client-compute risk |
| explicit audited actions | 不 optimistic balance/status |

### 审批者关注点（Reviewer Focus）
1. 是否复用 current UserService 而不是建第二 customer DB？
2. Risk/Limit 是否有 authoritative owner？
3. funding/freeze/limit 等高风险动作是否有明确影响和 audit？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

演进 current Customers page 成为 authoritative Admin customer operations surface。

### 2. Evidence

- STATIC CONFIRMED — `critical_pages/customers_portable.rs` 使用真实 `UserService`、过滤 staff、显示 wallet balances、支持 Create Customer/Admin funding。
- STATIC CONFIRMED — current security invariant 禁止 normal user 调 Admin topup。
- TARGET CONFIRMED — 目标还需要 Usage/Spend/Risk/Limits/Recent Activity，并保护 secrets/prompts。
- UNKNOWN — authoritative Risk/Limit service、unified customer activity projection、完整 high-risk action audit semantics。

### 3. Entry / Starting Point

`critical_pages/customers_portable.rs::Customers`、`backend::UserService`、Billing/Usage、future Risk/Activity、Operations gate。

### 4. Reuse Targets / Do Not Recreate

Reuse：UserService/customer records/balances/current authorization/billing/usage。  
Do Not Recreate：second customer DB、API secret display、prompt dump、frontend risk heuristic。

### 5. Scope

Allowed：evolve existing page、read drilldowns、approved customer operations。  
Avoid：Risk engine、Billing ledger redesign、arbitrary raw user table、secret/prompt exposure。

### 6. Behavior Contract

**Inputs**：Admin + account/balance/usage/risk/activity facts + explicit action。  
**Outputs**：customer list/detail + confirmed operation result。  
**Ownership**：User/Billing/Usage/Risk domains own facts/actions；UI composes/asks human intent。  
**Side Effects**：approved account/funding/limit/status operations only。

### 7. Failure / Forbidden Fallbacks

Mutation failure = not applied；Unknown risk remains Unknown；activity failure 保留 account/balance。禁止 client risk score、secret/prompt display、optimistic balance/status。

### 8. Impact / Invariants

Customer/account persistence via existing services；financial/admin operations require server auth/audit；sensitive credentials/content not default management data。

### 9. Dependencies

UI-003 + Risk/Limit contract + Recent Activity projection + high-risk action audit/Human Gate。Existing UserService/balance/funding 可优先复用。

### 10. Stop Conditions

STOP IF risk 需 frontend-compute、high-risk mutation 无 audit、secret/prompt 是必要输入、或 customer identity 必须从 logs 重建而非 UserService。

---

## 第三层：验收层（Definition of Done）

- [ ] customer identity/account state trace UserService。
- [ ] balance/usage/spend authoritative。
- [ ] Risk/Limit backend-owned。
- [ ] high-risk actions authorized/audited。
- [ ] no API secret/prompt exposure。
- [ ] failures not optimistic success。
- [ ] normal-user Admin action denial regression preserved。
- [ ] branch + PR。
