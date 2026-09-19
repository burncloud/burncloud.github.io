---
title: "Admin Suppliers"
slug: /burncloud-ui/admin/suppliers/
---

# Admin Suppliers

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Suppliers 管理供应商身份、等级、Reliability、资源和商业状态。Admin 应先看谁值得信任、谁需要关注，再按需下钻 Verification、Resources 和 Commercial Details。

### Primary Question
> **哪些 Supplier 值得信任、贡献如何、需要关注谁？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Supplier Profile | Buyer Credential |
| Level / Verification | 默认 Prompt 内容 |
| Reliability / Resources | 无审核提升 Trust |
| Commercial Status | 无权限商业秘密 |

### Reviewer Focus
1. Supplier Level 是否由真实 Verification/History 支撑？
2. Reliability 是否可解释？
3. Level、Revenue Share、Contribution 是否没有混成一个概念？

---

## 第二层：机器执行层
- Supplier profile ← Supplier registry
- Verification ← identity/resource/network evidence
- Reliability ← Reliability service
- Resource summary ← Node inventory
- Commercial terms ← authorized commercial configuration

身份、等级、合同和 Revenue Share 修改进入 Human / Business Gate；普通 health 与资源状态自动更新。

---

## 第三层：Definition of Done
- [ ] Supplier Level 有证据来源。
- [ ] Reliability / Contribution / Revenue Share 分离。
- [ ] 敏感商业字段按权限展示。
- [ ] 重要变更有 audit。
- [ ] 通过分支 + Pull Request 合并。
