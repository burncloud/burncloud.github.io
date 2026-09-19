---
title: "UI-ADMIN-011：实现 Admin Settings"
slug: /burncloud-ui/implementation-plan/ui-admin-011/
---

# UI-ADMIN-011：实现 Admin Settings

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
**功能依赖：UI-003、UI-007、UI-008 + domain Settings ownership + Human Gate contracts**

> 产品合同：[/burncloud-ui/admin/settings/](/burncloud-ui/admin/settings/)  
> Canonical production route：`/console/admin/settings`

### TL;DR
Admin Settings 只展示/修改有明确 backend owner 的平台设置。高风险 financial/security/Autopilot settings 必须 Human Gate；不建立 raw DB/env configuration console。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| backend-owned domain settings | 不 raw env/database editor |
| environment/runtime read-only facts | 不 UI-owned policy |
| safe maintenance actions | 不绕过 Human Gate |
| locale/user preference where appropriate | 不让 locale 改 auth |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/admin/settings` 的 backend-owned settings/maintenance surface。

### 2. Evidence
- STATIC CONFIRMED — current Settings 只展示服务器实际支持的 environment/runtime/cache facts，并有明确 cache clear confirmation。
- STATIC CONFIRMED — current page明确没有通用 settings CRUD API。
- UNKNOWN — approved domain settings ownership map/APIs + dangerous settings Human Gate。

### 3. Entry / Starting Point
current `functional_pages/settings.rs`、domain settings services、Admin Operations、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：environment/maintenance facts、existing confirmation patterns、approved domain services。  
Do Not Recreate：generic JSON settings blob、raw env/DB editor、client policy source。

### 5. Scope
Allowed：authoritative domain settings、read-only environment、approved maintenance/gated dangerous settings。  
Avoid：general settings architecture creation、raw infrastructure config console。

### 6. Behavior Contract
**Inputs**：Admin identity + authoritative settings + explicit edits/actions + locale。  
**Outputs**：confirmed values/result。  
**Ownership**：each backend domain owns its settings；Operations owns high-risk gate。  
**Side Effects**：approved settings/maintenance only。

### 7. Failure / Forbidden Fallbacks
No owner/API → no editable control；save failure not applied；dangerous operation cannot bypass gate。禁止 raw DB/env、client defaults promoted to server policy。

### 8. Impact / Invariants
Admin settings persistence；route `/console/admin/settings`；UI not source of configuration truth。

### 9. Dependencies
UI-003、007、008 + settings ownership/APIs + Admin Operations Human Gate。

### 10. Stop Conditions
STOP IF field lacks authoritative owner、requires raw DB/env mutation、dangerous settings bypass audit、or UI constants become server policy。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致；legacy `/settings` compatibility explicit。
- [ ] every editable setting has backend owner。
- [ ] dangerous changes gated/audited。
- [ ] no raw DB/env editor。
- [ ] current supported maintenance behavior preserved。
- [ ] locale preference uses UI-007 but cannot affect authorization。
- [ ] branch + PR。
