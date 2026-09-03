---
title: "UI-BUYER-005：实现 Buyer Usage"
slug: /burncloud-ui/implementation-plan/ui-buyer-005/
---

# UI-BUYER-005：实现 Buyer Usage

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Buyer**  
**功能依赖：UI-003、UI-007、UI-008 + authoritative Usage attribution**

> 产品合同：[/burncloud-ui/buyer/usage/](/burncloud-ui/buyer/usage/)  
> Canonical production route：`/console/buyer/usage`

### TL;DR
Usage 解释 Buyer 自己用了多少请求/Token、哪些模型贡献了用量、趋势如何；不把 Billing ledger、Admin logs 或 Provider telemetry 混成同一事实源。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| requests/tokens/time trends | 不计算平台 Revenue |
| model attribution | 不读取跨 tenant logs |
| export if authoritative | 不前端重建 metering |
| locale-aware numbers/time | 不翻译 model IDs |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/buyer/usage` 的 tenant-safe usage analytics。

### 2. Evidence
- STATIC CONFIRMED — current backend 已有 user-scoped usage/billing fragments。
- STATIC CONFIRMED — current Billing 页面包含 request/token/model spend evidence，但 Usage 与 Billing 目标语义应分离。
- UNKNOWN — 完整时间粒度/模型归因/export contract。

### 3. Entry / Starting Point
backend user usage/billing summary、existing analytics UI patterns、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：metering projections、model identity、chart/table patterns、shared formatters。  
Do Not Recreate：client metering engine、Admin log export、billing ledger。

### 5. Scope
Allowed：usage totals/trends/model breakdown/export where supported。  
Avoid：payment/invoice、platform Revenue、Provider telemetry。

### 6. Behavior Contract
**Inputs**：Buyer identity + scoped usage facts + time range + locale。  
**Outputs**：request/token/model/time analytics。  
**Ownership**：Metering/Usage service owns facts。  
**Side Effects**：read/export only。

### 7. Failure / Forbidden Fallbacks
Missing bucket/attribution → Unknown/partial，不填 0。禁止跨 tenant logs、client recomputation、URL 获权。

### 8. Impact / Invariants
Read-only analytics；server-side tenant scope；route `/console/buyer/usage`；locale-aware formatting only。

### 9. Dependencies
UI-003、007、008 + authoritative usage attribution。

### 10. Stop Conditions
STOP IF usage 必须从 Admin logs 前端过滤、metering 需在 UI 重建、或路由权限不明确。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] tenant isolation server-side。
- [ ] request/token/model totals 可追溯。
- [ ] partial attribution truthful。
- [ ] number/date/time format 使用 UI-007。
- [ ] model IDs 不翻译。
- [ ] branch + PR。
