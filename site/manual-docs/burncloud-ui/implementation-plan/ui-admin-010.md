---
title: "UI-ADMIN-010：实现 Admin Customers"
slug: /burncloud-ui/implementation-plan/ui-admin-010/
---

# UI-ADMIN-010：实现 Admin Customers

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003、UI-007、UI-008 + Customer Risk / Activity / Human Gate contracts**

> 产品合同：[/burncloud-ui/admin/customers/](/burncloud-ui/admin/customers/)  
> Canonical production route：`/console/admin/customers`

### TL;DR
Customers 复用现有真实 UserService/account/balance/admin funding 能力，并补充 authoritative usage/spend/risk/limits/activity。高风险账户动作必须授权/审计；不显示 API secret 或 prompt content。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| account/balance/status | 不显示 bearer secret |
| usage/spend/activity | 不显示 prompt content |
| risk/limits if authoritative | 不 client risk score |
| audited create/fund/limit/freeze | 不 optimistic financial mutation |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/admin/customers` 的 authoritative customer account operations page。

### 2. Evidence
- STATIC CONFIRMED — current Customers 使用真实 UserService、wallet balances、Create Customer / admin funding。
- STATIC CONFIRMED — normal user cannot use admin funding endpoints。
- UNKNOWN — customer Risk/Limit policy、unified activity projection、complete Human Gate semantics。

### 3. Entry / Starting Point
`critical_pages/customers_portable.rs`、UserService、Billing/Usage services、Admin Operations、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：UserService/customer records/balances/auth、approved risk/activity services。  
Do Not Recreate：second customer DB、client risk score、secret/prompt viewer。

### 5. Scope
Allowed：evolve current Customers page, authoritative drilldowns/actions。  
Avoid：Risk engine、billing ledger redesign、secret data display。

### 6. Behavior Contract
**Inputs**：Admin identity + customer/account/balance/usage/risk/activity + explicit action + locale。  
**Outputs**：customer list/detail/action result。  
**Ownership**：User/Billing/Usage/Risk services own facts/actions。  
**Side Effects**：approved account/financial/limit actions only。

### 7. Failure / Forbidden Fallbacks
Mutation failure not applied；unknown risk stays Unknown；activity failure preserves core account facts。禁止 client risk、secrets/prompts、optimistic balance。

### 8. Impact / Invariants
Admin customer/financial operations；route `/console/admin/customers`；high-risk audit mandatory。

### 9. Dependencies
UI-003、007、008 + Risk/Limit/activity/Human Gate contracts。

### 10. Stop Conditions
STOP IF risk client-computed、action unaudited、secret/prompt required、or identity reconstructed from logs。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致；legacy `/customers`/`/users` migrate here safely。
- [ ] UserService remains identity source。
- [ ] balances/usage/spend/risk/activity authoritative。
- [ ] high-risk actions authorized/audited。
- [ ] no secrets/prompts。
- [ ] money/date/status localized via UI-007；IDs stable。
- [ ] branch + PR。
