---
title: "ArtifactPreparer Contract"
slug: /burncloud-node/contracts/artifact-preparer/
---

# `ArtifactPreparer` Contract

```text
Owner: crates/platform/node
Status: Accepted / Framework Only
Source: crates/platform/node/src/preparation/
Fake: FakeArtifactPreparer
```

`preparation/` 是以 `preparation.rs` 为模块根的目录模块，Contract 类型由模块根统一 re-export；`FakeArtifactPreparer` 位于 `crates/platform/node/src/fake.rs`。

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

该 trait 通过 `#[async_trait]` 声明，并要求实现满足 `Send + Sync`。准备的落点只有两个：`Ok(PreparedArtifact)` 或 `Err(ArtifactPrepareError)`；校验不一致属于前者。

## 类型清单

```text
crates/platform/node/src/preparation/
├─ artifact_preparer.rs            → ArtifactPreparer
├─ artifact_request.rs             → ArtifactRequest
├─ artifact_source.rs              → ArtifactSource
├─ artifact_source_error.rs        → ArtifactSourceError
├─ artifact_verification_status.rs → ArtifactVerificationStatus
├─ prepared_artifact.rs            → PreparedArtifact
├─ artifact_prepare_error.rs       → ArtifactPrepareError
├─ digest.rs                       → Digest
├─ digest_algorithm.rs             → DigestAlgorithm
└─ digest_error.rs                 → DigestError
```

## 输入与输出

```text
ArtifactRequest
├─ source: ArtifactSource
│   ├─ File(PathBuf)   // 当前部署系统的本地文件路径
│   └─ Http(Url)       // http 或 https 地址
└─ expected_digest: Option<Digest>
    └─ Digest { algorithm: DigestAlgorithm, value: String }
        ↓
ArtifactPreparer
        ├─ PreparedArtifact { local_path: PathBuf, verification_status }
        └─ ArtifactPrepareError
```

`ArtifactRequest::new(source, expected_digest)` 是唯一构造入口，`source()` 与 `expected_digest()` 只返回只读引用，调用方不能替换请求中的来源或摘要。`Display` 在无摘要时只输出来源，有摘要时追加 `(expected digest: sha256:...)`。

## 来源解析

```text
ArtifactSource 入口
├─ ArtifactSource::parse(&str) / FromStr
├─ From<&Path>
└─ TryFrom<&Url>
```

```text
字符串输入
├─ 空或只含空白 → ArtifactSourceError::Empty
├─ Windows 盘符路径（如 C:\models\model.gguf）→ File(PathBuf)
├─ 含 :// 但无法被 URL 解析 → ArtifactSourceError::InvalidUrl
├─ http / https（协议名大小写不敏感）→ Http(Url)
├─ file:// → Url::to_file_path() 转化为 File(PathBuf)，转换失败 → InvalidFileUrl
├─ 其他协议（oci://、ftp:// 等）→ ArtifactSourceError::UnsupportedScheme
├─ 不含 :// 但被 URL 解析器识别出协议名 → ArtifactSourceError::UnsupportedScheme
└─ 其余输入按文件路径处理；含空字节或不含合法路径 → InvalidFilePath
```

字符串解析路径上的协议白名单在来源解析阶段完成，非法来源不会进入准备流程；`From<&Path>` 与枚举变体直接构造属于调用方已持有合法路径的场景，不再重复校验。访问器 `as_file_path()` / `as_http()` / `is_file_path()` / `is_http()` 用于在实现中区分分支，`Display` 对 `File` 使用宿主平台的路径格式，对 `Http` 保留 URL 格式。

## 摘要

```text
DigestAlgorithm
├─ Md5     → 16 字节，32 个十六进制字符
├─ Sha1    → 20 字节，40 个十六进制字符
├─ Sha256  → 32 字节，64 个十六进制字符
├─ Sha384  → 48 字节，96 个十六进制字符
└─ Sha512  → 64 字节，128 个十六进制字符
```

算法名解析忽略大小写与连字符，`sha256`、`SHA256`、`sha-256` 与 `SHA-256` 解析为同一算法；`name()` 始终返回规范化名称（`md5`、`sha1`、`sha256`、`sha384`、`sha512`）。

```text
Digest 构造
├─ Digest::new(algorithm, value)   // 先校验长度，再校验字符集，通过后统一转小写
├─ Digest::parse("algorithm:digest") / FromStr
└─ Digest::algorithm() / value()   // 只读访问器；Display 输出规范化 algorithm:digest
```

`Digest::new` 先按算法期望长度校验（`BadLength { expected, actual }`），再校验是否全部为 ASCII 十六进制字符（`NotHex`）；`Digest::parse` 在缺少 `:` 分隔符时返回 `MissingAlgorithm`，算法名不受支持时返回 `UnsupportedAlgorithm`。摘要非法只会在解析阶段失败，不会作为准备阶段的错误出现。

## 具体示例

输入（复用已存在的本地 Artifact，校验一致）：

```text
ArtifactRequest
├─ source: ArtifactSource::parse("/fake/artifacts/qwen-4b_fake.gguf").unwrap()
└─ expected_digest: Some(Digest::parse("sha256:6d82e5c3a7f1b90284d0f6e1ab93cd2715f64a08b3c9d7e0f4a35b6c8d1029e4").unwrap())
```

输出：

```text
PreparedArtifact
├─ local_path: "/fake/artifacts/qwen-4b_fake.gguf"   // 绝对路径
└─ verification_status: ArtifactVerificationStatus::Verified
```

输入（经 HTTP 下载，下载成功但校验与期望摘要不一致）：

```text
ArtifactRequest
├─ source: ArtifactSource::Http(Url::parse("https://fake.example.com/qwen-4b/fake.gguf").unwrap())
└─ expected_digest: Some(Digest::parse("sha256:6d82e5c3a7f1b90284d0f6e1ab93cd2715f64a08b3c9d7e0f4a35b6c8d1029e4").unwrap())
```

输出：

```text
PreparedArtifact
├─ local_path: "/data/cache/qwen-4b_fake.gguf"
└─ verification_status: ArtifactVerificationStatus::Failed
```

输入（未要求校验）：

```text
ArtifactRequest
├─ source: ArtifactSource::parse("/fake/artifacts/qwen-4b_fake.gguf").unwrap()
└─ expected_digest: None
```

输出：

```text
PreparedArtifact
├─ local_path: "/fake/artifacts/qwen-4b_fake.gguf"
└─ verification_status: ArtifactVerificationStatus::NotRequired
```

示例中的路径统一使用 POSIX 写法，实际输出的 `local_path` 是当前部署系统的绝对路径（Windows 上带盘符与反斜杠分隔符）。

校验不一致不是错误，而是正常的业务结果，返回 `Ok(PreparedArtifact)`，其中 `verification_status` 为 `Failed`；未要求校验时返回 `NotRequired`。只有来源不存在、不可读或网络下载失败等基础错误才返回 `Err(ArtifactPrepareError)`。

错误输出（本地路径不存在或下载失败）：

```text
ArtifactPrepareError::PrepareFailed(
    "source file not found"
)
```

来源解析阶段的失败输出：

```text
ArtifactSourceError::Empty
ArtifactSourceError::UnsupportedScheme("oci")
ArtifactSourceError::InvalidFileUrl("file://host/share/model.gguf")
ArtifactSourceError::InvalidFilePath("models/\0model.gguf")
```

摘要解析阶段的失败输出：

```text
DigestError::MissingAlgorithm
DigestError::UnsupportedAlgorithm("sha3")
DigestError::BadLength { expected: 64, actual: 7 }
DigestError::NotHex
```

失败时不得返回一个被当作成功使用的 `PreparedArtifact`，也不得继续启动 Runtime 或进程。

## `PreparedArtifact` 契约

```rust
PreparedArtifact::new(
    local_path: impl AsRef<Path>,
    verification_status: ArtifactVerificationStatus,
) -> io::Result<Self>
```

```text
PreparedArtifact
├─ local_path()            // 一定是绝对路径
├─ verification_status()   // Verified / Failed / NotRequired
├─ is_verified()           // Verified 或 NotRequired 为 true，Failed 为 false
└─ Display                 // "<local_path> (verification: verified|failed|not required)"
```

构造函数会把相对路径按进程当前工作目录解析为绝对路径，使回执不随之后的工作目录变化而指向其他位置；解析失败时通过 `io::Result` 返回错误，由实现映射为 `ArtifactPrepareError::PrepareFailed`。`is_verified()` 是布尔映射而非“是否校验通过”的唯一判据，判断是否继续启动需要同时看 `verification_status()`。

## Fake 行为

```text
FakeArtifactPreparer
├─ 不做下载、不做文件 I/O、不计算摘要
├─ local_path = <系统临时目录>/burncloud/fake/artifacts/<来源字符串，/ \ : 替换为 _>
└─ verification_status 恒为 Verified
```

Fake 只证明 Contract 可以被装配，不证明真实校验已经实现。示例中的 `Failed` 与 `NotRequired` 描述 Contract 允许的三态，Fake 目前只产生 `Verified`。

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

- `local_path` 一定是绝对路径，是后续步骤可使用的本地位置 Receipt。
- `is_verified() == true` 才能继续准备流程；`NotRequired` 也映射为 `true`，`Failed` 必须阻止后续启动。
- 校验不一致返回 `Ok` + `Failed`，只有来源缺失、不可读或下载失败等基础错误才返回 `Err`。
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
