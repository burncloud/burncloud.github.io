---
title: "NODE-302：复用下载系统完成 Prepare / 去重"
slug: /burncloud-node/implementation-plan/node-302/
---

# NODE-302：复用下载系统完成 Prepare / 去重

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Model Preparation**  
**功能依赖：NODE-301**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `main` 并通过 READY Gate。

### TL;DR

NODE-302 要复用现有 ModelService / DownloadManager，把 `ResolvedModel` 需要的 Artifact 准备到本地，并确保同一个 Artifact 同时只产生一个真实下载任务。它不重新发明下载技术，也不允许第一次推理请求卡住几十分钟等大模型。完成后，模型准备会变成可追踪、可复用、可去重的显式步骤。

### 背景与动机（Why）

BurnCloud 当前已有 aria2-based `DownloadManager`，支持数据库记录、进度监控、暂停/恢复和未完成任务恢复；ModelService 也能构造 Hugging Face 下载 URL 并调用 DownloadManager。问题是 Node 还缺一层以“Artifact identity”为单位的 Preparation 编排和并发去重。

如果每次需要模型都直接 `add_download()`，两个并发请求可能创建两个真实下载任务；如果把下载塞进 inference 请求，又会让 API 请求承担长时间准备工作。NODE-302 因此只负责**准备编排与去重**，下载实现继续属于现有 DownloadManager。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 复用 ModelService / DownloadManager | 不创建 NodeDownloader |
| 以 Artifact identity 做 prepare 去重 | 不在 inference 请求里长时间阻塞下载 |
| 已有完整 Artifact 直接复用 | 不把下载完成直接当校验 READY |
| Preparation 状态接入 NODE-301 | 不启动 Runtime |
| 明确失败 / 重试入口 | 不绕过现有下载数据库 |

### 风险与安全网（Risk）

> 这是**现有下载能力的编排层**：即使准备失败，也只能让 Artifact 保持非 READY；不能为了“继续运行”绕过验证、启动半成品文件或再造下载系统。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Node 复用现有 DownloadManager，而不是创建 NodeDownloader？
2. 是否同意同一 Artifact 的并发 prepare 必须合并为一个实际下载任务？
3. 是否同意 v0.1 的 inference API 不自动等待大型 Artifact 下载完成？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
ResolvedModel + ArtifactState
        ↓
prepare(artifact_identity)
        ↓
reuse existing READY/complete candidate
        OR
single deduplicated DownloadManager task
        ↓
PREPARING / downloaded candidate
        ↓
NODE-303 verification
```

### 2. Evidence

- `crates/download/src/lib.rs :: DownloadManager` 当前通过 aria2 执行下载，保存状态/进度到 `DownloadDB`，并恢复 incomplete downloads。
- `ModelService::download_model_file()` 当前会创建 `DownloadManager` 并调用 `add_download()`。
- `DownloadManager::add_download()` 本身按调用创建下载任务；current main 没有以 Node Artifact identity 为单位的明确并发 prepare 去重合同。

### 3. Entry / Starting Point

重新检查：

```text
NODE-301 Local Artifact State
NODE-204 ResolvedModel
crates/service/crates/models/src/lib.rs
crates/download/src/lib.rs
current DownloadDB schema / task identity
```

### 4. Reuse Targets / Do Not Recreate

Reuse：`ModelService`、`DownloadManager`、`DownloadDB`、existing aria2 continuation/recovery。  
Do Not Recreate：NodeDownloader、parallel download DB、custom HTTP downloader。

### 5. Scope

#### Allowed

- Preparation orchestration；
- Artifact identity → existing local file / download task lookup；
- concurrent prepare deduplication；
- download task reuse / join semantics；
- state transitions to NODE-301；
- explicit prepare errors；
- targeted concurrency tests。

#### Avoid

- Artifact integrity verification（NODE-303）；
- Runtime / Process；
- first inference request hidden auto-prepare；
- replacing aria2 / DownloadManager；
- Router / Billing / Auth。

### 6. Behavior Contract

Inputs：`ResolvedModel` + Local Artifact State。  
Output：prepared candidate awaiting/eligible for NODE-303 verification，或明确 prepare failure。

核心并发合同：

```text
same artifact identity + concurrent prepare
                ↓
       one underlying download task
                ↓
 multiple callers observe/join same preparation
```

已有可复用文件：不创建新 download task，但是否 READY 仍由 NODE-303 校验语义决定。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
concurrent prepare => multiple real downloads
first inference => block until huge model finishes downloading
DownloadManager unavailable => implement temporary downloader
existing file => skip all verification
prepare failure => start Runtime with partial file
```

### 8. Impact / Invariants

```text
persistence: reuse existing download/model persistence
external_calls: model artifact download via existing manager
billing/auth/routing: none
process runtime: no model spawn
concurrency: artifact-keyed preparation coordination
```

Candidate invariant：**下载技术属于现有 DownloadManager；Node 只编排 Artifact preparation。**

### 9. Dependencies

前置：`NODE-301`。  
后续：`NODE-303`。

### 10. Stop Conditions

STOP IF：去重必须重写 downloader、需要新下载数据库、需要把下载塞进 inference 请求、需要把未验证文件直接标 READY、或 scope 扩展到 Runtime/Router。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] ResolvedModel 可以进入明确 Preparation 流程。
- [ ] 同一 Artifact 并发 prepare 只创建一个真实下载任务。
- [ ] 已有候选文件可复用，不重复下载。
- [ ] prepare 状态与 NODE-301 一致。

### ✅ 边界保护

- [ ] 未创建 NodeDownloader / 第二套 DownloadDB。
- [ ] 未在 inference 请求中实现隐藏的长时间 auto-download。
- [ ] 未把 downloaded candidate 直接等同于最终 READY。
- [ ] 未启动 Runtime / Process。

### ✅ 回归与验证

- [ ] tests 覆盖并发去重、已有文件复用、下载失败、任务恢复/复用。
- [ ] existing DownloadManager pause/resume/recovery 语义不被破坏。
- [ ] partial file 不会进入 Runtime。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确 Artifact identity / dedup key。
- [ ] 只通过分支 + Pull Request 合并。
