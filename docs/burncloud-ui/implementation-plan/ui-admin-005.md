---
title: "UI-ADMIN-005：实现 Admin Models"
slug: /burncloud-ui/implementation-plan/ui-admin-005/
---

# UI-ADMIN-005：实现 Admin Models

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003、UI-007、UI-008 + Product Catalog / Manifest / Pricing / Availability contracts**

> 产品合同：[/burncloud-ui/admin/models/](/burncloud-ui/admin/models/)  
> Canonical production route：`/console/admin/models`

### TL;DR
Admin Models 管理平台“卖什么模型/产品”，不是单纯列 Channel 能跑什么。Buyer Marketplace 与 Admin Models 必须共享 canonical model identity，但权限和展示完全不同。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| product catalog/admin metadata | 不把 Channel rows 直接当 product |
| model/tier/pricing/availability | 不把 legacy `/models` 改 Buyer Marketplace |
| manifest/capability evidence | 不在 UI 管 Runtime process |
| gated product changes if backend exists | 不前端 pricing DB |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/admin/models` 的 canonical product model administration/read surface。

### 2. Evidence
- STATIC CONFIRMED — current `/models` 是 operator Channel model availability view，可作为 supply evidence。
- UNKNOWN — approved Product Catalog/Manifest projection and product mutation APIs。

### 3. Entry / Starting Point
current Models evidence、future Product Catalog/Manifest/Pricing services、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：canonical model identity、Manifest、Channel availability evidence、pricing service。  
Do Not Recreate：client product DB、frontend pricing engine、runtime manager。

### 5. Scope
Allowed：Admin model catalog/detail/status and separately authorized mutations。  
Avoid：Provider routing management、runtime process control、Buyer marketplace behavior。

### 6. Behavior Contract
**Inputs**：Admin identity + product/manifest/pricing/availability facts + explicit authorized edit + locale。  
**Outputs**：Admin product catalog/config/result。  
**Ownership**：Product/Manifest/Pricing services own facts/actions。  
**Side Effects**：only approved product mutations。

### 7. Failure / Forbidden Fallbacks
No product catalog → BLOCKED, not Channel-derived truth. Legacy `/models` maps toward this Admin semantic, never role-dynamic Marketplace。

### 8. Impact / Invariants
Potential product/pricing mutation high-risk；route `/console/admin/models`；Model IDs stable/untranslated。

### 9. Dependencies
UI-003、007、008 + Product Catalog/Manifest/Pricing contracts。

### 10. Stop Conditions
STOP IF product identity must be reconstructed from Channel rows、pricing is client-owned、or runtime/routing authority required。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] legacy `/models` semantic migration points Admin-side, not Buyer Marketplace。
- [ ] Buyer/Admin share canonical Model IDs。
- [ ] product/pricing/availability authoritative。
- [ ] Model IDs/API names not translated；labels/copy localized。
- [ ] branch + PR。
