---
title: "Admin"
slug: /burncloud-ui/admin/
---

# Admin

Admin 的 Mental Model：

```text
Supply → Capacity → Demand → Economics
```

Admin 是业务 + 基础设施 Command Center 的使用者，而不是逐 GPU 运维员。

## 页面

- Overview
- Supply
- Capacity
- Demand
- Models
- Operations
- Billing
- Revenue
- Settlements
- Suppliers
- Customers
- Settings

## Economics 边界

```text
Billing
= 客户账务 / 充值 / Invoice / 欠费 / Billing Policy

Revenue
= Revenue / Verified Cost / Gross Margin

Settlements
= Supplier Payable / Payout
```

三者是独立业务域，不能因为都涉及金额就合成一个页面。

## 最高边界

Admin 默认先看系统结论、风险和经济影响；只有诊断时才下钻 Node / GPU / Runtime / Provider。高风险账务、结算、安全和 Autopilot Policy 操作必须走明确授权、审计和 Verify。
