---
title: "Admin Operations"
slug: /burncloud-ui/admin/operations/
---

# Admin Operations

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Operations 是 BurnCloud Autopilot 的观察与例外处理中心：展示 Needs Attention、自动动作、Proposal、执行结果和 Verify 证据。正常低风险动作自动完成；只有高风险决策才要求人。

### Primary Question
> **BurnCloud Autopilot 最近做了什么？哪些事情需要人决定？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Autopilot Actions | 模糊的 Allow AI |
| Needs Attention | 每个自动动作确认框 |
| Proposals | 无 Verify 的 Success |
| Verification Result | 原始 PID 信息墙 |

### Reviewer Focus
1. 自动动作是否遵循 Observe → Decide → Act → Verify → Report？
2. Proposal 是否明确原因、成本、收益、风险和影响范围？
3. 已自动恢复的事情是否避免持续制造红色告警？

---

## 第二层：机器执行层
- Events ← Operations / Autopilot event stream
- Proposal ← decision/proposal service
- Expected / Actual impact ← action + verification evidence
- Actor / Time / Input / Result ← audit log

### Human by Exception
进入 Human Gate 的典型动作：大额外租、支付、合同/分成、安全策略、危险数据操作、不可逆基础设施变化。低风险模型准备、恢复、普通容量调整不要求逐次确认。

### Success Rule
“API 返回 200”不等于操作完成。必须有 Verify 阶段证明目标结果已发生。

---

## 第三层：Definition of Done
- [ ] 自动动作有 Reason / Action / Verify / Result。
- [ ] Proposal 对象明确，可 Approve/Reject。
- [ ] 高风险操作 audit 完整。
- [ ] Recovered 事件与 Active Incident 分离。
- [ ] 页面不退化成底层进程控制台。
- [ ] 通过分支 + Pull Request 合并。
