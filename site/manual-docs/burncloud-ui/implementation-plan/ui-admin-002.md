---
title: "UI-ADMIN-002：实现 Admin Supply"
slug: /burncloud-ui/implementation-plan/ui-admin-002/
---

# UI-ADMIN-002：实现 Admin Supply

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003 + Supplier Registry / Node Inventory / Hardware / Reliability / Verification**

> 产品合同：[/burncloud-ui/admin/supply/](/burncloud-ui/admin/supply/)

### TL;DR

Supply 回答“平台现在有多少可靠算力供应”。按 Supplier→Node→GPU 下钻，并解释 Reliability/Verification；它不是 Provider Channel 页面，也不是逐进程控制台。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Online Supply / Supplier Health | 不把 Channel 当 Supplier |
| Node/GPU/Region | 不逐 PID 管理 |
| Reliability/Verification | 不显示 Buyer Billing |
| drilldown | 不显示 Prompt/Secret |

### 审批者关注点（Reviewer Focus）
1. Supply total 是否与 Node inventory 一致？
2. Supplier identity 是否独立于 Provider Channel？
3. Trust/Verification 是否 evidence-backed？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 authoritative platform supply inventory/health/trust view。

### 2. Evidence

- STATIC CONFIRMED — current production 有 Providers/Channels/system metrics，但它们不是 Supplier/Node/GPU supply domain。
- TARGET CONFIRMED — page 需要 Supplier registry/Node inventory/HardwareProfile/Reliability/Verification。
- UNKNOWN — 上述 authoritative domain contracts 当前是否存在/完整。

### 3. Entry / Starting Point

Admin workspace；Supplier registry；Node inventory；HardwareProfile/ResourceSnapshot；Reliability/Verification services。

### 4. Reuse Targets / Do Not Recreate

Reuse：canonical Node hardware/telemetry + future Supplier/trust services；现有 table/filter patterns。  
Do Not Recreate：Channel→Supplier inference、second resource registry、PID control console。

### 5. Scope

Allowed：Supply page/read-only aggregates/drilldown。  
Avoid：registry/telemetry/reliability backend、scheduler/process controls、Buyer data。

### 6. Behavior Contract

**Inputs**：Admin + Supplier/Node/hardware/reliability/verification facts。  
**Outputs**：supply totals/filter/drilldown/attention。  
**Ownership**：Supply/Resource/Trust domains own facts；UI presents。  
**Side Effects**：read-only。

### 7. Failure / Forbidden Fallbacks

Partial inventory failure 显示 confirmed scope + Unknown；verification unknown ≠ Trusted。禁止把 Channels relabel Supplier 或以 UI 构造 trust。

### 8. Impact / Invariants

Read-only infrastructure/business supply；Supplier identity ≠ Provider Channel；Trust requires evidence。

### 9. Dependencies

UI-003 + Supplier Registry + Node Inventory + Hardware + Reliability + Verification。

### 10. Stop Conditions

STOP IF Provider Channels 必须被当 Supplier、Trust 需要猜测、或页面需要 routine PID/process operation。

---

## 第三层：验收层（Definition of Done）

- [ ] Supply total reconciles inventory。
- [ ] Supplier/Node/GPU drilldown preserves same facts。
- [ ] Verification/Reliability explainable。
- [ ] no Channel/Supplier identity confusion。
- [ ] no per-PID normal control。
- [ ] partial/unknown states truthful。
- [ ] branch + PR。
