---
title: "Admin Models"
slug: /burncloud-ui/admin/models/
---

# Admin Models

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Admin Models 管理 BurnCloud 的产品模型目录：Model、Version/Manifest、Tier、Pricing/Availability 和 Capacity Readiness。它不成为逐 Runtime / PID 操作页。

### Primary Question
> **BurnCloud 当前提供哪些模型，它们的产品与容量状态如何？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Model Catalog | 直接 PID 操作 |
| Manifest / Version | 手工 llama.cpp 参数 |
| Tier / Pricing Status | Buyer Secret |
| Capacity / Readiness | 未验证 Artifact 直接上线 |

### Reviewer Focus
1. Product Model 与底层 Artifact/Variant 是否分层？
2. Manifest/Version 是否可追溯？
3. 模型部署是否仍由 Autopilot，而不是 Admin 手工 start？

---

## 第二层：机器执行层
- Catalog ← approved Model catalog
- Manifest / Version ← Model Manifest source
- Tier / Pricing ← product config / pricing
- Capacity / Readiness ← serving capacity + Node/Provider availability
- Benchmark ← approved benchmark records

### Product Gate
新增/下架模型、改变 Tier 或 Pricing 属于产品/商业决策；本地模型下载、Variant 选择、Runtime preparation 属于 Node Autopilot，不在此页手工执行。

---

## 第三层：Definition of Done
- [ ] Catalog 与 Buyer Marketplace 使用同一 canonical model identity。
- [ ] Manifest / Version 状态可追溯。
- [ ] 未验证 Artifact 不显示 Ready。
- [ ] 无 PID / Runtime CLI 控制。
- [ ] 通过分支 + Pull Request 合并。
