---
title: "NODE-503：localhost:3000 本地推理完整 E2E"
slug: /burncloud-node/implementation-plan/node-503/
---

# NODE-503：localhost:3000 本地推理完整 E2E

**状态：PLANNED**  
**类别：Local Channel Integration**  
**依赖：NODE-003, NODE-502**

## 目标

证明 BurnCloud Node v0.1 的完整本地执行主链，而不是只证明各组件单独工作。

## E2E 链

```text
logical model
→ HardwareProfile
→ Model Resolver
→ Model Preparation
→ llama.cpp Runtime
→ Process READY
→ Local Channel / Ability
→ Existing ModelRouter
→ localhost:3000/v1/...
→ response
```

## 范围

**Allowed**：E2E fixture、最小 GGUF 测试模型/可替代测试资源、必要集成修复。  
**Avoid**：借 E2E Issue 顺手重构无关 Provider/Auth/Billing。

## Invariants

- `INV-RUNTIME-002`
- `INV-ROUTER-001`
- `INV-AUTH-002`
- `INV-BILLING-001`
- `INV-BILLING-002`

## 验证

- 客户端不提供 GGUF 绝对路径、PID、内部端口。
- 未 READY 模型不接流量。
- 本地请求得到正常响应。
- 现有 Provider routing / auth / billing 回归通过。

## Done When

上述链路稳定可重复通过，才把 BurnCloud Node v0.1 的本地执行闭环视为完成。