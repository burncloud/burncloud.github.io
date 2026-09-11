---
title: "BurnCloud 目录规则"
slug: /architecture/directory-rules/
sidebar_label: "目录规则"
description: "BurnCloud 最小目录规则 V1：领域决定归属、功能决定目录、复杂度决定层级、接口决定边界。"
---

# BurnCloud 目录规则

> **版本：V1**
>
> 本文定义 BurnCloud 仓库的最小目录规则。目标不是提前设计未来所有目录，而是建立一套足够简单、长期稳定、所有开发者都能执行的代码归属原则。

## 1. 核心原则

BurnCloud 的目录首先表达：

> **代码属于谁、负责什么、边界在哪里。**

目录优先按照业务归属组织，而不是按照 Service、Database、Controller、Repository 等技术类型组织。

四条核心规则：

> **领域决定归属。**  
> **功能决定目录。**  
> **复杂度决定层级。**  
> **接口决定边界。**

---

## 2. `crates/` 一级目录

`crates/` 第一层代表 BurnCloud 长期稳定的核心领域。

```text
crates/
├── kernel/
├── identity/
├── supply/
├── traffic/
├── commerce/
├── trust/
├── platform/
└── interfaces/
```

普通业务功能不得直接增加 `crates/` 一级目录。

### `kernel`

负责 BurnCloud 全局最小、最稳定的基础规则。

可以包括：

- 基础 ID 类型
- 时间等基础值类型
- 最小错误契约
- 极少量跨领域基础 Contract

不能包括具体的 User、Billing、Provider、Routing、Model、Pricing，也不能成为通用工具垃圾桶。

> `kernel` 必须保持极小，禁止演变为新的 `common`。

### `identity`

负责：

> **谁在使用 BurnCloud。**

典型功能：User、Account、Organization、Tenant、Authentication、API Key、Session、Authorization、Role、Permission。

```text
identity/
├── user/
├── auth/
└── permission/
```

### `supply`

负责：

> **BurnCloud 有什么资源可以提供。**

典型功能：Model、Provider、Channel、Upstream Credential、Capacity、GPU / Compute Resource、Marketplace Supply。

```text
supply/
├── model/
├── provider/
└── channel/
```

### `traffic`

负责：

> **一个请求如何进入、选择目标、执行并返回。**

典型功能：Gateway、Routing、Dispatch、Inference、Streaming、Retry、Failover、Load Balancing。

```text
traffic/
├── gateway/
├── routing/
└── inference/
```

### `commerce`

负责：

> **使用了多少、值多少钱、钱怎么结算。**

典型功能：Usage、Metering、Quota、Pricing、Billing、Ledger、Invoice、Settlement。

```text
commerce/
├── pricing/
├── billing/
└── settlement/
```

### `trust`

负责：

> **如何证明 BurnCloud 的行为可信、合规、可追溯。**

典型功能：Audit、Evidence、Attestation、Compliance、Risk、Security Governance。

```text
trust/
├── audit/
├── evidence/
└── compliance/
```

### `platform`

负责：

> **即使不知道 BurnCloud 是 AI Router，也仍然成立的通用技术能力。**

典型功能：Database Infrastructure、Storage、Cache、Networking、Messaging、Configuration、Observability、Transfer / Download、Installer / Update。

```text
platform/
├── storage/
├── cache/
├── networking/
└── lifecycle/
```

`platform` 不允许拥有 Billing、Routing、Provider 等业务规则。

### `interfaces`

负责：

> **BurnCloud 与外部世界之间的协议和入口适配。**

典型功能：HTTP、gRPC、UI、SDK、Webhook、External Events。

```text
interfaces/
├── http/
├── ui/
└── sdk/
```

`interfaces` 负责协议、参数和 DTO 转换，但不拥有核心业务。

---

## 3. 一级目录默认冻结

新增普通功能时，不允许直接在 `crates/` 下增加新的一级目录。

新增代码必须先判断：

```text
它属于谁？
   ↓
identity?
supply?
traffic?
commerce?
trust?
platform?
interfaces?
```

例如：

```text
billing      → commerce/billing
routing      → traffic/routing
provider     → supply/provider
user         → identity/user
networking   → platform/networking
http         → interfaces/http
```

只有出现真正独立的新领域时，才允许增加新的一级目录。

新增一级领域至少应满足大部分条件：

1. 无法自然归入现有任何领域；
2. 有独立的业务语言和职责；
3. 有独立的数据或状态生命周期；
4. 有独立的 Ownership / Maintainer；
5. 有清晰的公开边界；
6. 预计长期存在。

> **新增功能默认向下生长，不横向扩张一级目录。**

---

## 4. 一个功能只有一个主要归属

同一个业务不得因为技术实现不同而散落在多个顶级目录。

禁止：

```text
service/billing
database/billing
common/pricing
server/billing
```

应该首先归属于：

```text
commerce/
└── billing/
```

Billing 内部可以包含业务逻辑、数据库适配、缓存适配、事件适配和测试，但这些技术实现不能改变 Billing 的业务归属。

> **一个业务，一个家。**

---

## 5. 默认保持目录浅，复杂后再分级

前期默认使用：

```text
领域/
└── 功能/
```

例如：

```text
identity/user/
supply/provider/
traffic/routing/
commerce/billing/
platform/networking/
```

不要为了未来可能出现的复杂度提前建立大量层级。

当一个功能已经真实变复杂时，再继续向下拆：

```text
commerce/
└── billing/
    ├── account/
    ├── invoice/
    └── charging/
```

如果以后 `invoice` 继续扩大，还可以继续：

```text
billing/
└── invoice/
    ├── issuing/
    ├── adjustment/
    └── delivery/
```

目录允许形成树，但每一次分叉都必须代表真实的职责边界。

> **不为未来尚未出现的复杂度提前造树。**

---

## 6. 技术结构只能放在功能内部

允许：

```text
commerce/
└── billing/
    ├── src/
    ├── tests/
    └── adapters/
```

功能真正复杂后，也可以演进为：

```text
billing/
├── domain/
├── application/
├── adapters/
└── tests/
```

禁止重新建立全局技术分类：

```text
crates/
├── services/
├── databases/
├── repositories/
├── controllers/
└── models/
```

> **外部按业务分，内部按技术组织。**

---

## 7. 禁止垃圾桶目录

原则上禁止新增：

```text
common/
shared/
utils/
helpers/
misc/
others/
```

当代码无法归类时，应首先重新判断它真正属于哪个领域或功能。

例如：

```text
calculate_price() → commerce/pricing
validate_api_key() → identity/auth
```

真正通用的东西根据性质进入 `kernel` 或 `platform`，但两者同样禁止成为垃圾桶。

---

## 8. 测试跟随代码归属

谁拥有生产代码，谁拥有测试。

例如：

```text
platform/
└── networking/
    ├── src/
    └── tests/
```

以及：

```text
commerce/
└── billing/
    ├── src/
    └── tests/
```

Rust 单元测试可以直接与源文件放在一起：

```rust
#[cfg(test)]
mod tests {
    // ...
}
```

功能自身的黑盒或集成测试放 `<feature>/tests/`。

根目录 `/tests/` 只负责跨多个领域的系统级测试，例如 End-to-End、多领域 Integration、Compatibility、系统性能和整体回归。

> **功能测试跟功能走，系统测试放根目录。**

---

## 9. 跨领域只能通过公开边界协作

其他领域可以调用一个功能暴露的能力，但不能直接依赖它的内部实现。

正确：

```text
traffic
   ↓
commerce/billing public API
```

错误：

```text
traffic
   ↓
commerce/billing/internal/sqlx_repository
```

例如 Server 使用 Billing 时：

```text
apps/server
    ↓
commerce/billing
```

Server 只调用 Billing 对外暴露的能力；Billing 内部的 application、domain、adapters 和 tests 由 Billing 自己负责。

> **可以调用别人的能力，不能穿透别人的边界。**

---

## 10. `crates/` 之外的代码

不是所有代码都应该进入 `crates/`。

推荐仓库结构：

```text
burncloud/
├── apps/       # 可执行程序与 Composition Root
├── crates/     # 产品领域与可复用能力
├── tools/      # 研发工具、生成器、Harness
├── tests/      # 系统级测试
├── deploy/     # 部署
└── docs/       # 文档
```

`apps/` 负责系统启动与组件装配，不重新拥有 Identity、Traffic、Commerce 等业务逻辑。

`tools/` 服务开发流程，生产业务代码原则上不得依赖 `tools/`。

---

## 11. 新增代码只问三个问题

### 第一个问题：它属于谁？

优先在以下领域中确定唯一归属：

```text
identity
supply
traffic
commerce
trust
platform
interfaces
```

### 第二个问题：已经有对应功能目录吗？

有：放进现有目录。

没有：才考虑创建新的功能目录。

### 第三个问题：当前功能真的已经复杂到需要再分一级吗？

没有：保持目录浅。

有：再向下建立新的职责分类。

---

## 12. 判断目录是否健康

任何功能目录都应该能回答三个问题：

1. **我负责什么？**
2. **我不负责什么？**
3. **其他模块应该通过什么方式使用我？**

如果一个目录只能解释为“这里放相关代码”，说明这个目录的边界还不够清楚。

---

## 13. 最终规则

BurnCloud 的目录是一棵可以长期生长的树：

```text
Domain
   ↓
Feature
   ↓
Sub-feature
   ↓
Implementation
```

但不固定要求必须有多少层。

简单功能保持简单：

```text
commerce/billing
```

复杂度真正出现后再继续生长：

```text
commerce/billing/invoice
```

甚至：

```text
commerce/billing/invoice/issuing
```

每增加一层，都必须能够解释新的职责边界。

最终遵守四句话：

> **领域决定归属。**  
> **功能决定目录。**  
> **复杂度决定层级。**  
> **接口决定边界。**