---
title: "UI-BUYER-003：实现 Buyer Playground"
slug: /burncloud-ui/implementation-plan/ui-buyer-003/
---

# UI-BUYER-003：实现 Buyer Playground

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
**类别：Buyer**  
**功能依赖：UI-003、UI-007、UI-008 + Marketplace + authenticated data-plane proxy + Node demand states**

> 产品合同：[/burncloud-ui/buyer/playground/](/burncloud-ui/buyer/playground/)  
> Canonical production route：`/console/buyer/playground`

### TL;DR
Playground 必须通过真实 BurnCloud data plane 执行模型请求，Buyer 只选 Model/Tier/推理参数，不选 Provider/GPU。Node 本地准备状态只能 Observe/Explain。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Model/Tier/prompt/params | 不选 Provider/GPU |
| real `/v1` request path | 不 bypass Auth/Billing/Router |
| response + usage/latency/trace | 不直接 Download/Start Runtime |
| localized Node status | 不翻译 Model ID/error code |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
在 `/console/buyer/playground` 提供真实、可追溯、Buyer-safe 的 inference test surface。

### 2. Evidence
- STATIC CONFIRMED — current Playground 已通过 authenticated console proxy 触发真实 data-plane request 并保留 route trace。
- STATIC CONFIRMED — Node demand-driven architecture 要求 Provider serving 与 Local preparation 并行，UI 不拥有 Runtime。
- UNKNOWN — Product Tier 与完整 Node lifecycle projection contracts。

### 3. Entry / Starting Point
current Playground/proxy、Marketplace model identity、UI-004、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：existing authenticated proxy、Router/Billing/Auth path、request trace、shared status/i18n。  
Do Not Recreate：direct Provider call、client route engine、Node downloader/runtime controls。

### 5. Scope
Allowed：prompt/model/tier/params、run/cancel where supported、response/usage/trace/status presentation。  
Avoid：routing policy、Provider selection、Node process lifecycle。

### 6. Behavior Contract
**Inputs**：Buyer identity/token、Model/Tier/prompt/params、locale。  
**Outputs**：real response or structured failure + usage/latency/route receipt + localized Node serving explanation。  
**Ownership**：Router/Data Plane/Node own execution；UI owns interaction/presentation。  
**Side Effects**：real inference usage/billing occurs。

### 7. Failure / Forbidden Fallbacks
Request failure 不伪装 success；MODEL_PREPARING 等 code 保留 raw machine value + localized explanation。禁止直连 Provider、URL 获权、Runtime 操作。

### 8. Impact / Invariants
Data-plane call yes；Billing/Auth/Router semantics unchanged；route `/console/buyer/playground`；API/model/error identifiers unlocalized。

### 9. Dependencies
UI-003、007、008、Marketplace、UI-004 Node states、real proxy/data-plane contract。

### 10. Stop Conditions
STOP IF request 需要绕过 existing Router/Auth/Billing、Buyer 必须选择 Provider/GPU、或 UI 必须管理模型进程。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Buyer auth/tenant scope 验证。
- [ ] 请求真实经过 BurnCloud Router/Auth/Billing。
- [ ] Provider/Local 选择不交给 Buyer。
- [ ] Node preparing/ready/failure 使用 UI-004 + UI-007。
- [ ] error/model/API identifiers 不翻译。
- [ ] success/error/timeout/preparing/recovered E2E。
- [ ] branch + PR。
