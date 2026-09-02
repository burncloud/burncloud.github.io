---
title: "UI-SUPPLIER-004：实现 Supplier Reliability"
slug: /burncloud-ui/implementation-plan/ui-supplier-004/
---

# UI-SUPPLIER-004：实现 Supplier Reliability

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003 + Reliability Service / Node Evidence / Event Semantics**

> 产品合同：[/burncloud-ui/supplier/reliability/](/burncloud-ui/supplier/reliability/)

### TL;DR

Reliability 让 Supplier 理解自己的稳定性等级、为什么变化、需要修什么。默认给可理解等级与证据，不暴露其他 Supplier、隐藏可被游戏化阈值或 Traffic Weight 算法。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Reliability Level | 不暴露 hidden scoring internals |
| Availability Trend | 不显示 other Supplier scores |
| Unexpected Offline | 不显示 Traffic Weight logic |
| Actionable Reasons | 不在前端计算 score |

### 审批者关注点（Reviewer Focus）
1. level 是否可解释？
2. active vs recovered 是否分离？
3. actionable reason 是否有下一步？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

呈现 authoritative Supplier reliability result + evidence + actionability，不在 UI 定义 reliability algorithm。

### 2. Evidence

- TARGET CONFIRMED — levels/availability/unexpected offline/actionable reasons。
- TARGET CONFIRMED — forbid other-Supplier/internal gameable thresholds。
- UNKNOWN — authoritative Reliability service、Supplier lifecycle events、network/performance evidence、benchmark records。

### 3. Entry / Starting Point

UI-003；Reliability service；Node telemetry/lifecycle evidence；approved benchmark history。

### 4. Reuse Targets / Do Not Recreate

Reuse：canonical evidence/events/benchmark + shared status/chart patterns。  
Do Not Recreate：frontend reliability formula、local thresholds、second incident store。

### 5. Scope

Allowed：Reliability page/evidence/reasons/active-vs-recovered。  
Avoid：Reliability engine、scheduler/traffic algorithm、cross-Supplier comparison。

### 6. Behavior Contract

**Inputs**：Supplier scope + authoritative reliability + reasons/events。  
**Outputs**：level/trend/reasons/action/history。  
**Ownership**：Reliability/Telemetry own classification/evidence；UI explains。  
**Side Effects**：read-only。

### 7. Failure / Forbidden Fallbacks

Missing evidence => Unknown reason，不猜 score；partial telemetry 保留 confirmed facts。禁止 frontend score、other Supplier data、hidden thresholds。

### 8. Impact / Invariants

Read-only；evidence-backed；Recovered ≠ Active Problem；Supplier privacy server-side。

### 9. Dependencies

UI-003 + Reliability result + Node availability/network/performance evidence + active/recovered event semantics。

### 10. Stop Conditions

STOP IF level 必须由 UI 计算、需要 other Supplier data、hidden thresholds 必须暴露、或需要改变 traffic/scheduler behavior。

---

## 第三层：验收层（Definition of Done）

- [ ] Reliability level authoritative/explainable。
- [ ] reasons trace real telemetry/events。
- [ ] Active Problem / Recovered distinct。
- [ ] action only where Supplier intervention needed。
- [ ] no other-Supplier/internal scoring exposure。
- [ ] branch + PR。
