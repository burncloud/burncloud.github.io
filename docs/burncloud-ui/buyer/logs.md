---
title: "Buyer Logs"
slug: /burncloud-ui/buyer/logs/
---

# Buyer Logs

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Logs 是 Buyer 的请求诊断页：展示 Timestamp、Request ID、Model/Tier、Status、Latency、Tokens 和 Cost。默认保护 Prompt、API Key Secret、Supplier credential 和内部进程信息。

### Primary Question
> **某一次 API 请求发生了什么？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Request ID / Time | API Key Secret |
| Model / Tier / Status | Supplier credential |
| Latency / Tokens / Cost | 默认完整 Prompt |
| Safe error summary | PID / internal port |

### Reviewer Focus
1. 是否严格租户隔离？
2. Request ID 能否定位真实后端记录？
3. Provider → Local 自动切换是否只以安全摘要呈现？

---

## 第二层：机器执行层

### Production Mapping
- Request list / status ← Request observability / logs
- Usage ← Usage metering
- Cost ← Billing
- Request ID ← Server tracing

### Privacy Contract
默认 redacted 敏感请求内容；是否允许查看更详细 request/response 必须由后端权限和数据策略决定。

### State Contract
- Empty：解释尚无请求或筛选无结果。
- Partial Failure：详情失败不能清空请求列表。
- Error：日志服务失败不应暗示 Data Plane 一定失败。
- Recovered：保留筛选和定位上下文。

---

## 第三层：Definition of Done
- [ ] Tenant isolation 已验证。
- [ ] Secret / Supplier credential 不泄露。
- [ ] Request ID 可追溯。
- [ ] Logs 与 Usage/Billing 语义一致。
- [ ] Empty / Partial Failure / Error / Recovered 已验证。
- [ ] 通过分支 + Pull Request 合并。
