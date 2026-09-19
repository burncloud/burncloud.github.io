---
title: "UI-BUYER-004：实现 Buyer API Keys"
slug: /burncloud-ui/implementation-plan/ui-buyer-004/
---

# UI-BUYER-004：实现 Buyer API Keys

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
**类别：Buyer**  
**功能依赖：UI-003、UI-007、UI-008 + owner-scoped Token contract**

> 产品合同：[/burncloud-ui/buyer/api-keys/](/burncloud-ui/buyer/api-keys/)  
> Canonical production route：`/console/buyer/api-keys`

### TL;DR
Buyer 管理自己的 API credentials；Secret 只在创建/旋转合同允许的瞬间显示，列表不重新返回 bearer secret。URL 或 WorkspaceGate 不能替代服务端 owner scope。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| list/create/revoke own keys | 不查看别人 key |
| one-time secret reveal | 不在列表回显 secret |
| spend/rate metadata if authoritative | 不前端伪造 quota |
| localized confirmations | 不翻译 token IDs |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
在 `/console/buyer/api-keys` 提供 owner-scoped credential lifecycle UI。

### 2. Evidence
- STATIC CONFIRMED — current `/console/api/tokens` 已有 token CRUD capability。
- STATIC CONFIRMED — management list/read path不应返回 bearer secret，owner scope 需服务端验证。
- UNKNOWN — spend cap/rate-limit metadata 的最终 authoritative contract。

### 3. Entry / Starting Point
current APIKeys page、TokenService/backend endpoints、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：token service、auth token handling、secure one-time secret pattern、shared dialogs/i18n。  
Do Not Recreate：client credential DB、secret cache、frontend owner filter as security boundary。

### 5. Scope
Allowed：own key list/create/revoke/rename/metadata where supported。  
Avoid：Admin key management、auth backend redesign、secret persistence。

### 6. Behavior Contract
**Inputs**：Buyer identity + authorized token actions + locale。  
**Outputs**：owner-scoped key metadata and one-time secret when backend explicitly returns it。  
**Ownership**：Token service owns credentials/authorization。  
**Side Effects**：credential mutations。

### 7. Failure / Forbidden Fallbacks
Create/revoke failure 不 optimistic success；secret reveal不能从历史数据恢复。禁止显示全量 tokens 再前端过滤、URL 获权、翻译 raw token reference。

### 8. Impact / Invariants
Security-sensitive；backend owner scope final；canonical route `/console/buyer/api-keys`。

### 9. Dependencies
UI-003、007、008 + owner-scoped Token contract。

### 10. Stop Conditions
STOP IF service returns cross-tenant list、UI must retain bearer secret、或 route/auth 需要绕过 UI-008/Backend Authorization。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Buyer only sees own key metadata。
- [ ] secret only appears under approved one-time contract。
- [ ] revoke/create failure truthful。
- [ ] unauthorized direct URL/API access denied。
- [ ] dialogs/messages localized；IDs/secrets不翻译。
- [ ] branch + PR + security regression tests。
