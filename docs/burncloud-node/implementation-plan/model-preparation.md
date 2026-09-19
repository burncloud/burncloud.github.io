---
title: "类别四：Model Preparation"
slug: /burncloud-node/implementation-plan/model-preparation/
---

# 类别四：Model Preparation

Model Preparation 把 `ResolvedModel` 自动收敛成经过验证、可查询、可安全管理的本地 Artifact。

```text
ResolvedModel
   ↓
Artifact State
   ↓
Disk Admission
   ↓
Background Prepare / Download
   ↓
Verification
   ↓
READY Artifact
   ↓
Inventory / Cache / Safe Delete
```

关键原则：

- 用户不手工下载模型；
- `/v1` 请求不等待大型模型下载；
- 相同 Artifact 只有一个 active preparation pipeline；
- 下载完成不等于 READY，必须经过校验；
- Inventory 是现有 Model/Download/Artifact facts 的投影，不是第二份 source of truth；
- 删除只能作用于明确属于 BurnCloud、且未被 Runtime 使用的 Artifact；
- 优先复用现有 ModelService + DownloadManager，不创建 `NodeDownloader`、第二套 Model DB 或 Cache DB。

本类别包括：

- **[NODE-301](/burncloud-node/implementation-plan/node-301/)**：Local Artifact State；
- **[NODE-302](/burncloud-node/implementation-plan/node-302/)**：后台 Prepare、磁盘准入与下载去重；
- **[NODE-303](/burncloud-node/implementation-plan/node-303/)**：Artifact 校验、失败与恢复；
- **[NODE-304](/burncloud-node/implementation-plan/node-304/)**：Artifact Inventory / Cache / Delete Lifecycle。

NODE-304 补齐 `/burncloud-node/model-manager/` 已声明的 `list / cache / delete / status` 产品职责，但 v0.1 不建设复杂 LRU、自动空间调度或 warm-set 策略。

Model Preparation 不负责 Provider fallback，也不直接拥有 Runtime/Process 生命周期；这些分别属于现有 Router 与后续 Runtime/Reconciler 合同。
