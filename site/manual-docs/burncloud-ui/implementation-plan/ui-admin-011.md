---
title: "UI-ADMIN-011：实现 Admin Settings"
slug: /burncloud-ui/implementation-plan/ui-admin-011/
---

# UI-ADMIN-011：实现 Admin Settings

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003、UI-ADMIN-006 + Platform/Domain Settings Ownership**

> 产品合同：[/burncloud-ui/admin/settings/](/burncloud-ui/admin/settings/)

### TL;DR

Admin Settings 只管理真正的平台/domain 设置；不是“所有数据库字段/环境变量”的垃圾桶。当前 production Settings 已经谨慎地只暴露 server 真正支持的 Environment/Runtime/Cache maintenance，这个原则要保留并扩展到 approved domain settings。

### 背景与动机（Why）

Settings 最容易成为架构泄漏点。若页面没有明确 backend owner，就会把 frontend default、raw env、DB field 变成“配置真相”。高风险 financial/security/Autopilot settings 还必须进入 Human Gate。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| real platform/domain settings | 不 raw DB/env editor |
| Backend Owner / Policy Summary | 不 generic settings blob |
| safe maintenance | 不复制 Models/Capacity/Billing responsibilities |
| high-risk Gate/Audit/Verify | 不 dangerous unaudited switches |

### 审批者关注点（Reviewer Focus）
1. every editable field 是否有 backend owner？
2. high-risk change 是否有 impact/rollback/gate/audit/verify？
3. current truthful cache/environment behavior 是否保留？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

演进 current Settings 为 backend-owned platform/domain settings surface，不让 UI 成为 configuration source of truth。

### 2. Evidence

- STATIC CONFIRMED — current `functional_pages/settings.rs` 只展示 connected environment、runtime health、cache stats/clear 等 server-supported facts/actions。
- STATIC CONFIRMED — current page 明确声明没有 general settings CRUD API，因此不伪造 Appearance/Gateway Defaults/Notifications。
- STATIC CONFIRMED — cache clear 已有 explicit confirmation。
- TARGET CONFIRMED — high-risk financial/security/Autopilot changes 需要 Gate/Audit/Verify。
- UNKNOWN — approved platform/domain settings ownership map、domain settings APIs、complete high-risk policy semantics。

### 3. Entry / Starting Point

`functional_pages/settings.rs::Settings`、system metrics/cache APIs、future domain setting services、UI-ADMIN-006 Operations。

### 4. Reuse Targets / Do Not Recreate

Reuse：current environment/maintenance facts、form/confirmation patterns、approved domain services。  
Do Not Recreate：generic JSON config store、raw env/db editor、duplicate policy engine、UI-owned defaults as persisted truth。

### 5. Scope

Allowed：evolve Settings、authoritative domain settings、maintenance、gated dangerous settings。  
Avoid：general settings backend architecture、financial/security policy design、raw infra config console。

### 6. Behavior Contract

**Inputs**：Admin + authoritative setting values + explicit edit/action + risk policy。  
**Outputs**：confirmed value + applied/not-applied/audited result。  
**Ownership**：each backend domain owns setting；Operations/Policy owns high-risk gate；UI presents。  
**Side Effects**：approved settings/maintenance only。

### 7. Failure / Forbidden Fallbacks

Missing owner => no editable control；save failure stays not applied；Unknown config 不用 frontend default 覆盖；dangerous action cannot bypass Gate。禁止 raw DB/env mutation。

### 8. Impact / Invariants

Persistence through authoritative settings services；UI not source of truth；high-risk Human by Exception；current cache/environment truthfulness preserved。

### 9. Dependencies

UI-003 + approved settings ownership map + domain settings APIs + UI-ADMIN-006 high-risk gate semantics。

### 10. Stop Conditions

STOP IF setting 无 backend owner、implementation requires raw DB/env mutation、dangerous change bypasses audit/gate、或 UI constant 要被持久化为 policy truth。

---

## 第三层：验收层（Definition of Done）

- [ ] every editable setting has authoritative owner。
- [ ] current values real backend-derived。
- [ ] save failure not optimistic success。
- [ ] dangerous financial/security/Autopilot change gated/audited/verified。
- [ ] no raw DB/env config dump/editor。
- [ ] current supported maintenance behavior remains valid。
- [ ] branch + PR。
