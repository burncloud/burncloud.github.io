---
title: "Supplier Settings"
slug: /burncloud-ui/supplier/settings/
---

# Supplier Settings

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Supplier Settings 只放 Supplier 真正拥有的配置：通知、Payout Profile、Maintenance Window 和允许的资源偏好。这里不是 Runtime / Scheduler / Routing 配置中心。

### Primary Question
> **我的 Supplier 账号和资源运营偏好如何配置？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Notifications | Manual Model Deployment |
| Payout Profile | Runtime CLI / GPU Layers |
| Maintenance Window | Route Weights |
| Supplier Preferences | Scheduler Internals |

### Reviewer Focus
1. 设置是否真的由 Supplier 拥有？
2. 高风险金融/身份修改是否有额外验证？
3. 是否完全没有模型部署和 Traffic 控制？

---

## 第二层：机器执行层
- Supplier settings ← authoritative settings backend
- Payout profile ← Settlement / payment profile
- Maintenance windows ← Resource lifecycle policy
- Notifications ← Notification preferences

### Human Gate
Payout、身份、安全相关修改需要适用验证；普通通知偏好可直接保存。Maintenance Window 只是向 Scheduler 声明约束，不赋予 Supplier 手工迁移模型能力。

---

## 第三层：Definition of Done
- [ ] 所有设置有真实 Backend Owner。
- [ ] 保存失败明确指出未生效字段。
- [ ] Payout / identity 变更有正确验证。
- [ ] 无 Runtime / Route / Deployment 控制项。
- [ ] 通过分支 + Pull Request 合并。
