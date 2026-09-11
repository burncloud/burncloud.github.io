---
title: "BurnCloud 模块边界与依赖规则"
slug: /architecture/module-boundary-rules/
sidebar_label: "模块边界与依赖规则"
description: "BurnCloud 模块化单体最小规则 V1：定义模块责任、依赖方向、跨模块协作和禁止越界。"
---

# BurnCloud 模块边界与依赖规则

> **版本：V1**
>
> **DDD 定责任，模块化单体定依赖，公开接口定协作，编译边界禁止越界。**

## 1. 谁负责谁

每个业务只能有一个主要 Owner。

| 模块 | 负责 |
| --- | --- |
| `kernel` | 全局最小类型与契约 |
| `identity` | 用户、组织、认证、授权 |
| `supply` | 模型、Provider、Channel、供给资源 |
| `traffic` | 请求、路由、调度、执行 |
| `commerce` | 用量、额度、价格、账单、结算 |
| `trust` | 审计、证明、合规、风控 |
| `platform` | 数据库、缓存、网络、消息、监控等基础设施 |
| `interfaces` | HTTP、UI、SDK、CLI、Webhook 等外部入口 |

> **一个业务，一个 Owner，一个家。**

## 2. 谁能依赖谁

默认依赖方向：

```text
interfaces
    ↓
trust
    ↓
traffic
    ↓
commerce
    ↓
supply
    ↓
identity
    ↓
platform
    ↓
kernel
```

规则：

- `kernel` 不依赖任何业务模块；
- `platform` 只依赖 `kernel`；
- 上层模块可以依赖下层模块的公开接口；
- 下层模块不得反向依赖上层模块；
- 禁止循环依赖。

需要跨层协作时，优先通过公开 Contract 或事件完成；确有必要改变依赖方向时，必须先修改架构规则。

## 3. 跨部门怎么说话

只有两种正式方式：

### 同步调用

通过公开 API / Contract / Port：

```text
traffic
   ↓
supply::public
```

### 异步协作

通过公开事件：

```text
traffic
   ↓
UsageRecorded
   ↓
commerce
```

外部模块只能看到：

```text
public API
public contract
public event
```

模块内部实现默认不可见。

## 4. 数据归谁

谁拥有业务，谁拥有该业务的数据和状态，包括：

```text
业务规则
Repository
数据库表
缓存
事件
测试
```

其他模块不得直接读写其数据库表、Repository 或缓存，必须通过 Owner 的公开边界。

> **谁拥有业务，谁拥有数据。**

## 5. 什么禁止越界

以下行为禁止：

```text
跨模块访问 internal            ❌
跨模块访问 adapters            ❌
跨模块调用 repository          ❌
跨模块直接读写数据库表          ❌
形成循环依赖                   ❌
下层反向依赖上层               ❌
platform 依赖业务模块           ❌
kernel 依赖业务模块             ❌
interfaces 编写核心业务规则     ❌
同一业务存在多个 Owner          ❌
复制其他模块的业务规则          ❌
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

## 6. 默认隐藏，按需公开

模块内部默认私有，只公开稳定边界。

```text
billing/
├── public.rs
├── domain/
├── application/
├── adapters/
└── tests/
```

Rust 示例：

```rust
pub mod public;

mod domain;
mod application;
mod adapters;
```

> **不要默认 `pub`。**

## 7. 最终检查

开发任何代码前只问四个问题：

```text
1. 谁负责它？
2. 谁需要依赖它？
3. 通过什么公开接口协作？
4. 有没有穿透别人的内部边界？
```

最终原则：

> **一个业务一个 Owner，跨模块只走公开接口，数据跟随 Owner，依赖单向且禁止穿透。**
