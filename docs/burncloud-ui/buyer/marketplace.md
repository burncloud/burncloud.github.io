---
title: "Buyer Marketplace"
slug: /burncloud-ui/buyer/marketplace/
---

# Buyer Marketplace

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Marketplace 是**模型商店**，不是 GPU Marketplace。Buyer 默认只看到 Model、Price、Availability、Tier、Context 和关键能力；底层 Supplier、GPU、IDC 和内部 Routing 默认隐藏。

### Primary Question
> **BurnCloud 有哪些模型可以用？哪个适合我？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Model name / description | GPU 数量/型号 |
| Input / Output price | Supplier 商业身份 |
| Availability / Tier | IDC / Worker topology |
| Context / capability | Internal Route / Channel |

### Reviewer Focus
1. 默认卡片是否像模型商品，而不是云基础设施卡片？
2. Price / Availability 是否来自真实产品与 Serving 数据？
3. Advanced 是否只在需要时展示性能细节？

---

## 第二层：机器执行层

### Production Mapping
- Catalog ← approved Model catalog / Manifest product view
- Pricing ← Billing / pricing source
- Availability ← serving capacity / observability
- Tiers ← Product tier config
- Benchmark / version ← approved benchmark and model metadata

### Default vs Advanced
Default 允许：Model、short description、price、availability、tiers、context、primary CTA。

Advanced 才允许：real-time latency、historical availability、current load、version、benchmark、region、compatibility notes。

即使 Advanced，也不默认暴露 Supplier 商业身份、内部凭证或 Deployment topology。

### Autopilot
模型是否由 Local、Provider 或未来 Network serving，不成为 Buyer 手工选择项。Buyer 只声明 Model/Tier，BurnCloud 管理执行位置。

---

## 第三层：Definition of Done
- [ ] Workbench `WORKBENCH_MODELS` 已替换为真实 Catalog。
- [ ] Price / Availability 可追溯真实来源。
- [ ] Default 卡片不出现 GPU / Supplier / IDC。
- [ ] Use Model 可进入真实 Playground。
- [ ] Search / Filter / Empty / Partial Failure 已验证。
- [ ] 通过分支 + Pull Request 合并。
