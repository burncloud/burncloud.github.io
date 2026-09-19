---
title: "NODE-303：Artifact 校验、失败状态与恢复"
slug: /burncloud-node/implementation-plan/node-303/
---

# NODE-303：Artifact 校验、失败状态与恢复

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Model Preparation**  
**功能依赖：NODE-302**

> 这是实施计划，不是 Codex 的直接开发授权。实现前必须重新核对 current `main` 并通过 READY Gate。

### TL;DR

NODE-303 要在模型文件真正进入 `READY` 前做必要的完整性校验，并把中断、损坏、校验失败和恢复过程变成明确状态。这样“下载结束”“文件存在”和“Runtime 可以安全使用”不再混为一谈。完成后，Runtime Manager 永远只接收已经通过 Preparation 验证的 Artifact。

### 背景与动机（Why）

现有 DownloadManager 能知道 aria2 任务是否 complete，但下载任务 complete 并不能证明本地文件满足 Manifest 要求。文件可能被截断、旧版本残留、size/checksum 不匹配，或者上次异常退出留下了看似存在的路径。

如果不在 Runtime 前建立最后一道校验门，错误会从“模型文件损坏”变成“llama-server 启动失败”，让问题更难诊断。NODE-303 只负责**Artifact correctness 与 recovery**，不检查 Runtime 的 HTTP health。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 根据 Manifest 做 size/checksum 等校验 | 不做 Runtime health check |
| 校验成功后才能进入 Artifact READY | 不解析模型语义是否“聪明” |
| 记录 validation failure 原因 | 不启动 llama-server |
| 支持中断/损坏后的明确恢复路径 | 不修改 Router |
| 避免部分文件误判 READY | 不把进程状态混入 Artifact state |

### 风险与安全网（Risk）

> 这是**进入 Runtime 前的 fail-closed 安全门**：校验不确定时宁可保持非 READY，也不能为了快速启动而跳过完整性检查。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Artifact `READY` 必须以可验证条件为准，而不是“文件存在”？
2. 是否同意 checksum/size 条件由 Manifest 声明，Preparation 只执行校验？
3. 是否同意校验失败只影响 Artifact，不直接改 Router / Runtime 状态？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
prepared local candidate
        ↓
manifest-driven validation
        ↓
VALID → Artifact READY
INVALID / INTERRUPTED → FAILED / recoverable state
```

### 2. Evidence

- `DownloadManager` 当前追踪 download complete/error，但不代表 Node Artifact 的最终可运行校验合同。
- `ModelService` 当前能定位 model data directory / files，但 current main 尚无独立的 Artifact integrity gate。
- `InferenceService` 当前直接以 `file_path` 启动 llama-server，证明验证边界需要在 Runtime 前显式补齐。

### 3. Entry / Starting Point

重新检查：

```text
NODE-301 Artifact State
NODE-302 Preparation orchestration
NODE-201 Manifest integrity fields
current local model storage layout
```

### 4. Reuse Targets / Do Not Recreate

Reuse：Manifest 的 Artifact facts、NODE-301 state、现有文件存储路径。  
Do Not Recreate：download manager、Runtime health subsystem、model semantics analyzer。

### 5. Scope

#### Allowed

- size / checksum / Manifest-declared integrity checks；
- validation state transition；
- corrupted / partial file detection；
- retry/recovery entry semantics；
- validation diagnostics；
- file-fixture tests。

#### Avoid

- model quality / architecture semantic inference；
- Runtime binary / health；
- process spawn；
- Router / Channel；
- download implementation replacement。

### 6. Behavior Contract

Inputs：prepared Artifact candidate + Manifest integrity requirements。  
Output：`READY` 或结构化 validation failure。

必须满足：

```text
file exists != READY
download complete != READY unless required validation passes
validation failure preserves diagnostic reason
recovery re-runs required validation before READY
```

### 7. Failure / Forbidden Fallbacks

禁止：

```text
checksum mismatch => warn and continue
missing required checksum/size => guess success
partial file => READY
validation failure => launch runtime to "see if it works"
runtime /v1/models health => use as artifact validation
```

### 8. Impact / Invariants

```text
persistence: update existing Artifact state/diagnostics only
external_calls: none required
billing/auth/routing: none
process/runtime: none
filesystem: read/cleanup/recovery operations limited to owned artifact path
```

Candidate invariant：**READY Artifact 必须通过 Manifest 所要求的完整性校验。**

### 9. Dependencies

前置：`NODE-302`。  
后续：`NODE-401`。

### 10. Stop Conditions

STOP IF：需要通过启动 Runtime 才能判断 Artifact 完整、需要跳过 required validation、需要改写下载技术、或无法确认 Artifact 文件所有权而可能删除无关文件。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] Manifest-required validation 可以执行。
- [ ] 校验通过才进入 Artifact READY。
- [ ] partial/corrupt/mismatch 有结构化失败状态。
- [ ] recovery 后必须重新校验才能 READY。

### ✅ 边界保护

- [ ] 未用 Runtime health 代替 Artifact validation。
- [ ] 未启动模型进程。
- [ ] 未修改 Router / Channel / Billing / Auth。
- [ ] 未删除无法确认 ownership 的文件。

### ✅ 回归与验证

- [ ] tests 覆盖 valid、size mismatch、checksum mismatch、partial file、recovery success。
- [ ] validation failure 不会泄漏成 Artifact READY。
- [ ] NODE-301 state transitions 保持一致。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确 Manifest integrity requirements 与文件 ownership。
- [ ] 只通过分支 + Pull Request 合并。


---

## 第四层：人类验收（Human Acceptance）

> 本节由 [Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/) 生成。机器测试、CI 或 AI Review 不能替代这里的人工验收。

### NODE-303 — Artifact 校验 / 失败 / 恢复

**验收者：** 模型/Runtime 工程师。

**人工步骤：**
1. 准备一个正确 Artifact、一个截断文件、一个 checksum 错误文件。
2. 分别执行验证。
3. 修复损坏文件后重新验证。

**人类通过标准：** 只有满足 Manifest 要求的 Artifact 才 READY；损坏/部分文件有明确原因；修复后必须重新验证才能 READY。

**人工判定失败：** checksum mismatch 只 warning 后继续、下载 complete 自动等于 READY、或通过“启动 llama-server 看看”替代 Artifact 校验。

**建议证据：** valid/mismatch/partial/recovery 四组结果。
