---
title: "UI-SUPPLIER-004：实现 Supplier Reliability"
slug: /burncloud-ui/implementation-plan/ui-supplier-004/
---

# UI-SUPPLIER-004：实现 Supplier Reliability

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003、UI-007、UI-008 + Reliability Evidence contract**

> 产品合同：[/burncloud-ui/supplier/reliability/](/burncloud-ui/supplier/reliability/)  
> Canonical production route：`/console/supplier/reliability`

### TL;DR
Reliability 解释“我的供应质量如何、为什么、怎样改善”，必须由可验证 uptime/health/incident evidence 支撑，不在前端制造一个 opaque score。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| reliability level/evidence | 不 client-compute trust score |
| uptime/incidents/qualification | 不混同 contribution/revenue share |
| reasons + improvement path | 不显示其他 Supplier private data |
| localized explanations | 不翻译 evidence IDs |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/supplier/reliability` 的 evidence-backed reliability view。

### 2. Evidence
- STATIC CONFIRMED — Target 要求 Reliability 与 Level/Contribution/Revenue Share 分离。
- UNKNOWN — current-main Reliability domain contract and evidence model。

### 3. Entry / Starting Point
future Reliability service、Node health/incident evidence、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：health/readiness/incidents/uptime facts、approved reliability policy。  
Do Not Recreate：client scoring engine、opaque combined business score。

### 5. Scope
Allowed：reliability status/history/evidence/reason/qualification roadmap。  
Avoid：policy engine、earnings/contribution computation、Admin cross-supplier details。

### 6. Behavior Contract
**Inputs**：Supplier identity + reliability result + supporting evidence + locale。  
**Outputs**：status/why/how-to-improve。  
**Ownership**：Reliability service owns scoring/policy。  
**Side Effects**：none。

### 7. Failure / Forbidden Fallbacks
Missing evidence → Unknown；不能根据 UI telemetry 临时算分。禁止把 Level/Contribution/Revenue Share 合成 Reliability。

### 8. Impact / Invariants
Read-only trust/reliability；route `/console/supplier/reliability`；evidence-backed。

### 9. Dependencies
UI-003、007、008 + Reliability contract/evidence。

### 10. Stop Conditions
STOP IF score must be computed client-side、evidence unavailable、or unrelated economic concepts must be collapsed。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] reliability authoritative and evidence-backed。
- [ ] Level/Reliability/Contribution/Revenue Share remain distinct。
- [ ] unknown evidence not shown Verified/Healthy。
- [ ] localized explanation; stable evidence IDs unchanged。
- [ ] branch + PR。
