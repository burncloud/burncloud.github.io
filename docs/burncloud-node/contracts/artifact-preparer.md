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

Integration Queue 可以把这类伙伴代码归到 “Artifact Downloader”，但代码中的公开 Contract 是 `ArtifactPreparation`，真实实现是 `ArtifactPreparer`。

```text
ArtifactPreparer
├─ 从受支持的远程来源下载 Artifact
├─ 计算并校验 Artifact 摘要
└─ 返回本地 PreparedArtifact 回执
```

## 唯一职责

把受支持的远程 URL 转换成经过摘要校验的本地 `PreparedArtifact`。

```rust
async fn prepare(
    &self,
    url: Url,
    expected_digest: Digest,
) -> Result<PreparedArtifact, ArtifactPrepareError>;
```

`ArtifactPreparation` 通过 `#[async_trait]` 声明并要求实现满足 `Send + Sync`；`ArtifactPreparer` 是 Node 组合根使用的真实实现。准备的落点只有两个：`Ok(PreparedArtifact)` 或 `Err(ArtifactPrepareError)`；摘要不一致属于前者。

## 类型清单

```text
crates/platform/node/src/preparation/
├─ preparation.rs                  → 模块根，统一 re-export
├─ artifact_preparer.rs            → ArtifactPreparation / ArtifactPreparer
├─ artifact_source.rs              → ArtifactSource
├─ artifact_source_error.rs        → ArtifactSourceError
├─ artifact_verification_status.rs → ArtifactVerificationStatus
├─ prepared_artifact.rs            → PreparedArtifact
├─ artifact_prepare_error.rs       → ArtifactPrepareError
├─ digest.rs                       → Digest
├─ digest_algorithm.rs             → DigestAlgorithm
├─ digest_error.rs                 → DigestError
└─ artifact_request.rs             → ArtifactRequest（crate 内部，不对外导出）
```

`ArtifactRequest` 只把来源与期望摘要组装给实现内部使用，不属于公开 Contract；调用方只接触 `prepare(url, expected_digest)`。

## 输入与输出

```text
prepare(url: Url, expected_digest: Digest)
├─ url             // 必须是 http/https，且主机名属于受支持来源
└─ expected_digest // 必填：DigestAlgorithm + 规范化十六进制摘要
        ↓
ArtifactPreparer
        ├─ Ok(PreparedArtifact { local_path, verification_status })
        └─ Err(ArtifactPrepareError::PrepareFailed)
```

## 来源解析

`ArtifactSource` 当前只有 `Http(Url)` 一个变体：

```text
ArtifactSource 入口
├─ ArtifactSource::parse(&str) / FromStr
└─ TryFrom<&Url>
```

```text
输入
├─ 空或只含空白 ──────────────────→ ArtifactSourceError::Empty
├─ 无法被 URL 解析 ───────────────→ ArtifactSourceError::InvalidUrl
├─ http / https（大小写不敏感）───→ 继续校验主机名
├─ 其他协议（oci://、ftp:// 等）─→ ArtifactSourceError::UnsupportedScheme
└─ 主机名不在允许列表 ───────────→ ArtifactSourceError::UnsupportedHost
```

- 允许的主机名精确匹配 `modelscope.cn`、`hf-mirror.com`、`huggingface.com`、`huggingface.co`；子域名不与父域自动匹配。
- 来源校验在获取下载管理器之前完成，非法来源不会启动下载器。
- `ArtifactSource::parse` 会先去除输入首尾空白，再执行上述校验。

## 摘要

```text
DigestAlgorithm
├─ Md5     → 16 字节，32 个十六进制字符
├─ Sha1    → 20 字节，40 个十六进制字符
├─ Sha256  → 32 字节，64 个十六进制字符
├─ Sha384  → 48 字节，96 个十六进制字符
└─ Sha512  → 64 字节，128 个十六进制字符
```

算法名解析忽略大小写与连字符，`sha256`、`SHA256`、`sha-256` 与 `SHA-256` 解析为同一算法；`name()` 始终返回规范化名称。

```text
Digest 构造
├─ Digest::new(algorithm, value)          // 先校验长度，再校验字符集，通过后转小写
├─ Digest::parse("algorithm:digest") / FromStr
└─ Digest::algorithm() / value()          // 只读访问器；Display 输出规范化 algorithm:digest
```

`Digest::new` 先按算法期望长度校验（`BadLength { expected, actual }`），再校验是否全部为 ASCII 十六进制字符（`NotHex`）；`Digest::parse` 在缺少 `:` 分隔符时返回 `MissingAlgorithm`，算法名不受支持时返回 `UnsupportedAlgorithm`。摘要非法只会在解析阶段失败，不会进入准备流程。

## `PreparedArtifact` 回执

```rust
PreparedArtifact::new(
    local_path: impl AsRef<Path>,
    verification_status: ArtifactVerificationStatus,
) -> io::Result<Self>
```

```text
PreparedArtifact
├─ local_path()            // Verified 时一定是绝对路径；Failed 时为空
├─ verification_status()   // Verified / Failed
├─ is_verified()           // 仅 Verified 为 true
└─ Display                 // "<local_path> (verification: verified|failed)"
```

回执不变量：

- `Verified` 必须携带非空路径；相对路径按进程当前工作目录转换为绝对路径。
- `Failed` 必须携带空路径，任何非空路径都会被构造函数拒绝。
- `ArtifactVerificationStatus` 只有 `Verified` 与 `Failed`；摘要校验是强制步骤，不存在 “未要求校验” 状态。

## 具体示例

输入（下载并校验成功）：

```text
prepare(
  url = Url::parse(
      "https://modelscope.cn/models/AI-ModelScope/bge-small-zh-v1.5/resolve/master/model.safetensors"
  )?,
  expected_digest = Digest::parse(
      "sha256:354763b9b1357bc9c44f62c6be2276321081ed2567773608c0d0785b61d5a026"
  )?,
)
```

输出：

```text
Ok(PreparedArtifact {
    local_path: <绝对路径>/models/<下载文件>,
    verification_status: ArtifactVerificationStatus::Verified,
})
```

输入（两次下载校验均不一致）：

```text
prepare(
  url = Url::parse(
      "https://modelscope.cn/models/AI-ModelScope/bge-small-en-v1.5/resolve/master/model.safetensors"
  )?,
  expected_digest = Digest::parse(
      "sha256:0000000000000000000000000000000000000000000000000000000000000000"
  )?,
)
```

输出：

```text
Ok(PreparedArtifact {
    local_path: "",
    verification_status: ArtifactVerificationStatus::Failed,
})
```

摘要不一致不是错误，而是正常业务结果：第一次校验失败会删除下载文件并重新下载校验一次；第二次仍失败则删除文件，返回 `Ok(PreparedArtifact)` 且 `local_path` 为空。不会进行第三次尝试。

错误输出（来源被拒绝）：

```text
ArtifactPrepareError::PrepareFailed(
    "unsupported artifact source host: example.com"
)
```

错误输出（下载管理器启动、下载或文件读写失败）：

```text
ArtifactPrepareError::PrepareFailed("...")
```

来源解析阶段的失败输出：

```text
ArtifactSourceError::Empty
ArtifactSourceError::InvalidUrl("...")
ArtifactSourceError::UnsupportedScheme("oci")
ArtifactSourceError::UnsupportedHost("example.com")
```

摘要解析阶段的失败输出：

```text
DigestError::MissingAlgorithm
DigestError::UnsupportedAlgorithm("sha3")
DigestError::BadLength { expected: 64, actual: 7 }
DigestError::NotHex
```

`Err(ArtifactPrepareError::PrepareFailed)` 只用于来源被拒绝、下载管理器启动失败、下载失败以及文件读取或删除失败；摘要不匹配始终以 `Failed` 回执表达。失败时不得返回一个被当作成功使用的 `PreparedArtifact`，也不得继续启动 Runtime 或进程。

## 下载器生命周期

```text
ArtifactPreparer::new()
├─ 初始 ref_count = 0，无 DownloadManager
├─ 首个 prepare 请求启动 DownloadManager（ref_count = 1）
├─ 并发请求复用同一个 DownloadManager 并递增引用计数
└─ 最后一个请求释放后 ref_count = 0，DownloadManager 被丢弃并停止
```

下载按 `models` 类别落盘，返回路径必须为非空绝对路径，否则准备失败。校验以 64 KiB 缓冲区流式读取文件并计算摘要。

## Fake 行为

```text
FakeArtifactPreparer
├─ 不做下载、不做文件 I/O、不计算摘要
├─ local_path = <系统临时目录>/burncloud/fake/artifacts/<来源字符串，/ \ : 替换为 _>
└─ verification_status 恒为 Verified
```

Fake 只证明 Contract 可以被装配，不证明真实校验已经实现。

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

- 只有 `verification_status == Verified` 时 `local_path` 才非空，它是后续步骤可使用的本地位置 Receipt。
- `is_verified()` 为 `true` 才能继续准备流程。
- 摘要不一致返回 `Ok` + `Failed` + 空路径；只有来源被拒绝、下载失败或文件读写失败才返回 `Err`。
- 失败回执不能携带下载路径；未通过校验的下载文件在返回前已被删除。
- 下载、缓存、重试与校验方式属于实现内部，不进入 Orchestrator。

## BDD 边界

```gherkin
Scenario: Artifact cannot be verified
  When ArtifactPreparer prepares the request
  Then it returns an error or a Failed receipt with an empty local path
  And RuntimePreparer is not treated as proof that the artifact is valid
  And no process is started
```

## 停止条件

如果需要修改模型选择、Runtime、进程或路由才能完成 Artifact 准备，立即停止并拆分为其他 Owner 的任务。
