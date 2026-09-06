---
title: "UI-SUPPLIER-006：实现 Supplier Settlements"
slug: /burncloud-ui/implementation-plan/ui-supplier-006/
---

# UI-SUPPLIER-006：实现 Supplier Settlements

<!-- UI-ARCHITECTURE-DEPENDENCY: REQUIRED -->
> **Mandatory Architecture Dependency（强制）**
>
> 本实施单元必须遵守 [BurnCloud UI Architecture Contract](/burncloud-ui/architecture/)。Architecture Contract 是本页、READY Engineering Issue、Task Contract 与 Production Dioxus 实现的上位约束。
>
> - 实施前必须读取 [Directory Contract](/burncloud-ui/architecture/directory-contract/)、[Authorization Contract](/burncloud-ui/architecture/authorization-contract/)、[API Boundary](/burncloud-ui/architecture/api-boundary/) 与 [Code Ownership](/burncloud-ui/architecture/code-ownership/) 中适用规则；
> - Task Contract 必须明确 `Allowed Paths / Conditional Paths / Forbidden Paths`；
> - 本页只能增加更严格的限制，**不能放宽 Architecture Contract**；
> - 若页面需求与 Architecture Contract 冲突，必须 `STOP → Architecture Dependency / Foundation Issue`，不得由 AI/Codex 自行扩大 scope 或修改 Protected Architecture Zone。
>
> `Implementation convenience != architecture authority`；`CI green != permission to violate the Architecture Contract`。
<!-- UI-ARCHITECTURE-DEPENDENCY: END -->

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Supplier**  
**功能依赖：UI-003、UI-007、UI-008 + Settlement / Payout Ledger contract**

> 产品合同：[/burncloud-ui/supplier/settlements/](/burncloud-ui/supplier/settlements/)  
> Canonical production route：`/console/supplier/settlements`

### TL;DR
Supplier Settlements 只展示自己从 Payable → Processing → Paid/Failed 的真实结算生命周期和付款证据；不得把请求提交或 HTTP 200 显示成 Paid。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| payable/processing/paid/failed | 不 client-compute payable |
| settlement history | 不直接调用 payment provider |
| payout evidence/reference | 不显示其他 Supplier |
| localized status/currency | 不翻译 tx/reference IDs |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/supplier/settlements` 的 Supplier-owned settlement lifecycle view。

### 2. Evidence
- STATIC CONFIRMED — Target requires Payable/Processing/Paid/Failed distinction。
- UNKNOWN — current-main Supplier settlement ledger/payout provider result contract。

### 3. Entry / Starting Point
future settlement ledger/provider result、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：finalized earnings、settlement ledger、provider result。  
Do Not Recreate：client payable ledger、payment provider integration。

### 5. Scope
Allowed：own settlement list/detail/status/evidence and approved request action if backend supports。  
Avoid：Admin batch payout、payment engine、earnings computation。

### 6. Behavior Contract
**Inputs**：Supplier identity + authoritative settlement records/provider results + locale。  
**Outputs**：payable/payment lifecycle and evidence。  
**Ownership**：Settlement/payment services own state。  
**Side Effects**：only explicitly supported Supplier request action。

### 7. Failure / Forbidden Fallbacks
Submission != Processing/Paid unless authoritative state says so；partial/failed stays truthful。禁止 client payable calculation or optimistic paid。

### 8. Impact / Invariants
Financial sensitive；route `/console/supplier/settlements`；Payable != Processing != Paid。

### 9. Dependencies
UI-003、007、008 + Settlement/Payout ledger/result contracts。

### 10. Stop Conditions
STOP IF payable must be client-computed、Paid lacks provider/ledger verification、or page needs direct provider call。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] only Supplier-owned settlements visible。
- [ ] Payable/Processing/Paid/Failed distinct。
- [ ] provider/ledger result required for Paid。
- [ ] money/date/status localized; tx/reference IDs stable。
- [ ] branch + PR。
