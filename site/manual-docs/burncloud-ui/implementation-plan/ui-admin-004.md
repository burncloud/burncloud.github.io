---
title: "UI-ADMIN-004：实现 Admin Demand"
slug: /burncloud-ui/implementation-plan/ui-admin-004/
---

# UI-ADMIN-004：实现 Admin Demand

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003 + Demand Aggregation / Tier/Region Attribution / Forecast**

> 产品合同：[/burncloud-ui/admin/demand/](/burncloud-ui/admin/demand/)

### TL;DR

Demand 展示 Requests、Tokens、Concurrency、增长/峰值和 Forecast，按 Model/Tier/Region 下钻。Prediction 是事实之外的预测，必须与 Actual 分开。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Actual demand trend | 不显示 Buyer Prompt |
| Model/Tier/Region breakdown | 不显示 API secret |
| Forecast + confidence | 不用 UI 写 predictor |
| link to Capacity | 不在这里做 capacity action |

### 审批者关注点（Reviewer Focus）
1. Actual/Forecast 是否清楚分离？
2. Model/Tier 是否与 Capacity/Usage 一致？
3. Forecast failure 是否保留 Actual？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 authoritative demand analytics + prediction view，为 Capacity 提供 explainable input。

### 2. Evidence

- STATIC CONFIRMED — current logs/usage 可提供 request/token evidence fragments。
- STATIC CONFIRMED — current logs page 不是 demand forecast service。
- UNKNOWN — concurrency time-series、Tier/Region attribution、Forecast/confidence service。

### 3. Entry / Starting Point

Admin workspace；metering/request aggregates；canonical Model/Tier；Demand prediction service；Admin Capacity。

### 4. Reuse Targets / Do Not Recreate

Reuse：metering/request facts + canonical model identity。  
Do Not Recreate：frontend forecast model、private prompt analysis、unrelated UI-derived region/tier。

### 5. Scope

Allowed：Demand page/filter/chart/forecast explanation/Capacity links。  
Avoid：predictor implementation、capacity action、routing/scheduling changes。

### 6. Behavior Contract

**Inputs**：authoritative actual demand + product attribution + forecast/confidence。  
**Outputs**：Actual/Forecast trends and risk links。  
**Ownership**：Demand service owns aggregation/prediction；UI presents。  
**Side Effects**：read-only。

### 7. Failure / Forbidden Fallbacks

Forecast failure 保留 Actual；missing Region/Tier => Unknown；forecast 不伪装事实。禁止 client forecast/private prompt/secret use。

### 8. Impact / Invariants

Read-only analytics；Actual ≠ Forecast；Demand predicts, Capacity/Operations acts。

### 9. Dependencies

UI-003 + demand aggregation + Tier/Region attribution + forecast/confidence + compatible Capacity semantics。

### 10. Stop Conditions

STOP IF forecast 必须在 UI 生成、facts 需要 Buyer sensitive content、或 Model/Tier semantics 与 Capacity 冲突。

---

## 第三层：验收层（Definition of Done）

- [ ] Actual/Forecast separated。
- [ ] Model/Tier breakdown matches Usage/Capacity。
- [ ] Forecast has confidence/source。
- [ ] Buyer private content absent。
- [ ] demand risk links to Capacity。
- [ ] forecast partial failure preserves Actual。
- [ ] branch + PR。
