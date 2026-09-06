---
title: "UI-ADMIN-009：实现 Admin Suppliers"
slug: /burncloud-ui/implementation-plan/ui-admin-009/
---

# UI-ADMIN-009：实现 Admin Suppliers

<!-- UI-ARCHITECTURE-DEPENDENCY: REQUIRED -->
> **Mandatory Architecture Dependency（强制）**
>
> 本实施单元必须遵守 [BurnCloud UI Architecture Contract](/burncloud-ui/architecture/)。Architecture Contract 是本页、READY Engineering Issue、Task Contract 与 Production Dioxus 实现的上位约束。
>
> - 实施前必须读取 [Directory Contract](/burncloud-ui/architecture/directory-contract/)、[Authorization Contract](/burncloud-ui/architecture/authorization-contract/)、[API Boundary](/burncloud-ui/architecture/api-boundary/) 与 [Code Ownership](/burncloud-ui/architecture/code-ownership/) 中适用规则；
> - Task Contract 必须明确 `Allowed Paths / Conditional Paths / Forbidden Paths`；
> - 本页只能增加更严格的限制，**不能放宽 Architecture Contract**；
> - 若页面需求与 Architecture Contract 冲突，必须 `STOP → Architecture Dependency / Foundation Issue`，不得由 AI/Codex 自行扩大 scope 或修改 Protected Architecture Zone。
>
> `Implementation convenience != architecture authority`；`CI green != permission to violate the Architecture Contract`。
<!-- UI-ARCHITECTURE-DEPENDENCY: END -->

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003、UI-007、UI-008 + Supplier Registry / Verification / Reliability / Commercial contracts**

> 产品合同：[/burncloud-ui/admin/suppliers/](/burncloud-ui/admin/suppliers/)  
> Canonical production route：`/console/admin/suppliers`

### TL;DR
Suppliers 管理真实 Supplier business identity、verification、level、reliability、resources、contribution 和 commercial status。Provider Channel 不是 Supplier identity。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| supplier profile/verification | 不 Channel→Supplier inference |
| reliability/resources/contribution | 不合成 opaque trust score |
| authorized commercial config | 不泄露 credentials/secrets |
| evidence-backed status | 不直接 route/runtime control |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/admin/suppliers` 的 authoritative Supplier registry/business/trust surface。

### 2. Evidence
- STATIC CONFIRMED — current Providers/Channels 是 upstream routing entities，不等于 Supplier business identity。
- UNKNOWN — Supplier registry/verification/level/reliability/contribution/commercial services。

### 3. Entry / Starting Point
future Supplier services、Admin Supply、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：canonical Supplier identity、Node/resources、Reliability、Contribution、approved commercial settings。  
Do Not Recreate：Channel-derived Supplier registry、client trust score。

### 5. Scope
Allowed：Supplier list/detail/evidence and approved gated changes。  
Avoid：routing/provider management、secret display、trust engine design。

### 6. Behavior Contract
**Inputs**：Admin identity + supplier/trust/resource/commercial facts + authorized edit + locale。  
**Outputs**：supplier view/management result。  
**Ownership**：respective backend domains own facts/actions。  
**Side Effects**：only authorized/audited profile/commercial changes。

### 7. Failure / Forbidden Fallbacks
Unknown verification != Verified；no Channel inference；save failure not applied。禁止 secrets/client trust score。

### 8. Impact / Invariants
Admin trust/business management；route `/console/admin/suppliers`；Level/Reliability/Contribution/Revenue Share remain distinct。

### 9. Dependencies
UI-003、007、008 + Supplier registry/trust/reliability/contribution/commercial contracts。

### 10. Stop Conditions
STOP IF Supplier inferred from Channel、trust computed client-side、commercial changes unaudited、or secrets required。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Supplier identity authoritative and separate from Provider Channel。
- [ ] verification evidence-backed。
- [ ] concept separation preserved。
- [ ] gated changes authorized/audited。
- [ ] i18n labels/statuses localized; stable IDs unchanged。
- [ ] branch + PR。
