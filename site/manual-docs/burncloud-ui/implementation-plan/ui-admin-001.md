---
title: "UI-ADMIN-001：实现 Admin Overview"
slug: /burncloud-ui/implementation-plan/ui-admin-001/
---

# UI-ADMIN-001：实现 Admin Overview

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003 + Platform Revenue / Verified Cost / Capacity / Availability**

> 产品合同：[/burncloud-ui/admin/overview/](/burncloud-ui/admin/overview/)

### TL;DR

Admin Overview 是 Business + Infrastructure Command Center：先回答 Today Revenue、Gross Margin、Online GPU Capacity、API Availability，再告诉 Admin 最值得关注的 Supply/Capacity/Demand/Economics 风险。

### 背景与动机（Why）

current Overview 已经能读取 system metrics、Channels、Logs、Tokens、Usage、Billing，但目标首页不是 setup dashboard，也不能把 Buyer billing 当平台 Revenue。Admin 需要系统级结论而不是原始指标墙。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Revenue / Margin | 不显示 Buyer secret |
| Online Capacity | 不逐 PID 操作 |
| API Availability | 不做原始 GPU 信息墙 |
| Needs Attention | 不前端猜成本/毛利 |

### 审批者关注点（Reviewer Focus）
1. Gross Margin 是否只在 cost complete 时显示？
2. Needs Attention 是否有原因/影响/动作/结果？
3. 首页是否先给结论而不是原始 infrastructure dump？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立 platform-level Admin Overview composition，不在页面定义 Revenue/Cost/Capacity truth。

### 2. Evidence

- STATIC CONFIRMED — `critical_pages/dashboard.rs::Overview` 已有真实 operational data fragments。
- STATIC CONFIRMED — current page 是 setup/traffic oriented，不是 target economics/capacity command center。
- UNKNOWN — platform Revenue ledger、verified cost/Gross Margin、online GPU capacity aggregation、cross-domain risk summary。
- TARGET CONFIRMED — cost incomplete 时禁止 fake precise Margin。

### 3. Entry / Starting Point

current Overview UI/resource patterns；Admin workspace；Revenue/Cost/Capacity/Availability/Risk summary services。

### 4. Reuse Targets / Do Not Recreate

Reuse：existing observability/channel/log/status/partial-failure patterns。  
Do Not Recreate：frontend Revenue/Margin engine、user billing as platform revenue、raw PID dashboard。

### 5. Scope

Allowed：Admin Overview/read-only aggregates/drilldowns。  
Avoid：Revenue/Cost/Capacity engines、payments、scheduler/process controls。

### 6. Behavior Contract

**Inputs**：Admin + revenue/cost/capacity/availability/risk facts。  
**Outputs**：platform conclusions + Needs Attention/drilldown。  
**Ownership**：domain services own facts；Overview composes。  
**Side Effects**：read-only；high-risk action 在 Operations/domain page。

### 7. Failure / Forbidden Fallbacks

Missing cost => Margin Unknown/Estimated；partial failure 保留 confirmed metrics；action HTTP 200 不等于 recovery verified。禁止 Buyer secret/client economics/per-PID normal control。

### 8. Impact / Invariants

Read-only platform analytics；Admin auth；Overview gives conclusions not raw control；Margin requires verified cost。

### 9. Dependencies

UI-003 + Revenue + Verified Cost/Margin semantics + Capacity + Availability + Needs Attention summaries。

### 10. Stop Conditions

STOP IF target metrics 需要 frontend formulas/mock、user billing 被重解释成 platform revenue、或 Overview 必须实现 domain action engine。

---

## 第三层：验收层（Definition of Done）

- [ ] Revenue/Margin/Capacity/Availability authoritative。
- [ ] incomplete cost never fake precise Margin。
- [ ] Needs Attention includes reason/impact/action/result。
- [ ] no per-GPU/PID daily operation burden。
- [ ] partial/recovered states truthful。
- [ ] branch + PR。
