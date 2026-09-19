---
title: "Issue 标准"
slug: /burncloud-node/implementation-plan/issue-standard/
---

# BurnCloud Node Issue 标准

本页面是 BurnCloud Node 工程 Issue 的 **唯一规范源（Canonical Standard）**。

主代码仓库 `burncloud/burncloud` 可以通过 Issue Form、Task Contract、Agent Rules、CI 等方式执行本规范，但不得维护另一套语义不同的 Issue 标准。

核心原则：

> **PLANNED 不等于可以编码。Codex 只能实现通过 READY Gate 的 Engineering Issue。机器验证通过也不等于产品已经被人类验收。**

## 1. 从计划到 DONE 的完整责任链

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
基于 current main 核实真实入口、路径与验证方式
        ↓
Coding Agent / Human Developer
        ↓
Candidate Patch
        ↓
Pull Request
        ↓
Machine Verification
CI / tests / runtime / regression
        ↓
Human Acceptance
真实产品路径人工操作与签收
        ↓
DONE
```

### Implementation Plan

保存长期目标、类别、依赖和 `PLANNED` 能力。它不是当前代码事实，也不直接授权 Agent 开工。

### Engineering Issue

Engineering Issue 是实现授权合同。必须定义目标、边界、复用关系、行为合同、失败语义、机器验证目标、停止条件，以及**人类最终怎么验收**。

### Task Contract

真正修改代码前，必须基于 current `main` 再调查一次。Task Contract 可以缩小范围，但不能获得比父 Issue 更大的架构权限。

### Human Acceptance

Human Acceptance 回答的不是“代码有没有按计划写”，而是：

> **一个不依赖 AI 自我评价的人，如何通过真实操作证明这个产品行为真的成立？**

Canonical Registry：

[Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/)

## 2. 四层 Issue / Plan 结构

每一个 NODE Implementation Plan 页面最终必须呈现四层：

```text
第一层：Human Readable Layer
Why / Scope / Risk / Reviewer Focus

第二层：Machine Executable Specification
Goal / Evidence / Entry / Reuse / Scope /
Behavior / Failure / Impact / Dependencies / Stop

第三层：Definition of Done
Targeted / Regression / Runtime / Invariant verification

第四层：Human Acceptance
Human operator steps / visible result / failure criteria / evidence
```

前三层可以大量借助 AI/CI 执行；第四层不能由 AI 自己宣布 PASS。

## 3. 核心原则

每个 Engineering Issue 必须遵守：

1. **Single Outcome** — 一个 Issue 只交付一个主要可观察结果。
2. **Evidence First** — 当前事实来自 current source / test / runtime / accepted spec。
3. **Known Entry** — 给出真实入口或调查起点。
4. **Reuse Before Create** — 先明确复用，再允许新增抽象。
5. **Bounded Scope** — 明确 Allowed / Avoid。
6. **Explicit Contract** — 跨组件能力定义 Inputs / Outputs / Ownership / Side Effects。
7. **Explicit Failure** — 明确失败和禁止 silent fallback。
8. **Invariant Aware** — 识别相关架构 / INV-*。
9. **Stop Instead of Widen** — 越权时停止，不通过扩大 Diff 把任务“修通”。
10. **Machine Verifiable** — Definition of Done 必须可独立机器/运行验证。
11. **Human Acceptable** — 必须定义人类实际如何验收产品行为。
12. **No Hidden Architecture Change** — 架构变化不能隐藏在普通 Feature/Fix 中。
13. **PR Only** — 所有实现通过 Pull Request 进入 `main`。

## 4. Engineering Issue 必填结构

### 4.1 Goal

只描述一个主要可观察结果。禁止“优化一下”“完善功能”“顺便重构”。

### 4.2 Current Evidence

统一分类：

```text
STATIC CONFIRMED
DYNAMIC
INFERRED
UNKNOWN
RUNTIME VERIFIED
```

`INFERRED` / `UNKNOWN` 不能伪装成锁定事实。

### 4.3 Entry / Starting Point

例如：

```text
CLI: burncloud node
Route: POST /v1/chat/completions
Source: src/main.rs :: main
Source: crates/server/src/lib.rs :: start_server
```

不要求计划阶段提前写完整调用链，但必须防止 Agent 无边界猜测。

### 4.4 Reuse Targets / Do Not Recreate

例如：

```text
Reuse:
- existing burncloud-server
- existing ModelRouter
- existing DownloadManager

Do not recreate:
- second HTTP server
- second router
- second downloader
```

如果现有组件不能承担职责，先报告证据，不得因为方便直接建第二套。

### 4.5 Expected Behavior

描述完成后用户/系统应观察到什么结果。

### 4.6 Behavior Contract

跨组件至少定义：

```text
Inputs
Outputs
Ownership
Side Effects
```

锁语义，不提前强制 Rust struct / 函数名，除非已经是正式合同。

### 4.7 Failure Behavior

必须写失败时如何失败，以及 forbidden fallback。

### 4.8 Scope

同时写：

```text
Allowed
Avoid
```

需要跨越 `Avoid` 时触发 Stop Condition，而不是静默扩大 Diff。

### 4.9 Impact

至少判断：

```text
persistence
external calls
billing / usage / quota
auth / authorization
routing / provider
concurrency / transactions
public API / CLI
process / runtime lifecycle
```

没有影响时明确 `none`。

### 4.10 Invariants / Architecture

列出相关 `INV-*`。需要改变时明确：

```text
ARCHITECTURE / INVARIANT CHANGE REQUIRED
```

普通功能 Issue 无权自行批准这种变化。

### 4.11 Dependencies / Blockers

列出前置 Issue、外部环境、架构决策、测试资产。硬依赖未满足则保持 `PLANNED/BLOCKED`。

### 4.12 Stop Conditions

至少考虑：

```text
STOP IF:
- current source disproves a material assumption
- implementation requires changing an Avoid domain
- undeclared architecture/invariant change is required
- duplicate subsystem/source of truth is required
- dependency is unavailable
- meaningful verification cannot be performed
```

触发后：

```text
Do not widen scope.
Do not repair unrelated modules.
Do not rewrite requirement to fit patch.
Report conflict and evidence.
```

### 4.13 Machine Verification Targets

至少定义：

```text
Targeted
Regression
Runtime / E2E（适用时）
Protected Behavior
```

不能只写 `tests pass`。

### 4.14 Definition of Done

必须是独立可观察、可验证的结果，不是实现步骤。

### 4.15 Human Acceptance

每个 Issue 必须有独立 Human Acceptance，至少包含：

```text
验收者
人工步骤
人类通过标准
人工判定失败
建议证据
```

Human Acceptance 的要求：

1. 使用真实产品入口优先，例如 CLI、HTTP `/v1`、真实 Runtime、真实文件或真实状态。
2. 明确人应该**看到什么**，而不是要求人阅读内部代码相信实现。
3. 至少写一个“必须判失败”的反例。
4. 留下可复查证据：命令输出、请求/响应、trace、日志、截图等。
5. 如果只能用 mock/fixture，必须说明为什么不会改变被验收行为。

禁止以下作为唯一人类验收：

```text
AI says complete
CI green
unit tests green
PR approved by AI reviewer
code looks correct
```

## 5. Issue 大小标准

一个 Issue 尽量满足：

```text
one primary capability
one primary owner/domain
one reviewable behavior change
one independently verifiable completion point
one human-acceptable product outcome
```

出现多个独立能力、多个主要责任域、多个互不依赖 Done When，或需要第二领域架构权限时应拆分。

## 6. 状态语义

```text
PLANNED      进入计划，但无实现授权
READY        Evidence/Scope/Verification/Human Acceptance 已定义，可开工
IN PROGRESS  已有执行分支 / Candidate Patch / PR
BLOCKED      被依赖、证据、环境、架构或验收条件阻塞
DONE         PR 已合并 + Machine Verification 完成 + Human Acceptance PASS
SUPERSEDED   被新的 Issue / 决策替代
```

关键变化：

> **PR merged + CI green 但 Human Acceptance 未执行，不应直接标 DONE。**

## 7. READY Gate

Issue 只有同时满足以下条件才能成为 `READY`：

```text
[ ] Single Outcome 明确
[ ] 硬依赖已 DONE 或明确豁免
[ ] Current Evidence 已按 current main 核实
[ ] Entry / Starting Point 已确定
[ ] Reuse Targets 已确定
[ ] Allowed / Avoid 已确定
[ ] Behavior Contract 已确定（适用时）
[ ] Failure Behavior 已确定
[ ] Impact 已完整判断
[ ] Relevant Invariants 已确定
[ ] Machine Verification Targets 已确定
[ ] Done When 可独立验证
[ ] Human Acceptance 已定义且可执行
[ ] Stop Conditions 已确定
[ ] 未隐藏架构 / invariant 修改
```

Human Acceptance 在 READY 阶段要求“定义清楚怎么验”；不要求开工前就执行。

## 8. DONE Gate

Issue 只有同时满足以下条件才能成为 `DONE`：

```text
[ ] 对应 PR 已合并
[ ] Targeted verification PASS
[ ] Regression verification PASS
[ ] Runtime/E2E verification PASS（适用时）
[ ] Relevant invariants 保持成立
[ ] Human Acceptance 已由明确的人执行
[ ] Human Acceptance = PASS
[ ] 人工证据已记录
[ ] Known gaps 已显式记录
```

如果人工验收环境暂时不可获得，正确状态通常是 `BLOCKED` 或继续 `IN PROGRESS`，而不是让 AI 代签。

## 9. Codex / Coding Agent 执行规则

拿到 READY Issue 后，第一步不是写代码，而是 Task Contract，并重新核实：

1. Current Evidence 是否仍成立；
2. Entry 是否是真实入口；
3. Reuse Targets 是否仍存在并承担对应职责；
4. 最小真实执行路径是什么；
5. 前置依赖是否真正完成；
6. Scope 是否足以完成目标；
7. 是否触发 Stop Condition；
8. Verification Targets 对应的真实命令/测试在哪里；
9. Human Acceptance 需要什么环境和可观察证据。

Agent 可以准备人工验收脚本/步骤，但**不能把自己的执行结果自动写成 Human Acceptance PASS**。

发现冲突时：

```text
SCOPE / ARCHITECTURE CONFLICT DETECTED
No out-of-scope code changed.
Evidence: ...
Conflict: ...
Decision required: ...
```

## 10. Pull Request 规则

所有实现：

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
Machine Verification
  ↓
Human Acceptance
  ↓
main / DONE
```

禁止直接提交 `main` 再补 Issue/PR。

PR 正文至少说明：

- 实际改变的行为；
- Scope 是否扩大；
- Reuse Targets 是否被复用；
- Architecture / Invariant / API 是否变化；
- Failure Behavior 是否一致；
- 执行过哪些机器验证；
- 哪些验证无法执行；
- Human Acceptance 的执行步骤、执行者与结果；
- 是否触发 Stop Condition。

推荐人工签收记录：

```text
Human Acceptance: PASS / FAIL
Accepted by: <human identity>
Environment: <OS / hardware / runtime / provider>
Steps executed: <short list>
Evidence: <logs / screenshots / request-response / trace>
Known gaps: <none or explicit gaps>
```

## 11. BurnCloud Node 特殊边界

Node Issue 还必须遵守：

1. 优先复用现有 Server、Router、Database、Model Service、Download、Monitor。
2. 不得创建第二 Gateway、Router、Downloader、Database、Model/Cache truth，除非独立 Architecture Issue 批准。
3. Local Model 必须通过现有 Channel / Ability 进入 ModelRouter。
4. Resolver 只选择，不下载、不启动。
5. Model Preparation 管 Artifact，不管当前请求路由。
6. Runtime 定义“如何运行”，Process Manager 管真实进程。
7. `Process Spawned != Model READY`。
8. Gateway / Protocol compatibility 由 NODE-004 明确验收，不能因为现有代码存在就跳过。
9. Model Manager 的 inventory/cache/delete 由 NODE-304 明确验收，删除默认 fail closed。
10. Node v0.1 HardwareProfile vendor-neutral，但 GPU 自动检测是 NVIDIA-first。
11. BurnCloud Network/P2P/Multi-node 属于 Future，不是 Node v0.1 完成条件。
12. Implementation Plan 子页面默认 `PLANNED`，不能直接作为 Codex 授权。

## 12. Source of Truth

本页面定义 Engineering Issue / READY / DONE / Human Acceptance 的规范语义。

[Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/) 是每个 NODE Issue 的 canonical Human Acceptance Registry。

`burncloud/burncloud` 中的：

```text
.github/ISSUE_TEMPLATE/engineering_task.yml
docs/agent/TASK_CONTRACT.md
Agent / Harness rules
CI gates
```

属于本标准的执行实现，可以强化约束，但不得定义冲突语义。
