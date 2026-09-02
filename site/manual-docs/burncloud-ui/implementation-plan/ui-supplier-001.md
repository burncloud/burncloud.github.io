---
title: "UI-SUPPLIER-001：实现 Supplier Overview"
slug: /burncloud-ui/implementation-plan/ui-supplier-001/
---

# UI-SUPPLIER-001：实现 Supplier Overview

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003 + Supplier Scope / Earnings / Node Telemetry / Reliability**

> 产品合同：[/burncloud-ui/supplier/overview/](/burncloud-ui/supplier/overview/)

### TL;DR

Supplier 首页先回答“我的机器正常吗、今天贡献和收入怎么样”。顶部优先 Today Earnings、Online GPUs、GPU Utilization、Inference Today；只有真正需要 Supplier 行动的问题才进入 Needs Attention。

### 背景与动机（Why）

Supplier 不是平台运维员，也不是模型调度员。首页应该展示资源结果、贡献、收益和需要其本人处理的问题，而不是 Router、Runtime、PID 或模型部署控制。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Today Earnings / Online GPUs | 不显示 Buyer identity |
| GPU Utilization / Inference Today | 不显示 Router config |
| Needs Attention / Revenue Trend | 不提供 Deploy Model |
| Resource Health / Recovered | 不显示 Platform Margin |

### 审批者关注点（Reviewer Focus）
1. 四个指标是否来自 Supplier 自己的 authoritative facts？
2. Needs Attention 是否只含需要 Supplier 行动的问题？
3. 自动恢复成功是否从 Active Problem 移出？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立 Supplier-only overview composition，聚合收益、资源、贡献和 actionable health。

### 2. Evidence

- STATIC CONFIRMED — current production 尚无 Supplier workspace/page route。
- STATIC CONFIRMED — current Overview 是 mixed platform/operator dashboard。
- TARGET CONFIRMED — Supplier Overview 需要 Earnings/GPU/Utilization/Inference/Attention。
- UNKNOWN — authoritative Supplier scope、earnings ledger、Node telemetry/HardwareProfile、Supplier-actionable reliability projection。

### 3. Entry / Starting Point

UI-003 Supplier workspace；current Overview UI patterns；未来 Supplier/Node/Earnings/Health services。

### 4. Reuse Targets / Do Not Recreate

Reuse：metric/status/partial-failure patterns + canonical Supplier/Node/Earnings services。  
Do Not Recreate：frontend earnings ledger、Buyer log-derived earnings、second telemetry store、manual deployment controls。

### 5. Scope

Allowed：Supplier Overview/read-only aggregate/navigation。  
Avoid：Supplier registry backend、Node telemetry backend、earnings engine、routing/runtime/deployment actions。

### 6. Behavior Contract

**Inputs**：Supplier scope + earnings/resource/contribution/actionable health。  
**Outputs**：Supplier-only summary + actionable alerts。  
**Ownership**：domain services own facts；page composes。  
**Side Effects**：read-only/navigation。

### 7. Failure / Forbidden Fallbacks

Unknown earnings ≠ `$0`；telemetry partial failure 保留 confirmed earnings/resources；Recovered 不持续红色告警。禁止 Buyer data、Router controls、mock nodes。

### 8. Impact / Invariants

Read-only Supplier analytics；Supplier scope server-side；deployment/routing automation remains BurnCloud-owned。

### 9. Dependencies

UI-003 + Supplier identity/scope + Earnings/Contribution + Node telemetry + reliability event semantics。

### 10. Stop Conditions

STOP IF metrics 只能 mock/client-compute，Buyer data 是必要输入，或页面需要获得 route/runtime/deployment authority。

---

## 第三层：验收层（Definition of Done）

- [ ] 四个顶部指标 authoritative。
- [ ] Supplier isolation verified。
- [ ] Needs Attention truly actionable。
- [ ] Partial/Recovered truthful。
- [ ] no Buyer/Router/manual deployment controls。
- [ ] branch + PR。
