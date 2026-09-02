---
title: "UI-ADMIN-005：实现 Admin Models"
slug: /burncloud-ui/implementation-plan/ui-admin-005/
---

# UI-ADMIN-005：实现 Admin Models

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003 + Product Catalog / Manifest / Tier / Pricing / Readiness**

> 产品合同：[/burncloud-ui/admin/models/](/burncloud-ui/admin/models/)

### TL;DR

Admin Models 管产品模型目录：Model、Manifest/Version、Tier/Pricing、Capacity/Readiness。它不成为 Runtime/PID/llama.cpp 参数页。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Product Catalog | 不直接 PID 操作 |
| Manifest/Version | 不编辑 Runtime CLI |
| Tier/Pricing Status | 不把 raw Channel 当最终 catalog |
| Capacity/Readiness | 不把 unverified Artifact 标 Ready |

### 审批者关注点（Reviewer Focus）
1. Product Model 与 Artifact/Variant 是否分层？
2. Buyer Marketplace 是否共用 canonical identity？
3. local runtime preparation 是否仍由 Node Autopilot？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立 Admin product-model management/visibility surface，不吸收 Node runtime/process authority。

### 2. Evidence

- STATIC CONFIRMED — current `catalog.rs::Models` 从 Channels 推导 serving availability/redundancy。
- STATIC CONFIRMED — 该能力不是 approved Product Catalog/Manifest/Tier/Pricing source。
- TARGET CONFIRMED — Buyer/Admin 共享 canonical model identity；unverified Artifact != Ready。
- UNKNOWN — authoritative Product Catalog/Manifest/Version/Tier/Pricing contracts。

### 3. Entry / Starting Point

current catalog patterns；Product/Manifest/Pricing service；Capacity/Readiness；approved benchmark records。

### 4. Reuse Targets / Do Not Recreate

Reuse：canonical model identity、provider availability、future Node readiness/manifest records。  
Do Not Recreate：frontend manifest/pricing DB、raw Channel as product truth、PID/runtime CLI controls。

### 5. Scope

Allowed：Admin Models/read-only product metadata + separately authorized Product Gate actions。  
Avoid：Model Resolver/Download/Runtime、Provider/Route management、process controls。

### 6. Behavior Contract

**Inputs**：catalog/manifest/tier/pricing/readiness/benchmark facts。  
**Outputs**：product model list/detail/status。  
**Ownership**：Product domains own catalog decisions；Node/Router own serving readiness；UI presents。  
**Side Effects**：read-only unless explicit Product Gate。

### 7. Failure / Forbidden Fallbacks

Unverified/missing manifest never Ready；missing pricing Unknown；serving availability ≠ product approval。禁止 client manifest/raw runtime controls。

### 8. Impact / Invariants

Product Model ≠ Artifact/Variant/Runtime；Buyer/Admin share canonical identity；unverified ≠ Ready。

### 9. Dependencies

UI-003 + Product Catalog/Manifest/Version + Tier/Pricing + Capacity/Readiness + optional benchmark contract。

### 10. Stop Conditions

STOP IF final product catalog 必须 raw Channel-derived、unverified artifact 会被标 Ready、或需要 PID/runtime control。

---

## 第三层：验收层（Definition of Done）

- [ ] Admin/Buyer share canonical model identity。
- [ ] Manifest/Version trace authoritative source。
- [ ] Tier/Pricing authoritative。
- [ ] Capacity/Readiness truthful。
- [ ] unverified Artifact never Ready。
- [ ] no PID/runtime CLI control。
- [ ] branch + PR。
