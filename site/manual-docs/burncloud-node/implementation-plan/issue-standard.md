---
title: "Issue 标准"
slug: /burncloud-node/implementation-plan/issue-standard/
---

# BurnCloud Node Issue 标准

本页面是 BurnCloud Node 工程 Issue 的 **唯一规范源（Canonical Standard）**。

主代码仓库 `burncloud/burncloud` 可以通过 Issue Form、Task Contract、Agent Rules、CI 等方式执行本规范，但不得维护另一套语义不同的 Issue 标准。

核心原则：

> **PLANNED 不等于可以编码。Codex 只能实现通过 READY Gate 的 Engineering Issue。**

## 1. 三层职责

```text
Implementation Plan
未来准备做什么（PLANNED）
        ↓
Evidence Audit
        ↓
READY Engineering Issue
批准实现什么、边界是什么、失败时怎么办
        ↓
Task Contract
基于当前 main，核实真实入口、执行路径和验证方式
        ↓
Codex / Coding Agent
        ↓
Candidate Patch
        ↓
Pull Request
        ↓
Review + CI + Verification
        ↓
main
```

### Implementation Plan

实施计划保存长期目标、类别、依赖和 `PLANNED` 能力。

实施计划页面不是当前代码事实，也不直接授权 Codex 开始修改代码。

### Engineering Issue

Engineering Issue 是实现授权合同。它必须定义目标、边界、复用关系、行为合同、失败语义、验证目标和停止条件。

只有满足 READY Gate 的 Issue 才允许进入实现。

### Task Contract

Codex 在真正修改代码前，必须基于当前 `main` 再做一次源码调查。

Task Contract 可以根据当前证据缩小实现范围，但不能获得比父 Issue 更大的架构权限。

## 2. 核心原则

每个 Engineering Issue 必须遵守：

1. **Single Outcome** — 一个 Issue 只交付一个主要可观察结果。
2. **Evidence First** — 当前事实必须来自当前源码、测试、运行证据或已接受规范。
3. **Known Entry** — 必须给出真实入口或调查起点。
4. **Reuse Before Create** — 先明确复用现有组件，再允许新增抽象。
5. **Bounded Scope** — 明确 Allowed / Avoid 权限边界。
6. **Explicit Contract** — 跨组件能力必须定义输入、输出、Ownership 和 Side Effects。
7. **Explicit Failure** — 必须定义失败行为和禁止的 silent fallback。
8. **Invariant Aware** — 必须识别相关 Invariants / Architecture。
9. **Stop Instead of Widen** — 需要越权时停止，不允许通过扩大 Diff 把任务“修通”。
10. **Verifiable Done** — Done When 必须可以独立验证。
11. **No Hidden Architecture Change** — 架构和 invariant 变化不能隐藏在普通 Feature / Bug 中。
12. **PR Only** — 所有实现必须通过 Pull Request 进入 `main`。

## 3. Engineering Issue 必填结构

### 3.1 Goal

只描述一个主要可观察结果。

不要写“优化一下”“完善功能”“顺便重构”等无法验收的目标。

### 3.2 Current Evidence

必须引用当前证据，并使用统一分类：

- `STATIC CONFIRMED`
- `DYNAMIC`
- `INFERRED`
- `UNKNOWN`
- `RUNTIME VERIFIED`

`INFERRED` 和 `UNKNOWN` 不能被写成已经锁定的架构事实。

### 3.3 Entry / Starting Point

给 Codex 一个真实调查起点，例如：

```text
CLI: burncloud node
Route: POST /v1/chat/completions
Source: src/main.rs :: main
Source: crates/server/src/lib.rs :: start_server
```

这里不要求提前写完整调用链，只要求防止 Agent 无边界地从全仓库开始猜。

### 3.4 Reuse Targets / Do Not Recreate

明确应该优先复用的现有能力：

```text
Reuse:
- existing burncloud-server startup
- existing ModelRouter
- existing DownloadManager

Do not recreate:
- second HTTP server
- second router
- second downloader
```

如果现有组件不能承担职责，必须先报告证据，不得因为实现方便直接创建第二套系统。

### 3.5 Expected Behavior

说明完成后系统应该表现出什么行为。

### 3.6 Behavior Contract

跨组件能力至少定义：

```text
Inputs
Outputs
Ownership
Side Effects
```

这里锁的是语义，不提前规定具体 Rust struct、函数名或文件位置，除非这些名称已经是正式合同。

### 3.7 Failure Behavior

必须明确失败时怎么失败，以及禁止什么 fallback。

例如：

```text
No compatible variant:
- return explicit structured failure

Forbidden fallback:
- do not choose an arbitrary artifact
- do not silently route to Provider
- do not trigger download unless this Issue owns preparation
```

### 3.8 Scope

必须同时写：

```text
Allowed
Avoid
```

`Allowed` 是预期权限边界，不代表可以任意修改其中全部代码。

如果实现必须跨越 `Avoid`，必须触发 Stop Condition，而不是静默扩大 Diff。

### 3.9 Impact

至少判断：

- persistence
- external calls
- billing / usage / quota
- auth / authorization
- routing / provider
- concurrency / transactions
- public API / CLI
- process / runtime lifecycle

没有影响时明确写 `none`。

### 3.10 Invariants / Architecture

列出相关 `INV-*`。

如果需要改变 invariant 或架构边界，必须显式标记：

```text
ARCHITECTURE / INVARIANT CHANGE REQUIRED
```

这种变化必须经过独立架构决策，不能由普通功能 Issue 自行批准。

### 3.11 Dependencies / Blockers

列出前置 Issue、架构决策、外部环境或测试资产。

硬依赖进入 READY 前必须已经 DONE，或者明确获得豁免。

Codex 不允许一边实现当前 Issue，一边顺手实现前置 Issue。

### 3.12 Stop Conditions

这是 Codex 的硬边界。

至少考虑：

```text
STOP IF:
- current source disproves a material Issue assumption
- implementation requires changing an Avoid domain
- an undeclared architecture / invariant change is required
- implementation requires a duplicate subsystem or duplicate source of truth
- a required dependency is not available
- required verification cannot be meaningfully performed
```

触发时必须：

```text
Do not widen scope.
Do not repair unrelated modules.
Do not rewrite the requirement to fit the patch.
Report the conflict and evidence.
```

### 3.13 Verification Targets

至少定义：

```text
Targeted
Regression
Runtime / E2E（适用时）
Protected Behavior
```

不能只写“tests pass”。

具体命令如果在规划阶段无法安全确定，可以在 Task Contract 阶段根据当前仓库补齐。

### 3.14 Done When

必须是独立可观察、可验证的验收条件，不是实现步骤。

## 4. Issue 大小标准

一个 Issue 应尽量满足：

```text
one primary capability
one primary owner/domain
one reviewable behavior change
one independently verifiable completion point
```

出现以下情况应拆分：

- 同时新增多个互不依赖能力；
- 同时跨多个主要责任域；
- 一个 Issue 有多个互不依赖的主要 Done When；
- 完成一半已经形成独立价值；
- 标题必须使用“以及 / and”才能表达两个主要目标；
- Agent 必须获得第二个领域的架构权限才能完成第一个能力。

不要按文件或函数机械拆分，拆分单位是行为与责任边界。

## 5. 状态语义

```text
PLANNED      已进入实施计划，但没有实现授权
READY        已通过 Evidence Audit 和 READY Gate，可交给 Codex
IN PROGRESS  已有执行分支 / Candidate Patch / PR
BLOCKED      被依赖、证据缺口或架构决策阻塞
DONE         对应 PR 已合并且要求的验证完成
SUPERSEDED   被新的 Issue / 决策替代
```

## 6. READY Gate

Issue 只有同时满足以下条件才能成为 `READY`：

```text
[ ] Single Outcome 明确
[ ] 硬依赖已 DONE 或明确豁免
[ ] Current Evidence 已按当前 main 核实
[ ] Entry / Starting Point 已确定
[ ] Reuse Targets 已确定
[ ] Allowed / Avoid 已确定
[ ] Behavior Contract 已确定（适用时）
[ ] Failure Behavior 已确定
[ ] Impact 已完整判断
[ ] Relevant Invariants 已确定
[ ] Verification Targets 已确定
[ ] Done When 可独立验证
[ ] Stop Conditions 已确定
[ ] 未隐藏架构 / invariant 修改
```

任何一项不满足，保持 `PLANNED` 或 `BLOCKED`，不能交给 Codex 猜。

## 7. Codex 执行规则

Codex 拿到 READY Issue 后，第一步不是写代码，而是建立 Task Contract 并重新核实：

1. Issue 的 Current Evidence 在当前 `main` 是否仍成立；
2. Entry 是否对应真实入口；
3. Reuse Targets 是否仍存在并承担对应职责；
4. 最小真实执行路径是什么；
5. 前置依赖是否真的完成；
6. Scope 是否足以完成目标；
7. 是否已经触发 Stop Condition；
8. Verification Targets 对应的真实测试、命令和运行路径在哪里。

如果发现冲突，正确结果是：

```text
SCOPE / ARCHITECTURE CONFLICT DETECTED
No out-of-scope code changed.
Evidence: ...
Conflict: ...
Decision required: ...
```

而不是自行改写架构目标。

## 8. Pull Request 规则

所有实现必须走：

```text
READY Issue
  ↓
feature/fix branch
  ↓
Task Contract
  ↓
Candidate Patch
  ↓
Pull Request
  ↓
Review + CI + Verification
  ↓
main
```

禁止直接把实现提交到 `main` 再补 Issue 或补 PR。

PR 正文至少需要说明：

- 实际改变的行为；
- 实际 Scope 是否扩大；
- Reuse Targets 是否被复用；
- 是否改变 Architecture / Invariant / API；
- Failure Behavior 是否与 Issue 一致；
- 执行过哪些验证；
- 哪些验证无法执行；
- 是否触发过 Stop Condition。

## 9. BurnCloud Node 特殊边界

BurnCloud Node 的 Engineering Issue 还必须遵守：

1. 优先复用现有 BurnCloud Server、Router、Database、Model Service、Download、Monitor 能力。
2. 不得创建第二套 Gateway、Router、Downloader、Database 或模型系统，除非先通过独立 Architecture Issue 证明必要性。
3. Local Model 必须通过现有 Router 的 Channel / Ability 体系进入数据面，不创建旁路路由。
4. Resolver 只负责选择，不负责下载和进程启动。
5. Model Preparation 负责 Artifact 准备，不负责路由决策。
6. Runtime 定义“如何运行”，Process Manager 管理真实进程生命周期。
7. `Process Spawned != Model READY`；只有 readiness / health 成功后才能接入流量。
8. Implementation Plan 子页面默认是 `PLANNED`，不能直接作为 Codex 实现授权。

## 10. Source of Truth

本页面是 Issue 语义标准的 Canonical Source of Truth。

`burncloud/burncloud` 中的：

- `.github/ISSUE_TEMPLATE/engineering_task.yml`
- `docs/agent/TASK_CONTRACT.md`
- Agent / Harness rules
- CI gates

属于本标准的**执行实现**，它们可以强化约束，但不应另行定义一套冲突的 Issue 语义。
