---
title: "NODE-304：建立 Artifact Inventory / Cache / Delete Lifecycle"
slug: /burncloud-node/implementation-plan/node-304/
---

# NODE-304：建立 Artifact Inventory / Cache / Delete Lifecycle

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Model Preparation / Artifact Lifecycle**  
**功能依赖：NODE-301、NODE-303**

> 这是实施计划，不是 Codex 的直接开发授权。实现前必须基于 current `burncloud/burncloud/main` 重新确认 ModelService / DownloadManager / local artifact ownership，并通过 READY Gate。

### TL;DR

NODE-304 补齐 Model Manager 产品文档里已经承诺、但当前 Implementation Plan 没有独立责任人的 `list / cache / delete / status` 生命周期。它不创建新的模型管理系统，而是把 NODE-301 的 Artifact State、现有 ModelService 的 CRUD/文件能力和真实磁盘文件收敛成一个安全的本地 Artifact Inventory。完成后，人可以知道 Node 本地到底有哪些模型文件、占多少空间、当前是否可用，并能在明确 ownership 和 in-use 条件下安全删除。

### 背景与动机（Why）

NODE-301~303 已经覆盖 Artifact 状态、下载、磁盘准入、去重、完整性校验与失败恢复，但 Model Manager 产品页还明确声明：

```text
cache
list
delete
status
```

如果没有 NODE-304，这些能力要么变成“大家默认现有 ModelService 应该已经够用”，要么未来由 UI/CLI 各自直接操作文件系统，形成第二套事实和高风险删除路径。

NODE-304 只建立**库存与安全删除合同**。它不重新选择 Variant、不启动 Runtime、不决定 Router，也不建设复杂自动缓存策略。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 统一 Artifact inventory/list | 不创建第二套 Model DB |
| 显示真实 status/size/ownership | 不通过目录扫描猜 READY |
| 安全 delete/cleanup | 不删除 ownership 不明文件 |
| 删除后清理 stale state/cache | 不直接删除正在服务的 Artifact |
| 最小 cache lifecycle / storage facts | 不做复杂 LRU/自动容量调度 |
| 复用 ModelService / existing storage | 不重新选择 Variant |

### 风险与安全网（Risk）

> 删除模型是不可逆文件操作。NODE-304 的默认策略必须是 fail closed：只要 ownership、in-use 状态或目标路径不确定，就拒绝删除，而不是“尽量清理”。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Artifact Inventory 的状态真相来自现有模型/下载状态 + NODE-301，而不是单纯扫描目录？
2. 是否同意 in-use / ownership 不明时禁止删除？
3. 是否同意 v0.1 只做最小 cache/list/delete，不提前建设自动 LRU / GPU-aware cache scheduler？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立本地 Artifact 生命周期的可查询与安全清理合同：

```text
existing model/download facts
+ NODE-301 Artifact State
+ owned storage paths
        ↓
Artifact Inventory
        ↓
list / status / size / ownership
        ↓
Delete Admission
        ↓
filesystem cleanup
+ state cleanup
        ↓
ABSENT
```

### 2. Evidence

STATIC CONFIRMED：

- Model Manager 产品页把 `cache / list / delete / status` 列为最小职责；
- NODE-301 已确认 current ModelService 存在 model CRUD、data directory 与物理文件清理基础能力；
- NODE-301~303 已建立 Artifact identity/state、prepare、verification；
- current plan 尚无独立 Issue 对 inventory、cache lifecycle 和安全删除负责。

### 3. Entry / Starting Point

READY Audit 重新检查：

```text
crates/service/crates/models/
crates/download/
current model/download DB schema
current model data directory ownership
NODE-301 Local Artifact State
NODE-303 verification/recovery
NODE-401/402 runtime/process ownership needed for in-use check
```

### 4. Reuse Targets / Do Not Recreate

Reuse：ModelService、ModelDatabase、DownloadManager/DB 可复用状态、NODE-301 Artifact State、现有受管理模型目录。

Do Not Recreate：

```text
NodeModelInventoryDB
NodeCacheDB
second filesystem model registry
second downloader
```

### 5. Scope

#### Allowed

- authoritative inventory projection；
- list/status/size/variant/runtime reference/owned path 等最小字段；
- cache presence / reusable Artifact facts；
- delete admission；
- in-use guard；
- owned file cleanup；
- stale model/download/artifact state cleanup；
- failed/partial artifact explicit cleanup when ownership is proven；
- tests for delete safety and consistency。

#### Avoid

- complex automatic LRU / quota scheduler；
- Variant re-selection；
- network download；
- Runtime spawn/stop 机制重写；
- Router/Channel；
- arbitrary filesystem browser；
- deletion outside BurnCloud-owned artifact paths。

### 6. Behavior Contract

#### Inventory

每个 inventory item 至少应让调用方区分：

```text
canonical model identity
variant / artifact identity
local state
size / bytes on disk when known
owned storage location or opaque storage identity
in-use / protected status when determinable
last failure/diagnostic when relevant
```

Inventory 不能通过“目录里有 `.gguf`”直接推断 READY；READY 必须继承 NODE-301/303 的状态语义。

#### Delete Admission

```text
owned + not in use + safe target => may delete
in use                         => reject
ownership unknown              => reject
path outside managed storage   => reject
state conflict                 => reject or require reconciliation
```

删除成功后，文件系统和 authoritative Artifact state 必须一致收敛到 ABSENT/removed，不允许留下 ghost READY。

#### Cache Scope

v0.1 的 cache 只表示“本地已存在、可复用的 Artifact facts 与存储生命周期”。复杂 LRU、预热集合、自动空间回收策略属于后续独立设计。

### 7. Failure / Forbidden Fallbacks

结构化失败至少考虑：

```text
ARTIFACT_IN_USE
ARTIFACT_OWNERSHIP_UNKNOWN
ARTIFACT_NOT_FOUND
DELETE_PERMISSION_DENIED
DELETE_FAILED
STATE_CONFLICT
```

禁止：

```text
path looks like model => delete
in use => force delete then let runtime fail
unknown ownership => best effort cleanup
filesystem delete success => leave READY in DB
DB delete success => ignore file delete failure
cache cleanup => choose a different Variant automatically
```

### 8. Impact / Invariants

```text
persistence: existing model/download/artifact state cleanup only
external_calls: none
billing_auth_routing: none
filesystem: yes, restricted to proven BurnCloud-owned artifact paths
runtime_process: read in-use/protection fact only; no lifecycle ownership
```

必须保持：

- Artifact state 与 Process state 分离；
- READY 仍由 Preparation/Verification 决定；
- delete fail closed；
- no second model/cache database；
- inventory 是投影，不是第二份 source of truth。

### 9. Dependencies

前置：NODE-301、NODE-303。  
若安全 delete 需要判断 Runtime in-use，READY Gate 必须确认 NODE-402/403/404 已提供可复用的真实状态；不能在 NODE-304 自己重建 Process Manager。

NODE-503 最终产品验收应把 NODE-304 纳入 Node v0.1 完整功能覆盖，但 NODE-503 的推理主链不应依赖人工 delete 才能成功。

### 10. Stop Conditions

```text
STOP IF:
- ownership cannot be proven safely
- delete requires arbitrary path access
- inventory requires a second model/cache DB
- in-use check requires rebuilding process lifecycle
- implementation needs complex automatic cache scheduling
- deletion semantics conflict with current ModelService ownership
- meaningful filesystem safety tests cannot be performed
```

---

## 第三层：验收层（Definition of Done）

### ✅ Inventory / Status

- [ ] 本地已管理 Artifact 可以通过一个权威 inventory 查询。
- [ ] inventory 不用路径存在冒充 READY。
- [ ] state/variant/size/ownership 等关键信息可查询。
- [ ] failed/partial/ready 等状态与 NODE-301/303 一致。

### ✅ Delete / Cache Lifecycle

- [ ] 明确 owned 且未使用的 Artifact 可以安全删除。
- [ ] in-use Artifact 默认拒绝删除。
- [ ] ownership 不明或 managed root 外路径拒绝删除。
- [ ] 文件删除和状态清理要么一致成功，要么留下可恢复/可诊断失败，不能产生 ghost READY。
- [ ] 删除后再次 inventory 显示真实 ABSENT/removed 状态。

### ✅ 边界保护

- [ ] 未创建第二套 Model/Cache DB。
- [ ] 未实现复杂自动 LRU / capacity scheduler。
- [ ] 未重新选择 Variant。
- [ ] 未改 Router / Channel / Billing / Auth。
- [ ] 未把 Process Manager 职责复制进 Inventory。

### ✅ 回归与验证

- [ ] tests 覆盖 list、ready/failed/partial status、delete success、in-use reject、ownership reject、filesystem failure、state conflict。
- [ ] 删除操作不会作用于非 BurnCloud-owned 文件。
- [ ] existing ModelService / DownloadManager 基础行为不被破坏。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确真实 storage ownership / in-use source / state cleanup path。
- [ ] 实现只通过分支 + Pull Request 合并。


---

## 第四层：人类验收（Human Acceptance）

> 本节由 [Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/) 生成。机器测试、CI 或 AI Review 不能替代这里的人工验收。

### NODE-304 — Artifact Inventory / Cache / Delete Lifecycle

**验收者：** 产品负责人 + 模型存储工程师。

**人工步骤：**
1. 准备至少两个本地 Artifact，并用 Node 的 inventory/list 能力查看。
2. 核对模型、Variant、大小、状态、路径归属等用户可理解信息。
3. 删除一个明确属于 BurnCloud 的未运行 Artifact，确认文件和状态一致消失。
4. 尝试删除正在被 Runtime 使用的 Artifact 或非 BurnCloud-owned 文件。

**人类通过标准：** list/status 反映真实本地库存；删除只作用于明确 owned Artifact；in-use/ownership 不明时 fail closed；删除后不留下假 READY cache/state。

**人工判定失败：** 删除到无关文件、正在服务的 Artifact 被直接删掉、库存与磁盘事实不一致，或 cache cleanup 自己重新选择 Variant。

**建议证据：** 删除前后 inventory + 文件系统对比 + in-use 拒绝记录。
