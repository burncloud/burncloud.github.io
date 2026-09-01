---
title: "NODE-301：建立 Local Artifact State"
slug: /burncloud-node/implementation-plan/node-301/
---

# NODE-301：建立 Local Artifact State

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Model Preparation**  
**功能依赖：NODE-204**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-301 要让 BurnCloud 明确知道一个 `ResolvedModel` 对应的本地 Artifact 现在是 absent、preparing、ready 还是 failed，而不是只看“某个文件存在不存在”。这样下载中、损坏文件、上次失败和真正可运行的文件不会混在一起。完成后，Model Preparation 才能安全决定复用、准备或拒绝。

### 背景与动机（Why）

现有 BurnCloud 已有 ModelDatabase、ModelService 和 DownloadManager，DownloadManager 还会把下载状态写入数据库并恢复未完成下载。但“下载完成”与“这个 Artifact 已经可以交给 Runtime”仍然不是同一个概念。

如果 Node 只检查路径存在，部分下载、旧文件或校验失败文件都有机会被误判为 ready。NODE-301 因此只建立**Artifact 生命周期状态合同**，不重新实现下载器，也不混入 Runtime/Process 状态。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 定义 Local Artifact 状态 | 不创建第二套模型数据库 |
| 映射现有 model/download facts | 不重新实现下载器 |
| 区分 absent / preparing / ready / failed | 不混入 Process READY |
| 支持重启后的必要状态恢复 | 不把“文件存在”当 READY |
| 为 NODE-302/303 提供状态边界 | 不启动 Runtime |

### 风险与安全网（Risk）

> 这是**状态语义收口**：最坏结果应该是 Artifact 暂时无法进入 READY，而不能因为状态不清楚就把可疑文件交给 Runtime。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Artifact state 与 Process/Runtime state 完全分离？
2. 是否同意优先映射现有 Model / Download 状态，而不是建第二套数据库？
3. 是否同意 `READY` 必须代表“Preparation 已确认可使用”，不能只代表路径存在？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
ResolvedModel
     ↓
Artifact identity
     ↓
ABSENT / PREPARING / READY / FAILED
     ↓
NODE-302 prepare
NODE-303 verify/recover
```

### 2. Evidence

- `ModelService` 当前已有 model CRUD、data directory 和物理文件清理能力。
- `DownloadManager` 当前使用 DB 记录下载状态/进度，并在初始化时执行 `restore_incomplete_downloads()`。
- current `InferenceService` 仍直接接收 `file_path`，没有独立 Artifact readiness contract。

### 3. Entry / Starting Point

重新检查：

```text
crates/service/crates/models/
crates/download/
current model/download database schema
NODE-204 ResolvedModel
```

### 4. Reuse Targets / Do Not Recreate

Reuse：ModelService、ModelDatabase、DownloadManager、DownloadDB 中可复用状态。  
Do Not Recreate：NodeModelDB、NodeDownloadDB、第二套 downloader。

### 5. Scope

#### Allowed

- Artifact identity 到本地状态的映射；
- `ABSENT / PREPARING / READY / FAILED` 或等价明确状态机；
- 最小 persistence/state extension（仅 current architecture 证明必要时）；
- restart recovery semantics；
- state transition tests。

#### Avoid

- download orchestration（NODE-302）；
- checksum/完整性验证实现（NODE-303）；
- Runtime / Process state；
- Local Channel / Router；
- 第二套模型/下载数据库。

### 6. Behavior Contract

Inputs：`ResolvedModel.artifact_reference` + existing model/download/local-file facts。  
Output：authoritative Local Artifact State。

最小状态语义：

```text
ABSENT     = 本地没有可复用 Artifact
PREPARING  = Preparation 正在进行，尚不可交给 Runtime
READY      = Preparation 已确认 Artifact 可交给 Runtime
FAILED     = Preparation/verification 已失败，原因可诊断
```

`READY` 不等于 `Process READY`，也不等于“文件路径存在”。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
file exists => READY
aria2 complete => automatically READY without required verification
unknown persisted state => assume READY
Artifact failure => mark Runtime failed directly
create a new DB because mapping existing state is inconvenient
```

### 8. Impact / Invariants

```text
persistence: reuse existing model/download state; minimal extension only if justified
external_calls: none
billing/auth/routing: none
process/runtime: none
```

Candidate invariants：
- Artifact state 与 Process state 独立；
- READY Artifact 必须来自明确 Preparation contract。

### 9. Dependencies

前置：`NODE-204`。  
后续：`NODE-302`、`NODE-303`、`NODE-401`。

### 10. Stop Conditions

STOP IF：必须创建第二套 model/download DB、必须用路径存在冒充 READY、必须混入 process/readiness state、或 existing state ownership 无法在 current main 中确认。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] ResolvedModel 对应 Artifact 有唯一可查询的本地状态。
- [ ] ABSENT / PREPARING / READY / FAILED 语义明确。
- [ ] 重启后必要状态能安全恢复或重新判定。
- [ ] 文件不存在不会被标记 READY。

### ✅ 边界保护

- [ ] 未创建第二套模型/下载数据库。
- [ ] 未把 Runtime/Process state 混入 Artifact state。
- [ ] 未提前实现 NODE-302/303 的执行职责。

### ✅ 回归与验证

- [ ] tests 覆盖 absent、preparing、ready、failed 与 restart recovery。
- [ ] stale/unknown state 不会被当成 READY。
- [ ] 现有 ModelService / DownloadManager 基础行为不被破坏。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确真实 state source / persistence ownership。
- [ ] 只通过分支 + Pull Request 合并。
