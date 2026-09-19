---
title: "UI-SUPPLIER-003：实现 Supplier Deployments"
slug: /burncloud-ui/implementation-plan/ui-supplier-003/
---

# UI-SUPPLIER-003：实现 Supplier Deployments

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
**类别：Supplier**  
**功能依赖：UI-003、UI-007、UI-008 + Managed Deployment / Node Runtime State contract**

> 产品合同：[/burncloud-ui/supplier/deployments/](/burncloud-ui/supplier/deployments/)  
> Canonical production route：`/console/supplier/deployments`

### TL;DR
Deployments 是只读的自动部署结果页。Supplier 可以看 BurnCloud 在自己的资源上运行了什么、状态和效率如何，但不能 Deploy、Start、Stop、Choose Model、Change Traffic。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| managed deployments | 不 Deploy/Undeploy |
| model/runtime state | 不 Start/Stop |
| resource/throughput/efficiency | 不选 model/tier |
| failure/recovered explanation | 不改 traffic/routing |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
在 `/console/supplier/deployments` 提供 Supplier-owned managed deployment observability。

### 2. Evidence
- STATIC CONFIRMED — Target 明确 Deployments read-only；Autopilot/Node owns deployment decisions。
- UNKNOWN — authoritative managed deployment projection linking Supplier Node ↔ Model ↔ Runtime state。

### 3. Entry / Starting Point
Node Runtime/Deployment state、UI-004 canonical Node UX、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：Node/Autopilot deployment state、readiness/health、resource metrics。  
Do Not Recreate：frontend deployment scheduler、runtime manager、manual routing controls。

### 5. Scope
Allowed：read-only list/detail/status/throughput/resource allocation。  
Avoid：deployment mutation、runtime command、model selection、Traffic control。

### 6. Behavior Contract
**Inputs**：Supplier identity + owned managed deployment states + locale。  
**Outputs**：read-only deployment view with canonical status/explanation。  
**Ownership**：Node/Autopilot owns lifecycle；UI presents。  
**Side Effects**：none。

### 7. Failure / Forbidden Fallbacks
Unknown deployment state 不映射 Running；Process exists != READY。禁止 action buttons 直接操作 runtime/process。

### 8. Impact / Invariants
Read-only；route `/console/supplier/deployments`；UI-004 status semantics；Supplier no deployment authority。

### 9. Dependencies
UI-003、007、008、UI-004 + managed deployment projection。

### 10. Stop Conditions
STOP IF page needs direct runtime command、client deployment state machine、or supplier can select model/traffic。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Supplier sees only own deployment projection。
- [ ] Deployments read-only。
- [ ] Node statuses use UI-004；copy uses UI-007。
- [ ] Process Spawned 不显示成 READY。
- [ ] no Deploy/Start/Stop/Choose Model/Traffic actions。
- [ ] branch + PR。
