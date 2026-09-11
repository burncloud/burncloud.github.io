---
title: "BurnCloud 模块边界与依赖规则"
slug: /architecture/module-boundary-rules/
sidebar_label: "模块边界与依赖规则"
description: "BurnCloud 模块边界与依赖规则 V1：定义 Ownership、依赖、跨模块协作、crate 边界、测试范围与架构执行。"
---

# BurnCloud 模块边界与依赖规则

> **版本：V1**
>
> **DDD 定责任，模块化单体定依赖，公开接口定协作，编译边界禁止越界。**

## 1. Ownership：谁负责谁

每个业务只能有一个主要 Owner。

| 模块 | 负责 |
| --- | --- |
| `kernel` | 全局最小类型与契约 |
| `identity` | 用户、组织、认证、授权 |
| `supply` | 模型、Provider、Channel、供给资源 |
| `traffic` | 请求、路由、调度、执行 |
| `commerce` | 用量、额度、价格、账单、结算 |
| `trust` | 审计、证明、合规、风控 |
| `platform` | 数据库、缓存、网络、消息、监控等通用基础设施 |
| `interfaces` | HTTP、UI、SDK、CLI、Webhook 等外部入口 |

> **一个业务，一个 Owner，一个家。**

## 2. Dependency：谁能依赖谁

不规定业务模块的固定上下层，只规定依赖必须**显式、单向、无环、只走公开边界**。

```text
kernel
  → 不依赖业务模块

platform
  → 只依赖 kernel（指 BurnCloud 内部模块依赖）

identity / supply / traffic / commerce / trust
  → 可依赖 kernel、platform
  → 可依赖其他业务模块的 public contract
  → 禁止形成循环依赖

interfaces
  → 可依赖业务模块的 public API
  → 不拥有核心业务规则

apps
  → 可装配所有模块
  → 不拥有核心业务规则
```

跨业务模块新增依赖时，必须能说明**为什么由调用方依赖被调用方**；不能为了方便形成双向依赖。

## 3. Communication：跨模块怎么说话

只有两种正式方式。

### 同步

通过公开 API / Contract / Port：

```text
traffic
   ↓
supply::public
```

### 异步

通过公开 Event：

```text
traffic
   ↓
UsageRecorded
   ↓
commerce
```

外部模块只允许依赖：

```text
public API
public contract
public event
```

公开边界不得暴露数据库 Row、ORM Model、Adapter 类型等内部实现。

## 4. Data Ownership：数据归谁

谁拥有业务，谁拥有该业务的：

```text
业务规则
状态
Repository
数据库表
缓存
事件
测试
```

其他模块不得直接读写其数据库表、Repository 或缓存，必须通过 Owner 的公开边界。

> **谁拥有业务，谁拥有数据。**

## 5. Visibility：默认隐藏，按需公开

模块内部默认私有，只公开稳定边界。

```text
billing/
├── public.rs
├── domain/
├── application/
├── adapters/
└── tests/
```

```rust
pub mod public;

mod domain;
mod application;
mod adapters;
```

模块内部采用六边形原则：

```text
public
  ↓
application
  ↓
domain / ports
  ↑
adapters
```

`domain` 不依赖 Adapter；Adapter 实现 Port。

> **不要默认 `pub`。**

## 6. Crate Boundary：什么时候升级成 crate

> **目录不等于 crate。默认先做 module；只有边界需要编译器强制时才升级为 crate。**

出现以下任一实质需要时，可以独立成 crate：

- 独立 Ownership / Maintainer；
- 需要独立依赖控制；
- 已形成稳定 Public API；
- 需要隐藏内部实现；
- 需要编译或测试隔离；
- 变化速度已明显独立于父模块。

**文件多、目录多，本身不是拆 crate 的理由。**

## 7. Test Boundary：测试放哪里

测试跟随代码 Ownership。

```text
src/*.rs #[cfg(test)]  → 单元测试
crate/tests/           → 本 crate 的公开行为与集成测试
domain/tests/          → 必要时的领域内跨 crate 测试
/tests/                → 跨领域、E2E、兼容性、系统性能测试
```

原则：

> **功能测试跟功能走，只有系统行为才上浮到根 `/tests`。**

跨模块测试不得成为绕过 Public API 的理由。

## 8. Composition Root：谁负责组装

`apps/server`、`apps/cli` 等是 Composition Root。

它们负责：

```text
创建 Adapter
注入依赖
连接模块
启动系统
```

例如：

```text
apps/server
   ↓
Billing public API
   ↓
Billing application
   ↓
Billing port
   ↑
SqlxBillingRepository
```

`apps` 只负责装配，不编写 Billing、Routing 等核心业务规则。

## 9. 禁止越界

以下行为禁止：

```text
跨模块访问 internal / adapters       ❌
跨模块直接调用 Repository            ❌
跨模块直接读写数据库表 / Cache        ❌
公开数据库 Row / ORM / Adapter 类型   ❌
形成循环依赖                         ❌
platform / kernel 反向依赖业务模块    ❌
interfaces / apps 持有核心业务规则    ❌
同一业务存在多个 Owner                ❌
复制其他模块的业务规则                ❌
用测试绕过模块公开边界                ❌
```

错误：

```text
traffic
  ↓
commerce/billing/adapters/postgres
```

正确：

```text
traffic
  ↓
commerce/billing/public
```

## 10. Enforcement：规则如何执行

能由工具强制的规则，不只依赖人工约定。

```text
Cargo dependencies   → 限制 crate 依赖
Rust visibility      → 隐藏内部实现
CI architecture test → 检查非法依赖和越界
CODEOWNERS/Maintainer → 明确 Ownership
```

架构违规应尽量在编译或 CI 阶段失败。

## 11. 最终检查

开发任何功能前只问六个问题：

```text
1. 谁负责它？
2. 谁需要依赖它？
3. 通过什么公开接口协作？
4. 数据属于谁？
5. 是否真的需要独立 crate？
6. 测试应该属于模块、领域还是系统？
```

最终原则：

> **一个业务一个 Owner，跨模块只走公开接口，数据跟随 Owner，依赖显式且无环；目录按需升级为 crate，测试跟随 Ownership，装配集中在 apps。**
