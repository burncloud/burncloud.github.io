---
title: "Cache 规则"
slug: /architecture/crates/platform/cache/
sidebar_label: "Cache"
---

# `crates/platform/cache` 规则

本规则适用于 `crates/platform/cache/` 以及它直接拥有的实现文件。

继承：

- [基础规则](/architecture/foundation/)
- [Crates 目录规则](/architecture/crates/)
- [Platform 总体规则](/architecture/crates/platform/)
- [Rust 通用规则](/architecture/reusable-rules/rust/)

> **一句话边界：Platform Cache 负责“怎样缓存”，数据所属领域负责“缓存什么、何时失效、缓存失败后怎么办”。**

Cache 永远是业务数据的副本，不能成为新的业务真相来源。

## 1. Owner 与职责

### Owner

- 主要 Owner：Platform Owner。
- 被缓存数据的 Owner：仍然是原业务领域，例如 Identity、Supply、Traffic 或 Commerce。
- 涉及业务缓存策略的变更，必须由 Platform Owner 和对应 Domain Owner 共同审核。

### 负责

`platform/cache` 只负责通用缓存技术能力：

- 建立、维护和关闭缓存后端连接；
- 执行读取、写入、删除和精确失效；
- 执行调用方给出的 TTL；
- 提供带版本和命名空间的 key；
- 区分 hit、miss、unavailable 和 invalid data；
- 执行超时、连接恢复和资源释放；
- 提供不泄露业务数据的健康状态、指标和日志；
- 隐藏 Redis 等具体后端类型。

## 2. 禁止职责与数据归属

`platform/cache` 不拥有 User、Token、Channel、Provider、Price、Quota、Balance、Route 等业务真相。

明确禁止：

- 决定用户是否有权限；
- 决定 Token 是否有效；
- 决定 Channel 是否可用或应被路由；
- 决定余额是否足够；
- 决定价格、账单或扣费结果；
- 直接访问数据库进行回源；
- 把 Redis 中的数据当作唯一数据；
- 在 Platform 中定义跨域的 `CachedUser`、`CachedToken`、`CachedChannel`；
- 缓存明文密码、明文访问 Token、明文 Provider API key；
- 因缓存命中而跳过业务授权或业务校验。

数据归属不因复制到缓存而改变：

| 缓存内容 | 业务 Owner | Cache 的身份 |
|---|---|---|
| Token 查询结果 | Identity | 可丢失副本 |
| Channel 投影 | Supply | 可丢失副本 |
| 路由临时状态 | Traffic | 可丢失副本 |
| Price / Balance 投影 | Commerce | 可丢失副本 |
| Cache 连接和运行指标 | Platform | Platform 自有运行状态 |

## 3. 公开契约

公开接口必须与具体缓存后端无关。允许公开的最小概念：

- `CacheStore`：字节级读取、写入和精确删除；
- `CacheKey`：受校验的 namespace、version、scope 和 digest；
- `CacheTtl`：非零、有限的过期时间；
- `CacheError`：区分不可用、超时、编码错误和后端错误；
- `CacheStats`：只包含安全的运行统计。

必须满足：

1. miss 返回 `Ok(None)`；
2. 后端不可用返回明确错误，不能伪装成 miss；
3. fail-open 或 fail-closed 由业务调用方决定；
4. Redis client、connection、command 和 URL 类型不得出现在公开 API；
5. 业务 DTO、业务 key 规则和失效时机由数据 Owner 定义；
6. `clear_all` 不得作为普通公开业务接口；
7. 所有公开导出必须在 `lib.rs` 中逐项列出，禁止 glob re-export。

推荐的技术契约形状：

```rust
use async_trait::async_trait;
use std::{num::NonZeroU64, time::Duration};

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct CacheKey(String);

impl CacheKey {
    pub fn new(
        namespace: &str,
        version: u16,
        scope: &str,
        digest: &str,
    ) -> Result<Self, CacheError> {
        if namespace.is_empty() || scope.is_empty() || digest.is_empty() {
            return Err(CacheError::InvalidKey);
        }

        Ok(Self(format!(
            "bc:{namespace}:v{version}:{scope}:{digest}"
        )))
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

#[derive(Clone, Copy, Debug)]
pub struct CacheTtl(NonZeroU64);

impl CacheTtl {
    pub fn seconds(seconds: NonZeroU64) -> Self {
        Self(seconds)
    }

    pub fn as_duration(self) -> Duration {
        Duration::from_secs(self.0.get())
    }
}

#[derive(Debug, thiserror::Error)]
pub enum CacheError {
    #[error("cache is unavailable")]
    Unavailable,
    #[error("cache request timed out")]
    Timeout,
    #[error("cache key is invalid")]
    InvalidKey,
    #[error("cache data is invalid")]
    InvalidData,
    #[error("cache backend operation failed")]
    Backend,
}

#[async_trait]
pub trait CacheStore: Send + Sync {
    async fn get(&self, key: &CacheKey) -> Result<Option<Vec<u8>>, CacheError>;

    async fn put(
        &self,
        key: &CacheKey,
        value: &[u8],
        ttl: CacheTtl,
    ) -> Result<(), CacheError>;

    async fn remove(&self, key: &CacheKey) -> Result<(), CacheError>;
}
```

以上名称可以在实现前调整，但边界语义不能被削弱。

## 4. 依赖规则

### 可以依赖

- Rust 标准库；
- workspace 统一版本的异步运行时；
- workspace 统一版本的序列化库；
- Redis 等缓存后端 client；
- Platform Configuration 的公开契约；
- Platform Observability 的公开契约；
- 确有必要且通过 Kernel 准入的最小稳定类型。

### 禁止依赖

`platform/cache` 禁止依赖：

- `identity/**`；
- `supply/**`；
- `traffic/**`；
- `commerce/**`；
- `trust/**`；
- `interfaces/**`；
- 任何领域 Repository；
- `database` 或 SQL row 类型；
- HTTP Request / Response DTO；
- UI、CLI 或 Server 入口代码。

业务领域的核心代码也不得直接依赖 Redis 类型。需要缓存时，由对应领域定义缓存投影和策略，在该领域的 adapter 或应用装配层中组合 `CacheStore`。

正确依赖方向：

```text
Domain cache policy / DTO
          ↓
Application composition
          ↓
Platform Cache public contract
          ↓
Private Redis adapter
```

错误依赖方向：

```text
Platform Cache → UserRepository
Platform Cache → BillingService
Platform Cache → Router
```

## 5. 目录与文件结构

只有出现真实职责时才创建文件。初始结构不得超过：

```text
crates/platform/cache/
├── Cargo.toml
└── src/
    ├── lib.rs
    ├── config.rs
    ├── error.rs
    ├── store.rs
    └── redis.rs
```

| 文件 | 唯一职责 |
|---|---|
| `lib.rs` | crate 说明和逐项公开导出 |
| `config.rs` | 接收已经解析好的缓存连接配置和技术默认值 |
| `error.rs` | Cache 技术错误 |
| `store.rs` | 后端无关的 key、TTL 和 store 契约 |
| `redis.rs` | 私有 Redis adapter、连接与命令实现 |

禁止为了“以后可能用”预建：

```text
token.rs
user.rs
channel.rs
price.rs
quota.rs
billing.rs
router.rs
utils.rs
common.rs
manager.rs
```

当单个文件已经出现第二个独立技术职责，并且拆分后仍由同一个 Owner 负责时，才允许继续向下拆。

## 6. 代码写法

### 配置

- Library 不得在 `Default` 或构造函数里直接读取环境变量；
- 环境变量由 Platform Configuration 或程序入口解析后传入；
- 缓存默认关闭或启用必须由部署配置明确决定；
- 连接 URL 属于敏感配置，禁止原样输出。

### 错误

- miss、disabled、timeout、unavailable、invalid data 必须区分；
- 运行时缓存错误禁止使用 `unwrap`、`expect`；
- 后端原始错误可作为内部 source，但公开错误不得泄露凭据或完整连接地址；
- Cache 不替业务决定错误是否可以忽略。

### 日志

允许：

```rust
tracing::warn!(
    backend = "redis",
    operation = "get",
    error_kind = "timeout",
    "cache operation failed"
);
```

禁止：

```rust
tracing::info!("Connecting to Redis at {}", redis_url);
tracing::debug!(token = raw_token, "cache lookup");
tracing::debug!(api_key = provider_key, "cache write");
```

日志中只能记录安全的 backend、operation、namespace、耗时和错误类别。不得记录 value、原始 key、Redis 密码、Token 或 API key。

### Key

- 必须包含稳定 namespace；
- 必须包含格式 version；
- 多租户数据必须包含不可混淆的 scope；
- 认证凭据只能使用密码学摘要，不能把原文放进 key；
- 禁止把用户输入直接拼接为 Redis key；
- key 格式变更属于兼容性变更，必须有迁移或双读计划。

### 超时和降级

- 每次外部缓存 I/O 必须有明确超时；
- Cache 不可用时不得无限重试；
- 重试必须有次数上限和退避；
- fail-open 只能回到真实数据源，不能返回伪造业务数据；
- 权限、余额和扣费等高风险场景是否允许 fail-open，由对应 Domain Owner 决定。

## 7. 使用的可复用规则

本 crate 必须使用：

- Rust 通用规则；
- 基础错误处理规则；
- 基础日志规则；
- 安全底线；
- 变更原则。

只有真实发生对应行为时才追加：

- Background Job 规则：后台刷新、清理或重连任务；
- Database 规则：仅用于确认 Cache 不能代替数据库，不能因此增加数据库依赖；
- Migration 规则：Redis key、value 格式或 namespace 发生兼容迁移时。

不得引用与本 crate 无关的 UI、P2P、Download、Upload 规则。

## 8. 独有测试要求

本 crate 只承担 Cache 自己的测试。

### 单元测试

必须覆盖：

- 合法和非法 key；
- namespace、version、scope 隔离；
- TTL 不允许为零；
- miss 与 unavailable 不混淆；
- 错误转换不泄露敏感信息；
- disabled 实现不执行后端 I/O。

### Adapter 集成测试

存在 Redis adapter 时必须覆盖：

- put → get 命中；
- 未写入时 miss；
- TTL 到期；
- 精确 remove；
- 不同 Tenant / scope 不串数据；
- 后端连接失败；
- 请求超时；
- 断线后的有限恢复；
- 并发读写；
- 不兼容 value 被识别为 invalid data。

### 领域集成测试

由缓存数据的 Domain Owner 定义并放在该领域：

- 回源逻辑；
- 写入和失效时机；
- fail-open / fail-closed；
- 权限、余额、价格、Channel 状态的正确性。

不得为了测试 Platform Cache 而把真实 User、Billing、Router 或 Channel 模块作为依赖。

## 9. 完整正确示例

下面的例子展示 Cache 只保存 Identity 提供的投影，不决定 Token 是否有效。示例中的 `token_digest` 必须由安全哈希生成，不能传入原始 Token。

```rust
use serde::{Deserialize, Serialize};
use std::{num::NonZeroU64, sync::Arc};

#[derive(Debug, Serialize, Deserialize)]
struct TokenCacheEntry {
    user_id: String,
    status_version: u64,
}

struct IdentityTokenCache {
    store: Arc<dyn CacheStore>,
}

impl IdentityTokenCache {
    async fn find(
        &self,
        token_digest: &str,
    ) -> Result<Option<TokenCacheEntry>, CacheError> {
        let key = CacheKey::new(
            "identity.token",
            1,
            "global",
            token_digest,
        )?;

        let Some(bytes) = self.store.get(&key).await? else {
            return Ok(None);
        };

        serde_json::from_slice(&bytes)
            .map(Some)
            .map_err(|_| CacheError::InvalidData)
    }

    async fn save(
        &self,
        token_digest: &str,
        entry: &TokenCacheEntry,
    ) -> Result<(), CacheError> {
        let key = CacheKey::new(
            "identity.token",
            1,
            "global",
            token_digest,
        )?;
        let value = serde_json::to_vec(entry)
            .map_err(|_| CacheError::InvalidData)?;
        let ttl = CacheTtl::seconds(
            NonZeroU64::new(300).expect("300 is non-zero"),
        );

        self.store.put(&key, &value, ttl).await
    }
}
```

这里的职责是：

1. Identity 定义 `TokenCacheEntry`；
2. Identity 决定 Token 状态是否仍需查询真实数据；
3. Platform 执行通用 get、put、remove；
4. miss 或 Cache 故障后，由上层 Identity 流程决定是否回源；
5. Cache 不能自行批准访问。

常量构造中的 `expect` 只证明编译期固定值非零；运行时缓存错误仍然禁止 `unwrap` 和 `expect`。

## 10. 完整错误示例

### 错误：Platform 拥有业务 DTO

```rust
// crates/platform/cache/src/service.rs
pub struct CachedToken {
    pub raw_token: String,
    pub user_balance: i64,
    pub traffic_class: String,
}
```

错因：一个 Platform 类型同时拥有 Identity、Commerce 和 Traffic 数据，并泄露原始 Token。

### 错误：Cache 直接回源数据库

```rust
pub async fn get_user(&self, id: &str) -> Result<User, CacheError> {
    if let Some(user) = self.redis.get(id).await? {
        return Ok(user);
    }

    self.user_repository.find(id).await
}
```

错因：Platform 依赖业务 Repository，并开始决定 User 的读取流程。

### 错误：把不可用当成未命中

```rust
let cached = redis.get(key).await.unwrap_or(None);
```

错因：连接失败被伪装成 miss，调用方无法选择正确的降级策略。

### 错误：记录连接密钥

```rust
tracing::info!("Connecting to Redis at {redis_url}");
```

错因：URL 可能包含用户名、密码和内部地址。

### 错误：暴露全库清空

```rust
pub async fn clear_all(&self) {
    redis::cmd("FLUSHDB").execute().await.unwrap();
}
```

错因：普通公开接口可以清除其他领域和 Tenant 的缓存，且运行时错误会 panic。

## 变更规则

下列变化必须建立独立 Issue，并由受影响的 Domain Owner 审核：

- key namespace 或 version 变化；
- value 序列化格式变化；
- TTL 策略变化；
- fail-open / fail-closed 变化；
- 新增敏感字段缓存；
- 新增批量删除或管理接口；
- 新增缓存后端；
- 公开错误语义变化。

目录迁移、crate/package 重命名、公开 API 变更必须分别提交，不能在一个 Issue 中混做。

## Stop Conditions

出现以下任一情况，停止当前 Issue 并拆分：

- 无法确认被缓存数据的业务 Owner；
- 需要让 Platform 理解 User、Channel、Route、Price、Balance 的业务规则；
- 需要修改公开缓存契约；
- 需要改变 Redis key 或序列化格式；
- 需要修改 Auth、Billing、Routing 或 Channel 行为；
- 需要直接读取数据库才能完成 Cache；
- 一个变更同时跨越两个业务领域；
- 测试失败原因超出 Cache 技术边界。

## 新建或迁移前检查

在创建 `crates/platform/cache` 或迁移现有 Cache 代码前，必须确认：

- [ ] Owner 和 Reviewer 已明确；
- [ ] 来源文件已经按业务 Owner 分类；
- [ ] 没有把 `CachedToken`、`CachedChannel`、`CachedQuota` 原样搬入 Platform；
- [ ] Source → Target 文件映射已写入迁移 Issue；
- [ ] Allowed、Conditional、Forbidden Paths 已明确；
- [ ] key 和 value 兼容风险已记录；
- [ ] 敏感字段已识别；
- [ ] 独有测试已列出；
- [ ] Stop Conditions 已列出；
- [ ] 第一个真实职责迁入时才创建目录。
