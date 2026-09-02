---
title: "NODE-302：后台 Prepare、磁盘准入与下载去重"
slug: /burncloud-node/implementation-plan/node-302/
---

# NODE-302：后台 Prepare、磁盘准入与下载去重

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Model Preparation**  
**功能依赖：NODE-301、NODE-103、NODE-204**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-302 要让本地模型准备完全后台化：当 Node 收到一个模型需求后，只启动一条 Prepare / Download 任务，并在下载前检查磁盘是否足够。当前 `/v1` 请求绝不能因为大型模型下载而被长期阻塞。完成后，1000 个相同模型请求也只会触发 1 个实际下载。

### 背景与动机（Why）

用户不会手工点击“下载模型”。因此 Preparation 必须能由 Demand Reconciler 自动触发，同时又不能让 Router 或请求处理线程变成下载器。现有 DownloadManager 已有 aria2、DB 状态、恢复和进度能力，Node 应复用它并补齐 demand dedup 与磁盘准入。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 后台 Prepare / Download | 不在 `/v1` 请求里同步等待下载 |
| 相同 Artifact 并发去重 | 不创建 NodeDownloader |
| 下载前检查可用磁盘 | 不判断 GPU Variant（Resolver 已完成） |
| 复用 DownloadManager / ModelService | 不启动 Runtime |
| 维护 PREPARING / failure facts | 不决定 Provider fallback |

### 风险与安全网（Risk）

> 宁可明确返回 `INSUFFICIENT_DISK` 或保持 PREPARING，也不能为了“自动”而重复下载、占满磁盘或阻塞请求。

### 审批者关注点（Reviewer Focus）

1. 是否同意下载必须后台化？
2. 是否同意同一 Artifact 只能有一个 active prepare pipeline？
3. 是否同意磁盘不足必须在下载前尽早失败并可诊断？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
ResolvedModel
+ Local Artifact State
+ current disk facts
        ↓
Prepare admission
        ↓
ABSENT -> PREPARING
        ↓
existing ModelService / DownloadManager
        ↓
download completed
        ↓
NODE-303 verification
```

### 2. Evidence

- current DownloadManager 已有 DB-backed download status、aria2、resume/remove、restore incomplete downloads。
- current ModelService 已有 model/file/source knowledge。
- NODE-204 会提供 Artifact identity / expected size（when known）。
- current implementation 尚无“model demand -&gt; exactly one background prepare”合同。

### 3. Reuse Targets / Do Not Recreate

Reuse：ModelService、DownloadManager、Download DB/state、NODE-301 Artifact state、NODE-103 disk facts。  
Do Not Recreate：第二套 downloader、第二套 download DB、request-local downloader。

### 4. Scope

#### Allowed

- prepare admission；
- disk capacity check；
- same-artifact in-flight dedup；
- background task coordination；
- existing DownloadManager invocation；
- retry/reuse of resumable incomplete download；
- structured preparation failure；
- concurrency tests。

#### Avoid

- Variant selection；
- Artifact integrity verification（NODE-303）；
- Runtime / Process spawn；
- Router / Provider fallback；
- blocking `/v1` until download finishes。

### 5. Behavior Contract

```text
same artifact + N concurrent demands => <= 1 active prepare execution
READY artifact => no download
PREPARING artifact => join/observe existing preparation, do not duplicate
ABSENT + enough disk => start background preparation
ABSENT + insufficient disk => fail with INSUFFICIENT_DISK
failed resumable download => follow explicit retry/resume policy
```

Disk admission 至少应考虑：

```text
required_bytes (from manifest/ResolvedModel when known)
available_disk
safety margin / temporary download overhead if required by actual downloader
```

请求路径只允许提交/观察 demand，不允许持有下载 Future 直到模型完成。

### 6. Failure / Forbidden Fallbacks

结构化失败至少支持：

```text
INSUFFICIENT_DISK
ARTIFACT_SOURCE_UNAVAILABLE
DOWNLOAD_FAILED
DOWNLOAD_STATE_CONFLICT
```

禁止：

```text
100 requests => 100 downloads
insufficient disk => start anyway
provider available => cancel background preparation automatically
request handler => wait for full model download
prepare failure => mark Artifact READY
create NodeDownloader because wrapping existing DownloadManager is inconvenient
```

### 7. Impact / Invariants

```text
persistence: reuse existing download/model state
external_calls: artifact source download
billing/auth/routing: none
process/runtime: none
```

Candidate invariants：
- **Same Artifact has at most one active preparation pipeline.**
- **Inference request does not synchronously wait for large model preparation.**

### 8. Dependencies

前置：NODE-301、NODE-103、NODE-204。  
后续：NODE-303、NODE-504。

### 9. Stop Conditions

STOP IF：必须创建第二套 downloader、必须阻塞 inference request、无法避免重复下载、无法在下载前得到可信磁盘事实、或必须修改 Router/Billing/Auth 才能 Prepare。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] ABSENT Artifact 可通过后台 Prepare 进入 PREPARING。
- [ ] 相同 Artifact 的并发需求只产生一个实际下载任务。
- [ ] PREPARING 状态可复用/观察，不重复执行。
- [ ] 下载前执行磁盘准入。
- [ ] 磁盘不足返回结构化 `INSUFFICIENT_DISK`。
- [ ] 下载完成交给 NODE-303，而不是直接标记 READY。

### ✅ 边界保护

- [ ] 未创建第二套 downloader / download DB。
- [ ] 未在 Router 内执行下载。
- [ ] 未让 `/v1` 请求同步等待完整下载。
- [ ] 未提前启动 Runtime。

### ✅ 回归与验证

- [ ] 并发测试证明 N 个相同 demand &lt;= 1 个下载。
- [ ] tests 覆盖 READY/no-op、PREPARING/dedup、disk insufficient、download failure、resume。
- [ ] existing DownloadManager 基础行为不被破坏。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确真实 downloader / disk state ownership。
- [ ] 只通过分支 + Pull Request 合并。
