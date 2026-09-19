---
title: "UI-BUYER-007：实现 Buyer Logs"
slug: /burncloud-ui/implementation-plan/ui-buyer-007/
---

# UI-BUYER-007：实现 Buyer Logs

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
**功能依赖：UI-003、UI-007、UI-008 + tenant-safe Request Log projection**

> 产品合同：[/burncloud-ui/buyer/logs/](/burncloud-ui/buyer/logs/)  
> Canonical production route：`/console/buyer/logs`

### TL;DR
Buyer Logs 只能展示 Buyer 自己的请求可观测信息。current `/console/api/logs` 是管理日志能力，不能“取全量后前端过滤”；legacy `/logs` 也不得自动变成本页。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| own request ID/model/status | 不读全量 Admin logs |
| tokens/duration/cost/trace | 不显示 prompt/secret by default |
| filters/detail | 不前端 tenant filter 当安全边界 |
| localized status explanation | 不翻译 request/model/error IDs |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/buyer/logs` tenant-safe request observability page。

### 2. Evidence
- STATIC CONFIRMED — current `/console/api/logs` 属于 management/admin observability path。
- STATIC CONFIRMED — normal user 不应获得全量管理日志。
- UNKNOWN — dedicated tenant-safe Buyer log projection contract。

### 3. Entry / Starting Point
observability patterns、future Buyer log API、UI-003/007/008。Legacy `/logs` policy 由 UI-008/UI-005 控制。

### 4. Reuse Targets / Do Not Recreate
Reuse：request IDs、usage/cost/trace facts、filters/detail patterns、shared status/i18n。  
Do Not Recreate：client tenant filtering security、raw admin log proxy、prompt/credential viewer。

### 5. Scope
Allowed：Buyer-owned request list/filter/detail。  
Avoid：Admin logs、security event console、prompt content disclosure。

### 6. Behavior Contract
**Inputs**：Buyer identity + server-scoped request logs + locale。  
**Outputs**：own request observability and trace detail。  
**Ownership**：Observability service owns tenant projection。  
**Side Effects**：read-only。

### 7. Failure / Forbidden Fallbacks
No tenant-safe projection → BLOCKED。禁止 fetch all then filter、legacy `/logs` dynamic role mapping、URL 获权、翻译 IDs/error codes。

### 8. Impact / Invariants
Sensitive observability；server-side tenant scope mandatory；route `/console/buyer/logs`。

### 9. Dependencies
UI-003、007、008 + tenant-safe log projection。

### 10. Stop Conditions
STOP IF implementation needs Admin `/console/api/logs` full data、prompt/secret exposure、或 client filter 才能隔离 tenant。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Buyer logs server-side tenant scoped。
- [ ] legacy `/logs` 不自动映射本页。
- [ ] no prompt/secret exposure by default。
- [ ] request/model/error IDs 保持机器值；解释文案 localized。
- [ ] unauthorized cross-tenant tests pass。
- [ ] branch + PR。
