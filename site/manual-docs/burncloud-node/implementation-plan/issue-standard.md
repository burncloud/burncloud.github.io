---
title: "Issue 标准"
slug: /burncloud-node/implementation-plan/issue-standard/
---

# BurnCloud Node Issue 标准

BurnCloud Node 的实施页面按 **一个 Issue = 一个主要可验证能力** 拆分。

每个 Issue 页面都必须包含：目标、当前事实、期望行为、允许范围、避免范围、影响面、Invariants、依赖、验证计划和完成条件。

## 执行关系

```text
实施计划子页面
   ↓
GitHub Issue
   ↓
Task Contract
   ↓
feature/fix branch
   ↓
Pull Request
   ↓
Review + CI + Verification
   ↓
main
```

Issue 页面是计划，不代表代码已经实现。只有对应 PR 合并并完成验证后，状态才可以从 `PLANNED` 更新为 `DONE`。

## 状态

- `PLANNED`：已规划，尚未开始。
- `READY`：依赖和验收条件已经明确。
- `IN PROGRESS`：已有实现分支或 PR。
- `BLOCKED`：被架构决策或前置 Issue 阻塞。
- `DONE`：PR 已合并且验证完成。
- `SUPERSEDED`：被新的 Issue 或决策替代。

## Node 特殊边界

1. 复用现有 BurnCloud Server、Router、Database、Models、Download、Monitor。
2. 不创建第二套 Gateway、Router、Downloader、Database。
3. 本地模型通过现有 Channel / Ability 进入 Router。
4. Resolver 只选择；Model Preparation 才准备 Artifact。
5. Runtime 生成运行方式；Process Manager 管理进程生命周期。
6. `Process Spawned != Model READY`。
7. 所有实现修改必须通过 Pull Request 进入 `main`。

主代码仓库的规范文件：`docs/agent/ISSUE_STANDARD.md`。