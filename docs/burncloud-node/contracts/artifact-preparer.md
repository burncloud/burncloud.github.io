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
├─ source: ArtifactSource
│   ├─ File(PathBuf)   // 本地路径
│   ├─ Http(Url)       // http 地址
│   └─ Oci(String)     // 镜像仓库链接
└─ expected_digest: Option<Digest>   // 摘要算法 + 十六进制摘要
        ↓
ArtifactPreparer
        ├─ PreparedArtifact { local_path, verified }
        └─ ArtifactPrepareError
```

`source` 是强类型来源，编译器据此区分本地文件、HTTP 地址与镜像仓库链接；`expected_digest` 是结构化摘要，包含校检算法与规范化摘要。`DigestAlgorithm` 支持 `Sha1`、`Sha256`、`Sha384`、`Sha512` 与 `Md5`，摘要值在创建时校验并规范化为小写十六进制，非法格式在解析阶段即被拒绝，不会进入准备流程。

## 具体示例

输入（复用已存在的本地 Artifact）：

```text
ArtifactRequest
├─ source: ArtifactSource::File(PathBuf::from("/fake/artifacts/qwen-4b_fake.gguf"))
└─ expected_digest: Some(Digest::parse("sha256:6d82e5c3a7f1b90284d0f6e1ab93cd2715f64a08b3c9d7e0f4a35b6c8d1029e4").unwrap())
```

输入（经 HTTP 下载）：

```text
ArtifactRequest
├─ source: ArtifactSource::Http(Url::parse("https://fake.example.com/qwen-4b/fake.gguf").unwrap())
└─ expected_digest: Some(Digest::parse("sha256:6d82e5c3a7f1b90284d0f6e1ab93cd2715f64a08b3c9d7e0f4a35b6c8d1029e4").unwrap())
```

成功输出：

```text
PreparedArtifact
├─ local_path: "/fake/artifacts/qwen-4b_fake.gguf"
└─ verified: true
```

失败输出（校验不匹配）：

```text
ArtifactPrepareError::PrepareFailed(
    "artifact digest mismatch"
)
```

失败输出（摘要非法，如算法不受支持或非十六进制）：

```text
DigestError::UnsupportedAlgorithm("md6")
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
