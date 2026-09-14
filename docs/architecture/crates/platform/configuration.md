---
title: "Configuration 规则"
slug: /architecture/crates/platform/configuration/
sidebar_label: "Configuration"
---

# `crates/platform/configuration` 规则

本规则适用于 `crates/platform/configuration/` 以及它直接拥有的实现文件。

继承：

- [基础规则](/architecture/foundation/)
- [Crates 目录规则](/architecture/crates/)
- [Platform 总体规则](/architecture/crates/platform/)
- [Rust 通用规则](/architecture/reusable-rules/rust/)

> **一句话边界：Platform Configuration 负责“从哪里读取、怎样合并、怎样校验技术配置”，业务领域负责“配置代表什么业务规则”。**

Configuration 是配置输入的技术入口，不是所有 `Config` 类型的收容所。

## 1. Owner 与职责

### Owner

- 主要 Owner：Platform Owner。
- 安全审核：Security Owner。
- 业务配置 Owner：仍然是定义该业务规则的领域，例如 Traffic、Commerce 或 Supply。
- 环境变量、配置文件格式、优先级或密钥处理变化，必须由 Platform Owner 审核。

### 负责

`platform/configuration` 只负责通用配置技术能力：

- 从环境变量、配置文件和启动参数读取原始值；
- 按公开且固定的优先级合并不同来源；
- 解析字符串、数字、布尔值、地址、路径和持续时间；
- 校验平台级必填项、格式和安全约束；
- 区分缺失、格式错误、冲突和来源不可用；
- 将已校验的技术配置交给程序装配层；
- 隐藏 dotenv、文件解析器等具体实现；
- 提供不泄露敏感值的配置来源摘要和错误信息。

## 2. 禁止职责与配置归属

`platform/configuration` 不拥有价格、余额、权限、路由、供应商、告警策略等业务真相。

明确禁止：

- 把所有名字带 `Config` 的类型迁入 Platform；
- 决定价格同步频率是否符合 Commerce 规则；
- 决定某个 Provider、Model 或 Channel 是否可用；
- 决定路由权重、重试次数、熔断阈值或限流策略；
- 决定 Tenant 能否使用某项能力；
- 在读取配置时访问业务 Repository；
- 用环境变量绕过授权、计费、审计或合规规则；
- 给敏感配置提供可用于生产的弱默认值；
- 在日志、错误、Debug 或序列化结果中暴露密钥；
- 运行时静默修改已经生效的配置。

配置归属按“谁解释它的业务含义”判断：

| 配置内容 | Owner | Configuration 的职责 |
|---|---|---|
| 监听地址、日志目录、连接超时 | Platform | 读取、解析和校验 |
| JWT 密钥、内部服务密钥 | Identity / Trust | 安全读取并交给 Owner |
| Provider API key、区域、模型能力 | Supply | 安全读取或引用，不解释业务状态 |
| 路由权重、重试、熔断、限流 | Traffic | 只解析基础类型，不决定策略 |
| 价格同步、币种、计费精度 | Commerce | 不提供业务默认值 |
| 告警阈值和通知规则 | 对应 Operations/Trust Owner | 只提供技术输入能力 |
| 配置来源、解析器状态 | Platform | Platform 自有运行状态 |

## 3. 公开契约

公开契约必须描述配置技术语义，不暴露具体来源库。允许公开的最小概念：

- `ConfigSource`：环境变量、文件或启动参数等来源类别；
- `ConfigKey`：经过声明和校验的稳定配置键；
- `ConfigValue`：只在解析器内部短暂存在的原始值；
- `ConfigError`：缺失、无效、冲突、不可读和不安全；
- `ConfigLoader`：按固定优先级加载原始配置；
- `SecretString`：禁止明文 Debug 和 Display 的敏感值包装；
- `RuntimeConfig`：仅包含跨组件装配所需的平台级技术配置。

必须满足：

1. 来源优先级固定、可测试、可文档化；
2. 缺失与空字符串必须区分；
3. 无效值必须失败，不能静默换成默认值；
4. 敏感值不得实现明文 `Debug`、`Display` 或 `Serialize`；
5. dotenv、clap、serde 格式类型不得泄露到公开 API；
6. 业务领域配置由对应领域定义，Configuration 只提供加载能力；
7. 所有公开导出必须在 `lib.rs` 中逐项列出，禁止 glob re-export；
8. 配置快照创建后默认不可变；运行时刷新必须是独立契约。

推荐的技术契约形状：

```rust
use std::{collections::BTreeMap, fmt, net::SocketAddr, path::PathBuf};

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum ConfigSource {
    File,
    Environment,
    CommandLine,
}

#[derive(Clone, Debug, Eq, PartialEq)]
pub struct SecretString(String);

impl SecretString {
    pub fn expose(&self) -> &str {
        &self.0
    }
}

impl fmt::Debug for SecretString {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str("SecretString([REDACTED])")
    }
}

#[derive(Clone, Debug)]
pub struct RuntimeConfig {
    pub listen_addr: SocketAddr,
    pub log_dir: PathBuf,
    pub internal_secret: SecretString,
}

#[derive(Debug, thiserror::Error)]
pub enum ConfigError {
    #[error("required configuration is missing: {key}")]
    Missing { key: &'static str },
    #[error("configuration has an invalid value: {key}")]
    Invalid { key: &'static str },
    #[error("configuration sources conflict: {key}")]
    Conflict { key: &'static str },
    #[error("configuration source is unreadable")]
    SourceUnavailable,
    #[error("configuration violates a security requirement: {key}")]
    Insecure { key: &'static str },
}

pub trait ConfigLoader {
    fn load(
        &self,
        args: &BTreeMap<String, String>,
    ) -> Result<RuntimeConfig, ConfigError>;
}
```

以上名称可以在实现前调整，但“来源明确、校验后不可变、密钥默认不可见”的语义不能被削弱。

## 4. 依赖规则

### 可以依赖

- Rust 标准库；
- workspace 统一版本的配置文件解析库；
- workspace 统一版本的序列化库；
- 路径、URL、地址和持续时间等基础解析库；
- Platform Observability 的公开契约，但初始化时必须避免循环依赖；
- 确有必要且通过 Kernel 准入的最小稳定类型。

### 禁止依赖

`platform/configuration` 禁止依赖：

- `identity/**`；
- `supply/**`；
- `traffic/**`；
- `commerce/**`；
- `trust/**` 的业务实现；
- `interfaces/**` 的 HTTP、UI 或 CLI DTO；
- 任何业务 Service 或 Repository；
- Database row 或 ORM entity；
- Router、Billing、Provider 的具体实现。

领域可以依赖 Configuration 的通用读取契约，但 Configuration 不能反向理解领域配置。

正确依赖方向：

```text
Environment / File / CLI
           ↓
Platform Configuration
           ↓
Application composition
           ↓
Domain-owned config validation and service construction
```

错误依赖方向：

```text
Platform Configuration → BillingService
Platform Configuration → ChannelRepository
Platform Configuration → Router policy
```

## 5. 目录与文件结构

只有出现真实共享职责时才创建 crate。初始结构不得超过：

```text
crates/platform/configuration/
├── Cargo.toml
└── src/
    ├── lib.rs
    ├── error.rs
    ├── key.rs
    ├── loader.rs
    ├── secret.rs
    └── source/
        ├── mod.rs
        ├── environment.rs
        └── file.rs
```

| 文件 | 唯一职责 |
|---|---|
| `lib.rs` | crate 说明和逐项公开导出 |
| `error.rs` | 配置技术错误，不包含敏感值 |
| `key.rs` | 稳定配置键及其元数据 |
| `loader.rs` | 来源优先级、合并与平台级装配 |
| `secret.rs` | 敏感值包装和脱敏行为 |
| `source/environment.rs` | 环境变量读取 adapter |
| `source/file.rs` | 配置文件读取 adapter |

如果第一版只需要环境变量，不得预建 `file.rs` 或 `source/` 层级。目录应按真实职责从最小结构开始。

禁止建立业务收容文件：

```text
pricing.rs
billing.rs
provider.rs
channel.rs
routing.rs
tenant.rs
auth_policy.rs
feature_flags.rs
utils.rs
common.rs
manager.rs
```

## 6. 代码写法

### 加载与优先级

- 所有来源必须按同一条公开优先级规则合并；
- 推荐优先级为“启动参数 > 环境变量 > 配置文件 > 安全默认值”；
- 采用其他顺序必须在公开契约中明确，并建立独立变更 Issue；
- 同一来源重复声明且值冲突时必须报错；
- Library 的 `Default`、构造函数和 getter 不得偷偷读取环境变量；
- 环境变量只能在入口或 Configuration adapter 中读取一次。

### 默认值

- 只有不会削弱安全或改变业务结果的技术项才能有默认值；
- 监听端口、日志保留数量等技术默认值必须集中声明；
- JWT secret、数据库密码、Provider key、内部服务密钥不得有生产弱默认值；
- 缺失必填密钥必须阻止启动；
- 测试默认值只能存在于测试 fixture 中。

### 校验

- 原始字符串必须先解析，再构造不可变配置；
- 端口、大小、持续时间和重试次数必须检查上下界；
- 文件路径必须明确是输入文件、输出目录还是可执行文件；
- URL 必须校验 scheme，敏感连接必须拒绝不安全协议；
- 领域业务约束由领域构造函数继续校验，不能假装由 Platform 完成。

### 错误

- missing、empty、invalid、conflict、unreadable、insecure 必须区分；
- 禁止在运行时配置路径使用 `unwrap` 或 `expect`；
- 错误可以包含稳定 key 名，不能包含原始值；
- 底层解析错误可作为内部 source，但公开文案必须脱敏；
- 多个错误同时存在时，应一次返回可安全展示的完整错误集合或明确返回第一个错误，不能行为不确定。

### 日志

允许：

```rust
tracing::info!(
    source = "environment",
    key = "BURNCLOUD_DATABASE_URL",
    status = "present",
    "configuration loaded"
);
```

禁止：

```rust
tracing::info!(database_url = %database_url, "configuration loaded");
tracing::debug!(jwt_secret = %jwt_secret, "using secret");
```

日志只能记录安全 key、来源、是否存在、是否使用默认值和错误类别。不得记录密码、Token、API key、cookie secret、私钥或带凭据的 URL。

### 敏感值

- 必须使用不显示明文的包装类型；
- 暴露明文必须通过名字明确的方法，例如 `expose()`；
- 敏感值不得 Clone 到不必要的长期对象；
- 配置快照不得通过普通 API 返回给 UI 或 HTTP；
- 管理接口只能返回“已配置/未配置”和安全元数据。

### 运行时刷新

- 默认不支持隐式热更新；
- 需要刷新时必须单独定义版本、原子替换、失败回滚和审计规则；
- 读取到新配置但校验失败时，旧配置继续生效；
- 业务策略热更新必须由对应 Domain Owner 定义。

## 7. 使用的可复用规则

本 crate 必须使用：

- Rust 通用规则；
- 基础错误处理规则；
- 基础日志规则；
- 安全底线；
- 变更原则。

只有真实发生对应行为时才追加：

- Migration 规则：配置 key、文件格式、优先级或默认值变化；
- Background Job 规则：配置监听或定时刷新；
- Database 规则：仅在配置来源确实是平台配置存储时使用，不能因此读取业务表；
- HTTP API 规则：仅用于安全的管理查询接口，不能返回原始配置。

不得引用与本 crate 无关的 UI、P2P、Download、Upload 或 Streaming 规则。

## 8. 独有测试要求

本 crate 只承担 Configuration 技术边界测试。

### 单元测试

必须覆盖：

- 每一种来源的读取；
- 来源优先级；
- 缺失与空值；
- 合法和非法布尔值、数字、地址、URL、路径与持续时间；
- 上下界；
- 冲突值；
- 默认值只用于允许的技术配置；
- 密钥的 `Debug` 和错误信息不泄露明文；
- 未声明 key 的处理方式固定。

### 集成测试

存在多个来源时必须覆盖：

- 文件值被环境变量覆盖；
- 环境变量被启动参数覆盖；
- 文件不存在、无权限或内容损坏；
- 必填密钥缺失时启动失败；
- 重复加载得到相同不可变快照；
- 并行测试之间不共享进程环境变量状态；
- 日志和错误输出不包含测试密钥。

### 领域测试

下列内容由对应 Domain Owner 测试，不放进 Platform Configuration：

- 路由权重是否合法；
- 价格精度与币种规则；
- Provider 能力和区域组合；
- Tenant 功能权限；
- 告警阈值是否符合业务要求。

## 9. 完整正确示例

下面示例展示入口读取技术配置，再把 Traffic 自己的策略原始值交给 Traffic 解析。Platform 不解释路由策略。

```rust
use std::{collections::BTreeMap, net::SocketAddr, path::PathBuf};

fn required(
    values: &BTreeMap<String, String>,
    key: &'static str,
) -> Result<String, ConfigError> {
    match values.get(key).map(String::trim) {
        Some("") | None => Err(ConfigError::Missing { key }),
        Some(value) => Ok(value.to_owned()),
    }
}

fn build_runtime_config(
    values: &BTreeMap<String, String>,
) -> Result<RuntimeConfig, ConfigError> {
    let listen_addr = values
        .get("BURNCLOUD_LISTEN_ADDR")
        .map(String::as_str)
        .unwrap_or("127.0.0.1:3000")
        .parse::<SocketAddr>()
        .map_err(|_| ConfigError::Invalid {
            key: "BURNCLOUD_LISTEN_ADDR",
        })?;

    let log_dir = values
        .get("LOG_DIR")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("./logs"));

    let internal_secret = SecretString(required(
        values,
        "BURNCLOUD_INTERNAL_SECRET",
    )?);

    Ok(RuntimeConfig {
        listen_addr,
        log_dir,
        internal_secret,
    })
}

fn start(
    platform_values: &BTreeMap<String, String>,
    traffic_policy_json: &str,
) -> Result<(), StartupError> {
    let runtime = build_runtime_config(platform_values)?;

    // 业务规则仍由 Traffic 自己定义和校验。
    let traffic_policy = traffic::RoutingPolicy::from_json(
        traffic_policy_json,
    )?;

    application::run(runtime, traffic_policy)
}
```

这里的职责是：

1. Configuration 读取并校验监听地址、日志目录和敏感值存在性；
2. `SecretString` 的调试输出永远脱敏；
3. Traffic 定义并验证自己的 `RoutingPolicy`；
4. Application composition 负责把两者装配起来；
5. 没有模块在构造函数中再次读取环境变量。

## 10. 完整错误示例

### 错误：把业务策略全部放进 Platform

```rust
// crates/platform/configuration/src/lib.rs
pub struct GlobalConfig {
    pub provider_api_key: String,
    pub model_price_nano: i64,
    pub routing_weight: u32,
    pub tenant_can_overdraft: bool,
}
```

错因：一个 Platform 类型同时拥有 Supply、Commerce、Traffic 和 Identity 的业务规则。

### 错误：构造函数偷偷读取环境变量

```rust
impl BillingService {
    pub fn new() -> Self {
        let currency = std::env::var("BILLING_CURRENCY")
            .unwrap_or_else(|_| "USD".to_owned());
        Self { currency }
    }
}
```

错因：依赖不可见、无法稳定测试，并且用 Platform 输入替代 Commerce 的显式业务契约。

### 错误：敏感配置使用弱默认值

```rust
let jwt_secret = std::env::var("JWT_SECRET")
    .unwrap_or_else(|_| "change-me".to_owned());
```

错因：生产环境配置错误时仍会启动，形成可预测密钥。

### 错误：日志输出完整配置

```rust
tracing::info!(?config, "startup configuration");
```

错因：`config` 可能包含数据库密码、内部密钥和 Provider API key。

### 错误：无效值静默回退

```rust
let port = raw_port.parse::<u16>().unwrap_or(3000);
```

错因：操作者明确写错的值被伪装成默认配置，故障原因不可见。

## 变更规则

下列变化必须建立独立 Issue：

- 新增、删除或重命名公开配置 key；
- 改变来源优先级；
- 改变默认值；
- 改变配置文件格式或版本；
- 把普通值改为敏感值，或反向改变；
- 新增运行时热更新；
- 新增远程配置来源；
- 新增管理查询或修改接口；
- 改变错误语义或启动失败条件。

配置规则、目录迁移、crate/package 重命名和运行默认值变化必须分别提交，不能在一个 Issue 中混做。

## Stop Conditions

出现以下任一情况，停止当前 Issue 并拆分：

- 无法确认配置的业务 Owner；
- 需要让 Platform 理解 Billing、Provider、Tenant 或 Routing 业务规则；
- 需要改变现有环境变量、文件格式、优先级或默认值；
- 需要修改认证、计费、路由或供应商行为；
- 需要访问业务数据库才能读取配置；
- 需要把敏感配置暴露给 HTTP、UI 或日志；
- 需要同时迁移多个领域才能通过编译；
- 测试失败原因超出 Configuration 技术边界。

## 自动检查方法

当前阶段只定义文档，不新增 Harness 或 YAML。实现阶段至少应通过仓库已有命令检查：

```bash
cargo fmt --check
cargo check --workspace
cargo test -p burncloud-platform-configuration
```

并使用静态搜索确认：

```bash
rg -n 'std::env::var' crates --glob '*.rs'
rg -n 'JWT_SECRET|MASTER_KEY|API_KEY|DATABASE_URL' crates --glob '*.rs'
rg -n 'tracing::.*(secret|token|password|api_key|database_url)' crates --glob '*.rs'
```

搜索结果不是自动判错；它用于要求 Reviewer 逐项确认读取位置、Owner 和脱敏方式。
