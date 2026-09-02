---
title: "Buyer Overview"
slug: /burncloud-ui/buyer/overview/
---

# Buyer Overview

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Buyer 打开首页后 5 秒内必须知道：**今天花了多少、还有多少余额、API 是否稳定、今天用了多少 Token**。正常状态保持安静；余额不足时 `Top Up` 成为最高优先级 CTA。

### Primary Question
> **我今天用了多少？服务现在稳定吗？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Today Spend / Balance | GPU / Node 监控 |
| API Availability / Tokens Today | Supplier / IDC 信息 |
| Models in Use | Provider / Route 配置 |
| Recent Activity | 全平台经营 Dashboard |

### Reviewer Focus
1. 四个核心指标是否都是 Buyer 自己的数据？
2. 余额不足时是否只有一个最明显的 Top Up CTA？
3. 首屏是否完全不要求 Buyer 理解基础设施？

---

## 第二层：机器执行层

### Primary Information
- `today_spend` ← Billing / Usage aggregation
- `balance` ← Billing ledger
- `api_availability` ← serving observability
- `tokens_today` ← Usage metering
- Models in Use / Recent Activity ← Buyer-scoped usage and request summaries

### State Contract
- Loading：四指标使用 Skeleton，不先显示 `$0`。
- Empty：解释尚无 API 使用，并引导 Marketplace / Playground。
- Partial Failure：成功指标保留；失败指标显示 `Unavailable`，不得伪装成 0。
- Error：说明受影响数据，不暗示 API 一定故障。
- Recovered：明确说明数据已恢复。

### Boundaries
- React `RoleContext` 中的固定余额/消费数字不得进入生产。
- 页面不得直接读取 Provider/Channel 表拼 Buyer 状态。
- Top Up 必须由用户主动发起，Autopilot 不执行资金操作。

---

## 第三层：Definition of Done
- [ ] 四指标均来自真实后端。
- [ ] Buyer tenant isolation 已验证。
- [ ] Loading / Empty / Partial Failure / Error / Recovered 已验证。
- [ ] Buyer 首屏不出现 GPU / Supplier / IDC / Runtime。
- [ ] 视觉使用 `--bc-*` semantic tokens。
- [ ] 通过分支 + Pull Request 合并。
