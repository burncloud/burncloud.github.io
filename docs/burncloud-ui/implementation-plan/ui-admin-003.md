---
title: "UI-ADMIN-003：实现 Admin Capacity"
slug: /burncloud-ui/implementation-plan/ui-admin-003/
---

# UI-ADMIN-003：实现 Admin Capacity

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
**功能依赖：UI-003、UI-007、UI-008 + Capacity / Demand / Headroom / Queue contracts**

> 产品合同：[/burncloud-ui/admin/capacity/](/burncloud-ui/admin/capacity/)  
> Canonical production route：`/console/admin/capacity`

### TL;DR
Capacity 回答“哪些 Model/Tier 还剩多少安全余量、哪些快不够、为什么”。它不只是 GPU 总数，也不是 Supply 页换皮。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| headroom by Model/Tier | 不用 GPU count 代替 capacity |
| queue/throttle/latency | 不前端算 scheduler truth |
| risk/forecast evidence | 不直接操作 runtime |
| drilldown | 不隐藏 unknown assumptions |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/admin/capacity` 的 Model/Tier capacity headroom view。

### 2. Evidence
- STATIC CONFIRMED — Target Capacity 依赖 demand/supply/runtime serving facts。
- UNKNOWN — current-main canonical capacity/headroom service。

### 3. Entry / Starting Point
future Capacity service、Node/resource metrics、Demand service、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：serving/resource/demand/queue evidence。  
Do Not Recreate：client capacity scheduler/headroom formula as authoritative truth。

### 5. Scope
Allowed：read-only capacity/headroom/risk/drilldown。  
Avoid：scheduler design、runtime mutation、routing policy。

### 6. Behavior Contract
**Inputs**：Admin identity + capacity/demand/queue/latency facts + locale。  
**Outputs**：headroom/risk/trend/explanations。  
**Ownership**：Capacity service owns calculation。  
**Side Effects**：read-only/navigation。

### 7. Failure / Forbidden Fallbacks
Unknown demand/capacity → Unknown；no fake percentage。禁止 client scheduler and direct Runtime actions。

### 8. Impact / Invariants
Admin read-only；route `/console/admin/capacity`；Capacity != Supply。

### 9. Dependencies
UI-003、007、008 + authoritative capacity/headroom contracts。

### 10. Stop Conditions
STOP IF capacity must be inferred only from GPU count、client formula becomes source of truth、or page requires runtime control。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Model/Tier headroom authoritative。
- [ ] queue/throttle/latency evidence traceable。
- [ ] unknown inputs do not produce fake capacity。
- [ ] i18n/number/percentage formatting UI-007 compliant。
- [ ] branch + PR。
