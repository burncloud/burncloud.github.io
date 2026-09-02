---
title: "类别四：Model Preparation"
slug: /burncloud-node/implementation-plan/model-preparation/
---

# 类别四：Model Preparation

Model Preparation 把 `ResolvedModel` 自动收敛成经过验证的本地 Artifact。

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
```

关键原则：

- 用户不手工下载模型；
- `/v1` 请求不等待大型模型下载；
- 相同 Artifact 只有一个 active preparation pipeline；
- 下载完成不等于 READY，必须经过校验；
- 优先复用现有 ModelService + DownloadManager，不创建 `NodeDownloader`。

本类别包括：

- **NODE-301**：Local Artifact State；
- **NODE-302**：后台 Prepare、磁盘准入与下载去重；
- **NODE-303**：Artifact 校验、失败与恢复。

Model Preparation 不负责 Provider fallback，也不直接启动 Runtime；这些分别属于现有 Router 与后续 Runtime/Reconciler 合同。
