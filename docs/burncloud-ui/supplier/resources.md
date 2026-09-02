---
title: "Supplier Resources"
slug: /burncloud-ui/supplier/resources/
---

# Supplier Resources

## 第一层：人类阅读区

**状态：TARGET / PLANNED**

### TL;DR
Resources 展示 Supplier 自己的 Node / GPU 资源与健康：GPU、VRAM、温度、利用率、当前模型、Uptime。Supplier 可以请求 **Graceful Offline**，但不能控制模型部署、Runtime 参数或 Traffic。

### Primary Question
> **我的哪些机器在线？硬件与健康状态如何？**

| ✅ 做 | ❌ 不做 |
| --- | --- |
| Node / GPU / VRAM | Choose Model |
| Temperature / Utilization | Runtime 参数 |
| Current Model（只读） | Traffic Weight |
| Graceful Offline | Force Route |

### Reviewer Focus
1. 当前模型是否明确标记为 Autopilot Assigned / Read-only？
2. Graceful Offline 是否显示 Drain → Finish → Release → Offline？
3. Force / Unexpected Offline 是否与正常下线清楚区分？

---

## 第二层：机器执行层
- Hardware facts ← canonical HardwareProfile
- Available resources ← ResourceSnapshot
- Health / uptime ← Node and runtime health
- Current model ← managed deployment state
- Graceful Offline ← Resource lifecycle API

### Graceful Offline Contract
```text
Request Offline
→ Draining
→ Stop new work
→ Finish in-flight work
→ Release deployment
→ Offline
```

Supplier 不拥有 `Deploy Model / Start Runtime / Stop Process / Change Route` 权限。

---

## 第三层：Definition of Done
- [ ] `MOCK_SUPPLIER_NODES` 被真实 Node 数据替换。
- [ ] Hardware / Health / Assigned Model 均可追溯。
- [ ] Graceful Offline 全阶段可见。
- [ ] Supplier 无模型部署和 Traffic 控制入口。
- [ ] 通过分支 + Pull Request 合并。
