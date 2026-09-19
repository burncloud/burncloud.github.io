---
title: "Admin Customers"
slug: /burncloud-ui/admin/customers/
---

# Admin Customers

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Customers 让 Admin 理解 Buyer Account、Usage、Balance、Risk、Limits 和 Recent Activity，并处理明确账户问题。默认不暴露完整 API Key Secret 或完整敏感请求内容。

### Primary Question
> **哪些客户正在使用平台？账户、消费和风险如何？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Customer Account | 完整 API Key Secret |
| Usage / Spend | 默认完整 Prompt |
| Balance / Status | Supplier 私有数据 |
| Risk / Limits | 无权限财务信息 |

### Reviewer Focus
1. Customer 数据是否按权限隔离？
2. Usage / Balance / Risk 是否来自各自 authoritative service？
3. Freeze / Limit / financial action 是否清楚展示影响？

---

## 第二层：机器执行层
- Customer ← User / Customer service
- Usage ← Usage metering
- Balance / Spend ← Billing
- Risk / Limits ← account policy / risk service
- API Key 只展示 metadata，不展示 secret

账号冻结、额度、资金和危险数据操作需要明确对象、影响与审计；普通查询无需 Gate。

---

## 第三层：Definition of Done
- [ ] Customer tenant/account facts 可追溯。
- [ ] Secret / sensitive prompt 默认隐藏。
- [ ] Risk / Billing / Usage 不由前端自行推断。
- [ ] 高风险账户动作有确认和 audit。
- [ ] 通过分支 + Pull Request 合并。
