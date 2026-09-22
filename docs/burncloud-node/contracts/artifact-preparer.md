---
title: "ArtifactPreparer Contract"
slug: /burncloud-node/contracts/artifact-preparer/
---

# `ArtifactPreparer` Contract

```text
Owner: crates/platform/node
Status: Accepted / Framework Only
Source: crates/platform/node/src/preparation.rs
Fake: FakeArtifactPreparer
```

## 名称边界

Integration Queue 可以把这类伙伴代码归到 “Artifact Downloader”，但代码中的公开 Contract 是 `ArtifactPreparer`。

```text
ArtifactPreparer
├─ 可以通过下载准备 Artifact
├─ 也可以复用已经存在的本地 Artifact
└─ 因此不能收窄成只允许下载
```

## 唯一职责

把 `ArtifactRequest` 转换成经过准备和验证的本地 `PreparedArtifact`。

```rust
async fn prepare(
    &self,
    request: ArtifactRequest,
) -> Result<PreparedArtifact, ArtifactPrepareError>;
```

## 输入与输出

```text
ArtifactRequest
├─ source
└─ expected_digest
        ↓
ArtifactPreparer
        ├─ PreparedArtifact { local_path, verified }
        └─ ArtifactPrepareError
```

## 具体示例

输入：

```text
ArtifactRequest
├─ source: "qwen-4b/fake.gguf"
└─ expected_digest: Some("sha256:fake")
```

成功输出：

```text
PreparedArtifact
├─ local_path: "/fake/artifacts/qwen-4b_fake.gguf"
└─ verified: true
```

失败输出：

```text
ArtifactPrepareError::PrepareFailed(
    "artifact digest mismatch"
)
```

失败时不得返回一个被当作成功使用的 `PreparedArtifact`，也不得继续启动 Runtime 或进程。

## 不负责什么

```text
ArtifactPreparer 不负责
├─ 选择模型或 Variant
├─ 决定使用哪种 Runtime
├─ 生成启动参数
├─ 启动或停止进程
├─ 检查服务 READY
└─ 注册路由 Channel
```

## 必须保持的真相

- `local_path` 是后续步骤可使用的本地位置 Receipt。
- `verified = true` 才能继续准备流程。
- 下载、缓存、断点续传和校验方式属于实现内部，不进入 Orchestrator。

## BDD 边界

```gherkin
Scenario: Artifact cannot be verified
  When ArtifactPreparer prepares the request
  Then it returns an error or an unverified receipt
  And RuntimePreparer is not treated as proof that the artifact is valid
  And no process is started
```

## 停止条件

如果需要修改模型选择、Runtime、进程或路由才能完成 Artifact 准备，立即停止并拆分为其他 Owner 的任务。
