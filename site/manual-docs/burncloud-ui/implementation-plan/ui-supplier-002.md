---
title: "UI-SUPPLIER-002：实现 Supplier Resources"
slug: /burncloud-ui/implementation-plan/ui-supplier-002/
---

# UI-SUPPLIER-002：实现 Supplier Resources

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003 + Supplier Node Inventory / HardwareProfile / Resource Lifecycle**

> 产品合同：[/burncloud-ui/supplier/resources/](/burncloud-ui/supplier/resources/)

### TL;DR

Resources 展示 Supplier 自己的 Node/GPU/VRAM/Temperature/Utilization/Uptime/Assigned Model，并允许请求 Graceful Offline。Assigned Model 是只读 Autopilot 结果，不是 Supplier 的模型选择器。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Node/GPU/VRAM/Health | 不 Choose Model |
| Current Model read-only | 不改 Runtime args |
| Graceful Offline | 不改 Traffic Weight |
| Draining lifecycle | 不 Force Route |

### 审批者关注点（Reviewer Focus）
1. Graceful Offline 是否真实经历 Drain→Finish→Release→Offline？
2. Current Model 是否清楚标记 Autopilot assigned/read-only？
3. Force/Unexpected Offline 是否与正常下线分开？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 Supplier-scoped resource inventory/health 与一个受控 Graceful Offline intent。

### 2. Evidence

- TARGET CONFIRMED — page requires Node/GPU/VRAM/temp/utilization/current model/uptime。
- TARGET CONFIRMED — Graceful Offline state chain 明确。
- UNKNOWN — canonical Supplier-scoped HardwareProfile/ResourceSnapshot/managed assignment/resource lifecycle API。

### 3. Entry / Starting Point

UI-003；canonical Node inventory/HardwareProfile/ResourceSnapshot；resource lifecycle service。

### 4. Reuse Targets / Do Not Recreate

Reuse：Node hardware/resource/runtime state + shared tables/statuses。  
Do Not Recreate：`MOCK_SUPPLIER_NODES`、second telemetry store、model selector、Runtime CLI editor、traffic controller。

### 5. Scope

Allowed：resource list/detail、approved Graceful Offline action。  
Avoid：Node backend、deployment selection、process control、routing changes。

### 6. Behavior Contract

**Inputs**：Supplier scope + inventory/telemetry/deployment state + explicit offline request。  
**Outputs**：resource health/detail + lifecycle state。  
**Ownership**：Node/resource services own state/lifecycle；UI requests intent。  
**Side Effects**：Graceful Offline request only。

### 7. Failure / Forbidden Fallbacks

Telemetry unknown remains Unknown；offline request failure 不乐观显示 Offline。禁止 force-stop、deploy-model、runtime params、traffic controls。

### 8. Impact / Invariants

Supplier 可声明资源 availability intent，但不拥有 model/runtime/traffic decisions。Process ownership stays Node Autopilot。

### 9. Dependencies

UI-003 + Supplier-scoped inventory + hardware/resource telemetry + managed assignment + graceful-offline lifecycle。

### 10. Stop Conditions

STOP IF UI 必须直接读 raw OS/process state、force stop、choose model/runtime 或自己实现 drain lifecycle。

---

## 第三层：验收层（Definition of Done）

- [ ] real Node/GPU data replaces mock。
- [ ] hardware/health/assigned model authoritative。
- [ ] Graceful Offline stages visible/verified。
- [ ] unexpected/forced offline distinct。
- [ ] no model/runtime/traffic controls。
- [ ] Supplier isolation verified。
- [ ] branch + PR。
