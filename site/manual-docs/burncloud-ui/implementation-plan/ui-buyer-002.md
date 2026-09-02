---
title: "UI-BUYER-002：实现 Buyer Marketplace"
slug: /burncloud-ui/implementation-plan/ui-buyer-002/
---

# UI-BUYER-002：实现 Buyer Marketplace

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Buyer**  
**功能依赖：UI-003 + Product Catalog / Tier / Pricing / Availability**

> 产品合同：[/burncloud-ui/buyer/marketplace/](/burncloud-ui/buyer/marketplace/)

### TL;DR

Marketplace 是“模型商店”，不是 GPU Marketplace。Buyer 选择 Model/Tier；BurnCloud 决定 Provider、Local 或未来 Network 的执行位置。

### 背景与动机（Why）

current `catalog.rs::Models` 从 Channel 推导 model availability/redundancy，适合作为供给证据片段，但它会暴露 Provider/routing mental model，不能直接成为 Buyer 产品目录。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Model/description/price | 不展示 GPU/Supplier/IDC |
| Availability/Tier/context | 不让 Buyer 选 Provider |
| Search/Filter/Advanced | 不把 Channel rows 当 product catalog |
| Use Model → Playground | 不创建前端 pricing DB |

### 审批者关注点（Reviewer Focus）
1. catalog 是否来自 approved product identity？
2. Price/Availability 是否可追溯？
3. execution location 是否仍由 BurnCloud 管理？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 Buyer-safe product catalog，以 canonical Model/Tier 为产品选择单位。

### 2. Evidence

- STATIC CONFIRMED — current Models 从 `ChannelService::list` 建 model map。
- STATIC CONFIRMED — current view 包含 active providers/routing groups，属于 operator supply view。
- UNKNOWN — approved Product Catalog/Manifest product projection。
- UNKNOWN — authoritative Tier/Pricing/Buyer availability contracts。

### 3. Entry / Starting Point

`functional_pages/catalog.rs::Models`（UI pattern/evidence only）、product catalog backend、UI-003。

### 4. Reuse Targets / Do Not Recreate

Reuse：model identity、search/filter/table/card patterns、serving facts through Buyer-safe projection。  
Do Not Recreate：Channel-scraped product catalog、GPU marketplace、client pricing、Workbench mock models。

### 5. Scope

Allowed：Marketplace、search/filter/advanced、Use Model navigation。  
Avoid：Product Catalog backend architecture、Provider/Route management、model runtime/download。

### 6. Behavior Contract

**Inputs**：authoritative catalog/pricing/availability/Tier/capability。  
**Outputs**：Buyer model product list/detail + Playground navigation。  
**Ownership**：Product/Pricing/Serving own facts；page filters/presents。  
**Side Effects**：navigation only。

### 7. Failure / Forbidden Fallbacks

Missing price/availability → Unknown；partial failure 保留已确认产品；无 authoritative catalog 则阻塞。禁止暴露 raw Channel/GPU/Supplier。

### 8. Impact / Invariants

Read-only product discovery。Buyer chooses Model/Tier, not infrastructure。Buyer/Admin 必须共享 canonical model identity。

### 9. Dependencies

UI-003 + Product Catalog/Manifest + Tier/Pricing/Availability。

### 10. Stop Conditions

STOP IF final catalog 只能从 Channel rows 推导，必须暴露 Supplier/GPU/internal topology，或需要改变 Router behavior。

---

## 第三层：验收层（Definition of Done）

- [ ] Product catalog authoritative。
- [ ] Price/Availability/Tier 可追溯。
- [ ] Default 不出现 GPU/Supplier/IDC/internal Route。
- [ ] Use Model 进入真实 Playground。
- [ ] Search/Filter/Empty/Partial Failure 验证。
- [ ] canonical model identity 与 Admin/Playground 一致。
- [ ] branch + PR。
