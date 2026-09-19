---
title: "Supplier Deployments"
slug: /burncloud-ui/supplier/deployments/
---

# Supplier Deployments

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Deployments 是**只读透明页**：告诉 Supplier BurnCloud 当前在其资源上运行什么、为什么、处于什么阶段。它不是模型部署控制台。

### Primary Question
> **BurnCloud 当前在我的资源上运行什么？状态如何？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Model / State | Deploy Model |
| Resource summary | Choose Model |
| Started / Uptime | Change Runtime |
| Autopilot reason | Traffic Control |

### Reviewer Focus
1. 是否所有 deployment action 都保持只读？
2. Preparing / Ready / Draining / Failed 是否有可解释阶段？
3. Supplier 是否能从异常跳到 Resource / Reliability，而不是自己“修部署”？

---

## 第二层：机器执行层
- Deployment state ← managed Runtime / Process lifecycle
- Readiness / Health ← Node Process Manager
- Reason ← Scheduler / Demand Reconciliation explanation
- Resource allocation ← canonical Node resource state

### Autopilot Contract
低风险部署、启动、停止、切换和恢复由 BurnCloud 自动执行并报告。Supplier 不为每次模型动作做 Approve。

### Hidden
PID、internal port、raw Runtime CLI、Router weight 默认不展示；诊断权限即使存在也不意味着获得写权限。

---

## 第三层：Definition of Done
- [ ] Deployments 只读。
- [ ] 状态来自真实 Runtime / Process 状态机。
- [ ] 自动动作有 Reason / Result。
- [ ] 无 Deploy / Start / Choose Model / Route 控制。
- [ ] 通过分支 + Pull Request 合并。
