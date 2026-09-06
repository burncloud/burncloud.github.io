---
title: "UI-ADMIN-004：实现 Admin Demand"
slug: /burncloud-ui/implementation-plan/ui-admin-004/
---

# UI-ADMIN-004：实现 Admin Demand

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
**功能依赖：UI-003、UI-007、UI-008 + Demand / Attribution / Forecast contracts**

> 产品合同：[/burncloud-ui/admin/demand/](/burncloud-ui/admin/demand/)  
> Canonical production route：`/console/admin/demand`

### TL;DR
Demand 只回答“请求/token 需求在哪里增长、哪些 Model/Tier/tenant/region 贡献、未来可能怎样”。Forecast 必须和 Actual 分开。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| actual demand trends | 不用 Revenue 代替 demand |
| model/tier/tenant/region attribution | 不把 forecast 当 actual |
| forecast + confidence if authoritative | 不 client AI 猜趋势 |
| bursts/velocity | 不泄露 unauthorized tenant details |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/admin/demand` 的 platform demand analytics。

### 2. Evidence
- STATIC CONFIRMED — existing usage/logs contain demand evidence fragments。
- UNKNOWN — canonical demand aggregation/forecast service and confidence contract。

### 3. Entry / Starting Point
Usage/Logs evidence、future Demand service、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：metering/request facts、canonical Model/Tier identity、approved forecast。  
Do Not Recreate：client forecast engine、Revenue→Demand inference。

### 5. Scope
Allowed：actual demand/trends/attribution/forecast presentation。  
Avoid：capacity scheduler、pricing changes、client prediction engine。

### 6. Behavior Contract
**Inputs**：Admin identity + actual demand + optional forecast/confidence + locale。  
**Outputs**：demand trends/bursts/attribution/forecast。  
**Ownership**：Demand service owns facts/forecast。  
**Side Effects**：read-only。

### 7. Failure / Forbidden Fallbacks
No forecast → unavailable；Actual remains usable。禁止 client forecast、cross-tenant unauthorized detail。

### 8. Impact / Invariants
Read-only；route `/console/admin/demand`；Actual != Forecast。

### 9. Dependencies
UI-003、007、008 + Demand/Forecast contracts。

### 10. Stop Conditions
STOP IF demand must be inferred from revenue、forecast computed client-side、or tenant privacy cannot be preserved。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Actual demand authoritative。
- [ ] Forecast explicitly separated + confidence/finality where applicable。
- [ ] tenant/region drilldown authorization safe。
- [ ] locale-aware numbers/time; machine Model/Tier IDs stable。
- [ ] branch + PR。
