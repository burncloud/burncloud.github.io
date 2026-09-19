---
title: "Kernel 规则"
slug: /architecture/crates/kernel/
description: "规定 BurnCloud Kernel 的准入条件、职责、依赖、代码写法、测试和迁移边界。"
---

# `crates/kernel` 规则

Kernel 是 BurnCloud 最底层、最小、最稳定的代码地基。它不是业务领域，也不是把暂时不知道放哪里的代码集中起来的公共目录。

> **Kernel 必须少而稳定。不能确定是否属于 Kernel 时，默认不放入 Kernel。**

继承[基础规则](../foundation.md)和 [Rust 通用规则](../reusable-rules/rust.md)。

## 1. Owner 与职责

Owner 是 Kernel Maintainer。任何新增公开类型、公开 Trait 或序列化格式，都必须由 Kernel Owner 批准。

代码进入 Kernel 必须同时满足：

1. 至少两个独立领域确实需要；
2. 没有任何自然业务 Owner；
3. 没有数据库、网络、文件、进程和 UI 副作用；
4. 不依赖其他 BurnCloud crate；
5. 语义稳定，不跟随单个业务频繁改变。

可以进入 Kernel 的候选内容包括 `Clock`、`Timestamp`、`DomainEvent`、`EventEnvelope`、`EventId`、`CorrelationId` 和 `CausationId`。“候选”不代表必须预先创建，只有出现真实需求后才能增加。

## 2. 不负责什么与业务真相

Kernel 不拥有具体业务真相，不判断用户、模型、路由、账务、权限或供应状态。

| 类型或能力 | 唯一 Owner |
|---|---|
| `UserId`、`TenantId`、Access Token | Identity |
| `ModelId`、`ProviderId`、`ChannelId` | Supply |
| `Money`、`Currency`、Invoice 状态 | Commerce |
| Route、Retry、Failover 决策 | Traffic |
| Audit、Proof、合规结论 | Trust |
| Database、Cache、日志实现 | Platform |
| HTTP、CLI、UI 类型 | Interfaces |

其他领域可以通过 Owner 的公开契约使用这些类型。“很多地方使用”不能成为移入 Kernel 的理由。

Kernel 禁止保存 Service、Repository、Handler、Adapter、数据库 Model、Migration、HTTP 类型、业务规则、密钥、Token，以及无明确语义的 `common.rs`、`utils.rs`、`helpers.rs`。

## 3. 公开契约

`lib.rs` 只能导出经过批准的最小稳定契约，内部实现默认私有。每个公开契约必须说明：

- 类型表达的唯一语义；
- 构造和解析条件；
- 不变量和错误结果；
- 序列化格式是否属于兼容承诺。

禁止建立包含全系统业务错误的巨大 `KernelError`。各领域必须拥有自己的错误类型。

## 4. 依赖规则

允许的方向是所有领域单向依赖 Kernel：

```text
Identity ─┐
Supply   ─┤
Traffic  ─┤
Commerce ─┼──► Kernel
Trust    ─┤
Platform ─┤
Interfaces┘
```

Kernel 不能反向依赖任何 BurnCloud crate。允许依赖 Rust 标准库；只有公开值类型确实需要时，才能批准少量基础库，例如 `serde`、`uuid` 或 `time`。

禁止依赖 `axum`、`reqwest`、`sqlx`、`tokio`、日志实现和任何 `burncloud-*` 业务 crate。必须通过数据库、网络、环境变量或异步 Runtime 才能工作的代码不属于 Kernel。

## 5. 禁止越界行为

下列理由一律不能作为 Kernel 准入依据：

- 暂时不知道放哪里；
- 多个 crate 都在使用；
- 将来可能复用；
- 想缩短 import 路径；
- 想把原来的 `common` 整体改名。

Kernel 不得重新定义其他领域已经拥有的类型，也不得提供绕过业务 Owner 的修改方法。

## 6. 目录和文件结构

初始结构保持最小：

```text
crates/kernel/
├── Cargo.toml
└── src/
    ├── lib.rs
    ├── clock.rs          # 有真实需要时创建
    ├── timestamp.rs      # 有真实需要时创建
    ├── event.rs          # 有真实需要时创建
    └── correlation.rs    # 有真实需要时创建
```

不要预建空目录。一个概念只有一个文件时直接使用文件；出现多个紧密相关文件后，才升级成同名子目录。

禁止创建 `kernel/utils/`、`kernel/helpers/`、`kernel/common/`、`kernel/services/`、`kernel/repositories/` 和 `kernel/adapters/`。

## 7. 代码、错误、日志与安全

Kernel 代码必须：

- 优先使用不可变值对象和强类型；
- 构造时建立不变量，不能创建半有效对象；
- 行为确定，同样输入得到同样结果；
- 默认无 `async`、无 IO、无全局可变状态；
- 默认私有，只导出真正需要的最小接口；
- 返回明确错误，不猜测、不静默修复非法输入。

Kernel 不记录运行日志，只返回结构化结果或错误，由调用方在正确上下文中记录。Kernel 不得接收、保存或输出密码、API Key、Access Token 等敏感数据。

## 8. 继承的规则

Kernel 遵守[基础规则](../foundation.md)和 [Rust 通用规则](../reusable-rules/rust.md)。

Kernel 没有 Database、HTTP、UI、Download 或 Background Job 职责，因此默认不引用这些可复用规则。出现相关需要时，必须停止并重新判断归属。

## 9. 独有测试与迁移要求

Kernel 测试只验证构造、解析、格式化、边界值、相等、排序、Hash、不变量、序列化兼容性和确定性行为。

测试不得启动数据库、HTTP Server、异步 Runtime 或真实文件系统。需要这些环境的代码不属于 Kernel。

从 `crates/common` 迁移时，必须逐个公开符号确认 Owner：

```text
有明确业务 Owner        → 移回对应领域
属于通用技术实现         → Platform
属于外部协议             → Interfaces
满足全部 Kernel 准入条件 → 才能进入 Kernel
无法确定                 → 停止迁移，由架构 Owner 决定
```

禁止把 `crates/common` 整体移动或改名成 `crates/kernel`。

Kernel 的公开类型、序列化格式和不变量属于 Protected Zone。破坏兼容性的修改必须使用独立 Issue，并明确所有下游影响。

## 10. 完整示例

### 正确示例

```rust
use std::{fmt, str::FromStr};
use uuid::Uuid;

#[derive(Clone, Copy, Debug, Eq, Hash, PartialEq)]
pub struct CorrelationId(Uuid);

impl CorrelationId {
    pub fn new() -> Self {
        Self(Uuid::new_v4())
    }
}

impl fmt::Display for CorrelationId {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        self.0.fmt(formatter)
    }
}

impl FromStr for CorrelationId {
    type Err = uuid::Error;

    fn from_str(value: &str) -> Result<Self, Self::Err> {
        Uuid::parse_str(value).map(Self)
    }
}
```

它不依赖数据库、HTTP 或业务领域，非法输入明确返回错误。

### 错误示例

```rust
pub mod helpers {
    use sqlx::PgPool;

    pub struct KernelService {
        database: PgPool,
    }

    impl KernelService {
        pub async fn can_charge_tenant(&self, tenant_id: &str) -> bool {
            true
        }
    }

    pub struct Money(pub f64);      // 应归 Commerce。
    pub struct ModelId(pub String); // 应归 Supply。
}
```

错误原因：`helpers` 没有职责含义；Kernel 依赖数据库和异步 Runtime；Kernel 决定 Commerce 业务；抢走 Supply 和 Commerce 的类型；`f64` 不能表达可靠金额不变量。

## 准入判断与停止条件

向 Kernel 增加代码前必须回答：

> 如果删除七个上层领域以及所有数据库、网络和 UI，这段代码是否仍有完整、稳定、独立的意义？

答案不是明确的“是”，就禁止进入 Kernel。

出现以下情况必须停止当前 Issue：

- 需要新增其他 BurnCloud crate 依赖；
- 需要访问数据库、网络、文件、进程或环境变量；
- 类型已有明确领域 Owner；
- 只是为了复用、方便导入或暂存代码；
- 修改公开格式或不变量，但没有获得 Kernel Owner 批准。

> **Kernel 越小，系统边界越清楚；Kernel 越大，所有领域越容易重新耦合。**
