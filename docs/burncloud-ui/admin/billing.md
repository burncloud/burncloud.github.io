---
title: "Admin Billing"
slug: /burncloud-ui/admin/billing/
---

# Admin Billing

## 页面使命

Admin Billing 回答：

> **平台上的客户现在是如何被计费、充值、开票和处理欠费/账务异常的？**

它是 Customer Billing Operations 页面，不是 Revenue 页面，也不是 Supplier Settlement 页面。

```text
Admin Billing
≠ Admin Revenue
≠ Admin Settlements
```

## Canonical Production Route

```text
/console/admin/billing
```

这是受保护的 Admin Console 页面。URL 本身不授予 Admin 权限；Backend Authorization 仍是最终权限真相。

## 首屏建议

优先展示：

- Customer Billing Accounts
- Recharge / Top-up Orders
- Outstanding / Delinquent Accounts
- Billing Anomalies
- Invoice / Transaction Status
- Billing Policy / Limits（仅当 backend 有真实 owner）

页面默认回答平台客户账务状态，不展示 Supplier payout，也不把 Buyer Billing 页面复制给 Admin。

## Admin Billing 与 Buyer Billing

Buyer Billing：

```text
/console/buyer/billing
```

回答“我的余额、充值、交易、Invoice、支付方式和 Spend Limit”。

Admin Billing：

```text
/console/admin/billing
```

回答“整个平台 Customer Billing 发生了什么、哪些订单/账户异常、哪些操作需要管理员处理”。

两者可以复用相同的 authoritative Billing/Payment/Ledger 服务，但权限、数据范围和用户任务不同。

## Admin Billing 与 Revenue

Admin Revenue 负责：

```text
Revenue
Verified Cost
Gross Margin
Economics drilldown
```

Admin Billing 不在前端计算 Revenue 或 Margin。

## Admin Billing 与 Settlements

Admin Settlements 负责：

```text
Supplier Payable
Settlement Batch
Processing / Paid / Failed
Payout verification
```

Admin Billing 不执行 Supplier payout。

## 行为合同

**Inputs**：Admin identity、authoritative customer billing account、recharge order、transaction、invoice、delinquency/anomaly、billing policy/audit facts。  
**Outputs**：平台客户账务状态、筛选/下钻、明确授权后的账务操作结果。  
**Ownership**：Billing / User / Payment / Policy services owns truth；UI 只组合和发起明确人类意图。  
**Side Effects**：高风险账务调整只能通过 backend-authorized、audited、verified action。

## Failure / Unknown

- Unknown 不显示成 `0`、`Paid` 或 `Healthy`。
- API 提交成功不等于账本已完成变更；必须 Verify authoritative result。
- 部分财务服务失败时保留其它已确认事实。
- 不允许前端自己推导欠费、Revenue、Margin 或 payable。

## 权限与敏感信息

- Admin WorkspaceGate 只是 UX gate。
- Backend API 必须再次验证 Admin capability / tenant/customer scope。
- 不展示 API secret、支付凭据、Supplier secret terms 或不必要的 PII。
- 高风险 balance correction、refund/adjustment、policy change 必须审计。

## 页面状态

至少覆盖：

```text
Loading
Ready
Empty
Partial Failure
Error
Recovered
Unauthorized / Forbidden
```

## Done When

- Admin Billing 与 Buyer Billing / Revenue / Settlements 的职责清晰分离。
- 页面所有金额和状态可追溯到 authoritative backend。
- 高风险账务操作具有 reason / actor / scope / audit / verify。
- Unknown / Partial Failure 不被伪装成成功。
- `/console/admin/billing` 受 AuthGate + WorkspaceGate + Backend Authorization 保护。
- i18n 和 currency/date/number formatting 遵循 Production i18n contract。
