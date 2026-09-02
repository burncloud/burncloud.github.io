---
title: "UI-SUPPLIER-007：实现 Supplier Settings"
slug: /burncloud-ui/implementation-plan/ui-supplier-007/
---

# UI-SUPPLIER-007：实现 Supplier Settings

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003 + Supplier Settings / Payout Profile / Maintenance / Notifications**

> 产品合同：[/burncloud-ui/supplier/settings/](/burncloud-ui/supplier/settings/)

### TL;DR

Settings 只放 Supplier 真正拥有的设置：Notifications、Payout Profile、Maintenance Window 和批准的 resource preferences。这里不是 Runtime/Scheduler/Route 配置中心。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Notifications | 不 Manual Model Deployment |
| Payout Profile | 不 Runtime CLI/GPU Layers |
| Maintenance Window | 不 Route Weights |
| Supplier Preferences | 不 Scheduler internals |

### 审批者关注点（Reviewer Focus）
1. 每个 setting 是否有 backend owner？
2. Payout/identity 是否有额外验证？
3. Maintenance Window 是否只是约束声明？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 Supplier-owned settings surface，不把 frontend 变成 generic configuration source。

### 2. Evidence

- TARGET CONFIRMED — Supplier settings 仅 Notifications/Payout/Maintenance/Preferences。
- TARGET CONFIRMED — 明确排除 Deployment/Runtime/Route/Scheduler controls。
- UNKNOWN — authoritative Supplier settings backend、payout profile、maintenance policy、notification preference contracts。

### 3. Entry / Starting Point

UI-003；existing settings form patterns（reuse only after ownership audit）；future Supplier setting domains。

### 4. Reuse Targets / Do Not Recreate

Reuse：existing form/error patterns + authoritative domain services。  
Do Not Recreate：generic settings blob、client config DB、raw env editor、runtime/scheduler controls。

### 5. Scope

Allowed：Supplier-owned settings + approved validation。  
Avoid：platform settings、backend settings architecture、model/runtime/traffic controls。

### 6. Behavior Contract

**Inputs**：Supplier scope + authoritative values + explicit edits。  
**Outputs**：confirmed saved/not-applied values。  
**Ownership**：每个 backend domain owns setting；UI owns form/confirmation。  
**Side Effects**：real settings changes through owner service only。

### 7. Failure / Forbidden Fallbacks

Unknown config 不用 frontend default 覆盖；partial save 保留 confirmed values；high-risk change 无验证则不应用。禁止 raw env、route/runtime/deployment/scheduler controls。

### 8. Impact / Invariants

Persistence via authoritative services；Supplier preference constrains Autopilot, does not replace it。

### 9. Dependencies

UI-003 + ownership map + notifications + payout profile + maintenance/resource policy。

### 10. Stop Conditions

STOP IF setting 无 backend owner、需 raw DB/env mutation、或给 Supplier deployment/runtime/route authority。

---

## 第三层：验收层（Definition of Done）

- [ ] every setting has authoritative owner。
- [ ] failed fields remain not applied。
- [ ] payout/identity uses required validation。
- [ ] maintenance window only declares constraints。
- [ ] no runtime/route/deployment controls。
- [ ] cross-Supplier isolation verified。
- [ ] branch + PR。
