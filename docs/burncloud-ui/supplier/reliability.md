---
title: "Supplier Reliability"
slug: /burncloud-ui/supplier/reliability/
---

# Supplier Reliability

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Reliability 让 Supplier 知道资源稳定性现在处于什么等级、为什么、哪些问题需要修复。默认展示 `Excellent / Good / Needs Attention / At Risk` 等可理解等级，而不是把复杂内部评分当唯一真相。

### Primary Question
> **BurnCloud 如何评价我的资源稳定性？我需要修复什么？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Reliability Level | 完整内部风控模型 |
| Availability Trend | 其它 Supplier Score |
| Unexpected Offline | 可被游戏化的隐藏阈值 |
| Actionable Reasons | Traffic Weight 算法细节 |

### Reviewer Focus
1. Supplier 是否能理解“为什么降级”？
2. 自动恢复成功是否只记录，而不是持续告警？
3. 需要 Supplier 行动的问题是否有明确下一步？

---

## 第二层：机器执行层
- Reliability ← Reliability service
- Availability / Offline ← Node telemetry and lifecycle events
- Performance / Network stability ← measured health evidence
- Benchmark history ← authoritative benchmark records

复杂 score 可以作为 Advanced 诊断输入，但默认 UI 应先给等级、原因和可行动建议。

### Notification Rule
只有真正需要 Supplier 处理的机器、网络、稳定性问题才升级通知；Autopilot 已成功恢复的事件进入历史记录。

---

## 第三层：Definition of Done
- [ ] Reliability 等级可解释。
- [ ] 原因可追溯真实 telemetry / events。
- [ ] Supplier 不看到其它 Supplier 内部评分。
- [ ] Recovered 与 Active Problem 清楚区分。
- [ ] 通过分支 + Pull Request 合并。
