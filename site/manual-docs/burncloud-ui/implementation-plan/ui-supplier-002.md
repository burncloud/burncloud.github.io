---
title: "UI-SUPPLIER-002：实现 Supplier Resources"
slug: /burncloud-ui/implementation-plan/ui-supplier-002/
---

# UI-SUPPLIER-002：实现 Supplier Resources

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003、UI-007、UI-008 + Supplier Node Inventory / ResourceSnapshot / Graceful Offline contract**

> 产品合同：[/burncloud-ui/supplier/resources/](/burncloud-ui/supplier/resources/)  
> Canonical production route：`/console/supplier/resources`

### TL;DR
Resources 让 Supplier 看自己的 Node/GPU/VRAM/temperature/utilization/health，并允许在后端支持时请求 Graceful Offline；它不提供模型、端口、进程、Traffic 控制。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| own nodes/GPU/VRAM/health | 不选 model |
| telemetry/resource snapshot | 不设 gpu_layers/port/PID |
| graceful offline request | 不 kill runtime |
| diagnostics/explanation | 不修改 Router |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/supplier/resources` 的 Supplier-owned resource inventory 和安全 lifecycle request surface。

### 2. Evidence
- STATIC CONFIRMED — Target Resources 是 Supplier 资源页，不是 Admin capacity scheduler。
- UNKNOWN — current-main Supplier registry/Node ownership/HardwareProfile/ResourceSnapshot contracts。
- UNKNOWN — Graceful Offline lifecycle API/policy。

### 3. Entry / Starting Point
Node hardware/resource services once accepted、UI-003/007/008、shared status/table patterns。

### 4. Reuse Targets / Do Not Recreate
Reuse：canonical Node identity、HardwareProfile、ResourceSnapshot、health lifecycle。  
Do Not Recreate：frontend hardware discovery、process manager、scheduler、Supplier route engine。

### 5. Scope
Allowed：own resource list/detail、telemetry、graceful offline/resume only if authoritative。  
Avoid：model selection、runtime command、Traffic control、Admin fleet planning。

### 6. Behavior Contract
**Inputs**：Supplier identity + owned Node/resource telemetry + locale + explicit graceful lifecycle request。  
**Outputs**：resource state + verified lifecycle result。  
**Ownership**：Node/Supplier services own resources/actions。  
**Side Effects**：only approved graceful lifecycle request。

### 7. Failure / Forbidden Fallbacks
Offline request submitted != Offline；必须等待 authoritative result。禁止 direct process kill、frontend ownership inference、URL 获权。

### 8. Impact / Invariants
Operational but bounded；Supplier may request graceful lifecycle, not runtime/process control。Route `/console/supplier/resources`。

### 9. Dependencies
UI-003、007、008 + Supplier Node Inventory/ResourceSnapshot/Graceful Offline contract。

### 10. Stop Conditions
STOP IF ownership 需 client 推断、action 必须直接 kill process、或 Supplier 被授予 model/runtime/traffic authority。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] only Supplier-owned resources visible。
- [ ] hardware/telemetry authoritative。
- [ ] graceful offline result verified，不 optimistic。
- [ ] no model/runtime/traffic controls。
- [ ] units/status localized appropriately；Node/GPU model IDs 保持稳定。
- [ ] branch + PR。
