---
title: "Buyer Playground"
slug: /burncloud-ui/buyer/playground/
---

# Buyer Playground

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Playground 不是 Demo，而是第一次真实 API 使用入口。Buyer 选择 Model / Tier、输入请求、点击 `Send`，看到真实响应、Latency、Usage，并能复制对应 API 示例。

### Primary Question
> **这个模型现在能不能满足我的需求？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Model / Tier 选择 | 手工选择 Provider |
| 调用真实 `/v1` | 手工选择 GPU |
| Response / Usage / Latency | 手工部署模型 |
| 生成 API 示例 | 绕过 Auth / Billing 的假 Demo |

### Reviewer Focus
1. Playground 是否与正式 `/v1` 使用同一语义？
2. `MODEL_PREPARING`、Provider serving、Local Ready 是否能正确解释？
3. UI 是否完全没有 Download / Start llama.cpp 等基础设施按钮？

---

## 第二层：机器执行层

### Production Mapping
- Model list ← Approved Model catalog / Router capability
- Tier ← Product tier contract，默认 `Standard`
- Response ← Existing BurnCloud `/v1` data plane
- Tokens / Cost ← Usage metering + Billing
- Request ID ← Server tracing / Logs

### Node Autopilot Contract
```text
Local READY → 正常返回
Local not READY + Provider available → 当前请求走 Provider，后台准备 Local
No serving candidate + local preparation possible → MODEL_PREPARING
Hardware/Disk/Runtime blocked → 展示明确诊断
```

Playground 不直接触发下载实现；它只发送真实请求，后台 Demand Reconciliation 负责模型准备。

### State Contract
- Loading：真实请求 loading；长时本地准备显示阶段，不无限 spinner。
- Partial Failure：响应成功但 Usage 子数据失败时保留响应。
- Error：区分 Auth / Billing / Provider / MODEL_PREPARING / Hardware。
- Recovered：重试成功后保留上一错误的上下文与 Request ID。

---

## 第三层：Definition of Done
- [ ] Playground 与生产 `/v1` 同路径/同语义。
- [ ] 不存在假响应。
- [ ] Provider → Local 自动切换不需要 Buyer 操作。
- [ ] Request ID 可跳转对应 Logs。
- [ ] Error / MODEL_PREPARING / Recovered 已验证。
- [ ] 通过分支 + Pull Request 合并。
