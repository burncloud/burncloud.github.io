---
title: "AI Coding Boundaries"
slug: /burncloud-ui/architecture/ai-coding-boundaries/
---

# AI Coding Boundaries

AI/Codex 可以执行实现，但不能拥有“重新定义 BurnCloud UI 架构”的权力。

```text
AI Execution Capability ↑
AI Architecture Authority ↓
```

## Required Task Contract

每个 AI UI 任务必须明确：

```text
Goal
Current Evidence
Canonical Product Contract
Architecture Contract
Allowed Paths
Conditional Paths
Forbidden Paths
Dependencies
Stop Conditions
Machine Verification
Human Acceptance
```

## Mandatory STOP

```text
STOP IF:
- 需要新增第二 Router / Auth / API truth
- 需要跨 Buyer/Supplier/Admin 私有域 import
- 需要修改 L4 Protected Zone 但 Issue 未授权
- 需要页面直接访问 Database/Service/Provider
- 需要用 mock/client inference 补 backend truth
- 需要把 unknown/pending 伪装成 success
- 需要扩大 Issue 到无关页面
```

AI 不得通过“顺手重构”“为了测试方便”“当前目录不好用”自行扩大 ownership scope。