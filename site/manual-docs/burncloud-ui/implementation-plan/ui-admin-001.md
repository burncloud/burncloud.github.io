---
title: "UI-ADMIN-001：实现 Admin Overview"
slug: /burncloud-ui/implementation-plan/ui-admin-001/
---

# UI-ADMIN-001：实现 Admin Overview

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003、UI-007、UI-008 + Revenue / Cost / Capacity / Reliability contracts**

> 产品合同：[/burncloud-ui/admin/overview/](/burncloud-ui/admin/overview/)  
> Canonical production route：`/console/admin/overview`

### TL;DR
Admin Overview 只提供平台级经营与基础设施结论：Revenue/Cost/Margin、Supply/Capacity/Demand、Reliability 与需要人工处理的例外。不是 Provider/Route/GPU 列表首页。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| platform economics summary | 不猜 Gross Margin |
| supply/capacity/demand conclusions | 不逐 GPU 调度 |
| reliability/attention | 不把 Admin URL 当权限 |
| Operations drilldown | 不直接执行高风险动作 |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/admin/overview` 的 Admin command overview。

### 2. Evidence
- STATIC CONFIRMED — current Overview 有多个真实数据片段，但 mental model 混合。
- UNKNOWN — unified platform revenue/cost/capacity/demand/reliability projections。

### 3. Entry / Starting Point
current Overview patterns、future platform domain services、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：authoritative finance/capacity/demand/reliability facts、shared metrics/status。  
Do Not Recreate：client gross-margin engine、capacity engine、manual GPU scheduler。

### 5. Scope
Allowed：read-only executive summary + drilldowns。  
Avoid：domain engines、routing/runtime control、financial mutation。

### 6. Behavior Contract
**Inputs**：Admin-authorized identity + platform facts + locale。  
**Outputs**：platform conclusions/alerts/navigation。  
**Ownership**：domain services own facts。  
**Side Effects**：read-only/navigation。

### 7. Failure / Forbidden Fallbacks
Incomplete cost → Margin unavailable/estimated；unknown capacity 不显示 Healthy。禁止 URL 获权、client business truth。

### 8. Impact / Invariants
Admin-only read；route `/console/admin/overview`；estimated != final。

### 9. Dependencies
UI-003、007、008 + platform finance/capacity/demand/reliability contracts。

### 10. Stop Conditions
STOP IF Overview must compute domain truth client-side、requires direct runtime control、or Admin authorization cannot be server-side verified。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Admin workspace/API authorization verified。
- [ ] Revenue/Cost/Margin/Capacity/Demand facts authoritative or explicit Unknown。
- [ ] no fake precise margin/capacity。
- [ ] money/number/time/status localized via UI-007。
- [ ] branch + PR。
