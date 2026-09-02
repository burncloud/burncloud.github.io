---
title: "UI-ADMIN-003：实现 Admin Capacity"
slug: /burncloud-ui/implementation-plan/ui-admin-003/
---

# UI-ADMIN-003：实现 Admin Capacity

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003 + Capacity / Demand / Node Readiness / Provider Capacity / Economics / Autopilot**

> 产品合同：[/burncloud-ui/admin/capacity/](/burncloud-ui/admin/capacity/)

### TL;DR

Capacity 围绕 Model/Tier 展示 Available Capacity、Headroom、Utilization、Risk，以及 BurnCloud 已经自动做了什么。不是“有多少 GPU”页面，也不把调度交给 Admin。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Model/Tier Capacity | 不用 Channel count 代替 capacity |
| Headroom/Risk/Utilization | 不逐 GPU 默认调度 |
| Local/Provider/External explanation | 不管理 PID/Port |
| Proposal cost/margin impact | 不在 UI 做 scheduler |

### 审批者关注点（Reviewer Focus）
1. risk 是否按 Model/Tier 业务语义表达？
2. auto action 是否有 Verify？
3. high-cost proposal 是否有 cost/margin/impact？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 Model/Tier capacity/risk view + Autopilot recovery/proposal transparency。

### 2. Evidence

- STATIC CONFIRMED — current catalog 可得 model availability/redundancy，但不等于 capacity/headroom。
- STATIC CONFIRMED — current system metrics 是 host metrics，不等于 cross-supply capacity。
- UNKNOWN — Capacity aggregation、Demand forecast、Node readiness capacity、provider/external economics、Autopilot verify contracts。

### 3. Entry / Starting Point

Admin workspace；canonical model identity；Capacity/Demand/Node/Provider/Economics/Operations services。

### 4. Reuse Targets / Do Not Recreate

Reuse：Router model identity/provider availability + canonical Node capacity + status/proposal patterns。  
Do Not Recreate：Channel-count capacity formula、UI scheduler、PID/port controls。

### 5. Scope

Allowed：Capacity page/risk/recovery/proposal presentation。  
Avoid：scheduler/capacity engine、Node runtime/process、routing algorithm。

### 6. Behavior Contract

**Inputs**：Model/Tier + capacity/demand/readiness/economic/action facts。  
**Outputs**：capacity/headroom/risk + action/verify/proposal view。  
**Ownership**：Capacity/Autopilot/Economics decide；UI explains/gates approved high-risk proposal。  
**Side Effects**：read-only by default。

### 7. Failure / Forbidden Fallbacks

Unknown capacity/headroom stays Unknown；forecast labeled forecast；action not success until Verify。禁止 channel-count formula/manual GPU scheduler。

### 8. Impact / Invariants

Capacity = product-serving capacity, not raw GPU count；low-risk Autopilot；high-risk Human by Exception；Verify mandatory。

### 9. Dependencies

UI-003 + Capacity + Demand + Node readiness + Provider/external capacity/economics + Autopilot Proposal/Verify。

### 10. Stop Conditions

STOP IF capacity 只能从 raw Channel/GPU counts 推导、UI 必须 schedule GPUs、Verify 不存在、或 high-risk economics 只能猜。

---

## 第三层：验收层（Definition of Done）

- [ ] Model/Tier capacity authoritative。
- [ ] Headroom/Risk explainable。
- [ ] Actual/Forecast separated。
- [ ] auto action has Verify result。
- [ ] high-risk proposal shows cost/margin/impact。
- [ ] no default manual GPU scheduler/PID controls。
- [ ] branch + PR。
