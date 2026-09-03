---
title: "UI-SUPPLIER-001：实现 Supplier Overview"
slug: /burncloud-ui/implementation-plan/ui-supplier-001/
---

# UI-SUPPLIER-001：实现 Supplier Overview

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003、UI-007、UI-008 + Supplier Registry / Node / Earnings contracts**

> 产品合同：[/burncloud-ui/supplier/overview/](/burncloud-ui/supplier/overview/)  
> Canonical production route：`/console/supplier/overview`

### TL;DR
Supplier 首页回答“我的资源是否健康、今天贡献了什么、今天赚了多少、哪里需要注意”。它是供应商经营与资源状态首页，不是部署控制台。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| earnings/resource/reliability summary | 不选择模型部署 |
| health/attention | 不控制 Traffic |
| contribution summary | 不直接 Start/Stop Runtime |
| localized state/explanation | 不翻译 Node/Model IDs |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
在 `/console/supplier/overview` 提供 Supplier-owned business/resource summary。

### 2. Evidence
- STATIC CONFIRMED — Target 需要 Supplier earnings/resources/reliability mental model。
- UNKNOWN — current-main authoritative Supplier registry、Contribution、Earnings、Reliability unified contracts。

### 3. Entry / Starting Point
future Supplier services、Node telemetry、shared dashboard patterns、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：Node/resource telemetry、Contribution/Earnings/Settlement services、shared status/i18n。  
Do Not Recreate：client Supplier registry、earnings formula、manual deployment controller。

### 5. Scope
Allowed：read-only summary、attention navigation、approved graceful operational requests。  
Avoid：Model/Runtime/Traffic authority、earnings engine。

### 6. Behavior Contract
**Inputs**：Supplier-authorized identity + own resources/contribution/earnings/reliability + locale。  
**Outputs**：summary metrics/alerts/actions。  
**Ownership**：backend Supplier/Node/Finance services own facts。  
**Side Effects**：navigation only unless a separately authorized action exists。

### 7. Failure / Forbidden Fallbacks
Unknown earnings/health 不显示 0/Healthy。禁止从 Provider/Channel 推断 Supplier、URL 获权、UI 直接控制 Runtime。

### 8. Impact / Invariants
Supplier tenant scope server-side；canonical route `/console/supplier/overview`；observe &gt; control。

### 9. Dependencies
UI-003、007、008 + Supplier/Node/Earnings/Reliability contracts。

### 10. Stop Conditions
STOP IF Supplier identity 必须从 Channel 推断、财务数据需 client 计算、或页面必须获得 Runtime/Traffic authority。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Supplier authorization/tenant isolation server-side。
- [ ] earnings/resources/reliability authoritative。
- [ ] no Deploy/Runtime/Traffic controls。
- [ ] Unknown/Partial/Error/Recovered truthful。
- [ ] currency/number/status copy 遵循 UI-007；machine IDs 不翻译。
- [ ] branch + PR。
