---
title: "UI-SUPPLIER-003：实现 Supplier Deployments"
slug: /burncloud-ui/implementation-plan/ui-supplier-003/
---

# UI-SUPPLIER-003：实现 Supplier Deployments

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003 + Managed Deployment / Process Readiness / Autopilot Reason**

> 产品合同：[/burncloud-ui/supplier/deployments/](/burncloud-ui/supplier/deployments/)

### TL;DR

Deployments 是透明页：告诉 Supplier BurnCloud 当前在其资源上跑什么、状态如何、为什么这么做。不是部署控制台。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Model/State/Resource summary | 不 Deploy Model |
| Preparing/Ready/Draining/Failed | 不 Start/Stop process |
| Autopilot reason/result | 不 Change Runtime |
| link to Resource/Reliability | 不 Traffic Control |

### 审批者关注点（Reviewer Focus）
1. 是否严格 read-only？
2. `Process Spawned != Model READY` 是否保留？
3. 异常是否引导看 Resource/Reliability，而不是“手工修部署”？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 Supplier-scoped managed deployment transparency，不授予 runtime/process authority。

### 2. Evidence

- TARGET CONFIRMED — Deployments = read-only transparency。
- TARGET CONFIRMED — forbidden actions: Deploy/Choose Model/Change Runtime/Traffic Control。
- NODE INVARIANT — Spawned != Ready。
- UNKNOWN — Supplier-scoped deployment state、Process Manager readiness/health、Scheduler/Demand explanation projection。

### 3. Entry / Starting Point

UI-003；managed Node deployment/runtime/process state；resource allocation；Autopilot reason/result。

### 4. Reuse Targets / Do Not Recreate

Reuse：canonical runtime/process lifecycle、readiness、resource state、shared status/timeline。  
Do Not Recreate：deployment controller、PID/port manager、Route control surface。

### 5. Scope

Allowed：read-only list/detail/reason/navigation。  
Avoid：process lifecycle implementation、scheduler/demand logic、routing mutations、secret diagnostics。

### 6. Behavior Contract

**Inputs**：Supplier scope + deployment/readiness/resource/reason facts。  
**Outputs**：read-only deployment transparency。  
**Ownership**：Node runtime/process/demand own lifecycle；UI observes。  
**Side Effects**：none。

### 7. Failure / Forbidden Fallbacks

Unknown lifecycle stays Unknown；missing reason 不猜。禁止 Deploy/Start/Stop/Choose Model/Traffic actions；PID/internal port/raw CLI 默认隐藏。

### 8. Impact / Invariants

Read-only；Supplier transparency ≠ authority；Spawned ≠ Ready；diagnostic visibility ≠ write permission。

### 9. Dependencies

UI-003 + Supplier-scoped managed deployment + readiness + reason/result contracts。

### 10. Stop Conditions

STOP IF normal UI 需要 raw PID/port/CLI、manual deployment controls，或 readiness 只能从 process existence 推导。

---

## 第三层：验收层（Definition of Done）

- [ ] deployment state authoritative/read-only。
- [ ] Preparing/Ready/Draining/Failed semantics real。
- [ ] automatic actions expose safe reason/result。
- [ ] no Deploy/Start/Choose/Route controls。
- [ ] no PID/internal port/raw CLI default exposure。
- [ ] Supplier isolation verified。
- [ ] branch + PR。
