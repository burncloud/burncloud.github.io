---
title: "UI-ADMIN-002：实现 Admin Supply"
slug: /burncloud-ui/implementation-plan/ui-admin-002/
---

# UI-ADMIN-002：实现 Admin Supply

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003、UI-007、UI-008 + Supplier / Node / Hardware / Provider supply contracts**

> 产品合同：[/burncloud-ui/admin/supply/](/burncloud-ui/admin/supply/)  
> Canonical production route：`/console/admin/supply`

### TL;DR
Supply 回答“平台现在有多少可靠供给、来自哪里、健康度如何”。它可以复用 Provider/Channel、Supplier Node、owned IDC、cloud reservation 等事实，但不能把其中任意一种当全部 Supply。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| supply composition | 不把 Channel=Supplier |
| supplier/node/provider/owned capacity evidence | 不把 Supply=Capacity headroom |
| health/geography/type | 不直接调度 GPU |
| Advanced drilldown | 不泄露 secrets |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/admin/supply` 的 authoritative platform supply view。

### 2. Evidence
- STATIC CONFIRMED — current Providers/Channels 有真实 upstream supply facts。
- UNKNOWN — canonical Supplier registry/Node supply/owned capacity/cloud reservation unified projection。

### 3. Entry / Starting Point
existing Provider/Channel pages as evidence/reuse、future Supplier/Node inventory、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：Provider/Channel facts、Supplier/Node inventory、health/resource evidence。  
Do Not Recreate：client supply registry、Channel→Supplier inference。

### 5. Scope
Allowed：supply aggregation/read/detail/filters。  
Avoid：capacity planning engine、route mutation、raw credentials。

### 6. Behavior Contract
**Inputs**：Admin identity + authoritative supply facts + locale。  
**Outputs**：supply totals/composition/health/drilldown。  
**Ownership**：Supply constituent services own facts。  
**Side Effects**：read-only。

### 7. Failure / Forbidden Fallbacks
Missing Supplier registry ≠ infer from Channel；partial sources remain partial. Legacy `/providers` may remain Advanced/Legacy until parity。

### 8. Impact / Invariants
Admin read-only；route `/console/admin/supply`；Supply != Capacity != Demand。

### 9. Dependencies
UI-003、007、008 + supply contracts。

### 10. Stop Conditions
STOP IF Supplier must be inferred from Channel、secrets required、or Supply page must implement scheduler/routing mutations。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] supply sources explicit and authoritative。
- [ ] Channel/Supplier/Owned/Cloud concepts not collapsed incorrectly。
- [ ] legacy Providers capability preserved until parity/removal decision。
- [ ] i18n/formatting follows UI-007；IDs stable。
- [ ] branch + PR。
