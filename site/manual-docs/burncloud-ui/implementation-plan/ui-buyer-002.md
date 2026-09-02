---
title: "UI-BUYER-002：实现 Buyer Marketplace"
slug: /burncloud-ui/implementation-plan/ui-buyer-002/
---

# UI-BUYER-002：实现 Buyer Marketplace

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Buyer**  
**功能依赖：UI-003、UI-007、UI-008 + Product Catalog / Tier / Pricing / Availability**

> 产品合同：[/burncloud-ui/buyer/marketplace/](/burncloud-ui/buyer/marketplace/)  
> Canonical production route：`/console/buyer/marketplace`

### TL;DR
Marketplace 是“模型商店”，不是 GPU Marketplace。Buyer 选择 Model/Tier；BurnCloud 决定 Provider、Local 或未来 Network 的执行位置。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Model/description/price | 不展示 GPU/Supplier/IDC |
| Availability/Tier/context | 不让 Buyer 选 Provider |
| Search/Filter/Advanced | 不把 Channel rows 当 product catalog |
| Use Model → Playground | 不让 legacy `/models` 变成本页 canonical path |

### 审批者关注点（Reviewer Focus）
1. Catalog 是否来自 approved product identity？
2. Price/Availability 是否可追溯？
3. legacy `/models` 是否保持 Admin/operator 原语义？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
提供 Buyer-safe product catalog，以 canonical Model/Tier 为产品选择单位。

### 2. Evidence
- STATIC CONFIRMED — current Models 从 Channel 列表构建可用性视图，属于 operator supply evidence。
- UNKNOWN — approved Product Catalog/Manifest product projection。
- UNKNOWN — authoritative Tier/Pricing/Buyer availability contracts。

### 3. Entry / Starting Point
current Models pattern/evidence only、Product Catalog backend、UI-003/007/008。Canonical route 只来自 UI-008。

### 4. Reuse Targets / Do Not Recreate
Reuse：model identity、search/filter patterns、Buyer-safe serving facts、shared locale formatter。  
Do Not Recreate：Channel-scraped catalog、GPU marketplace、client pricing、Workbench mock models。

### 5. Scope
Allowed：Marketplace list/detail/search/filter/Use Model navigation。  
Avoid：Product Catalog backend architecture、Provider/Route management、runtime/download。

### 6. Behavior Contract
**Inputs**：Buyer-authorized identity + authoritative catalog/pricing/availability/Tier + locale。  
**Outputs**：localized Buyer product list/detail + Playground navigation。  
**Ownership**：Product/Pricing/Serving services own facts。  
**Side Effects**：navigation only。

### 7. Failure / Forbidden Fallbacks
Missing price/availability → Unknown；partial failure 保留已确认产品；无 authoritative catalog 则阻塞。禁止 raw Channel/GPU/Supplier、URL 获权、把 `/models` 动态解释为 Marketplace。

### 8. Impact / Invariants
Buyer chooses Model/Tier, not infrastructure。Model IDs 不翻译。Canonical route `/console/buyer/marketplace`。

### 9. Dependencies
UI-003、UI-007、UI-008 + Product Catalog/Manifest + Tier/Pricing/Availability。

### 10. Stop Conditions
STOP IF catalog 只能从 Channel rows 推导、必须暴露内部 topology、route 需违反 UI-008、或需要改变 Router behavior。

---

## 第三层：验收层（Definition of Done）
- [ ] Product catalog authoritative。
- [ ] canonical route 与 UI-008 一致，legacy `/models` 不指向本页。
- [ ] Buyer authorization/tenant scope 验证。
- [ ] Price/Availability/Tier 可追溯。
- [ ] Default 不出现 GPU/Supplier/IDC/internal Route。
- [ ] Use Model 进入 `/console/buyer/playground`。
- [ ] user-facing copy/i18n/formatting 符合 UI-007；Model IDs 不翻译。
- [ ] branch + PR。
