---
title: "Node 框架合同"
slug: /burncloud-node/contracts/
hide_table_of_contents: false
---

# Node 框架合同

本节记录 BurnCloud Node **已经存在于代码中的公开框架合同**。它说明各能力如何接线、各自拥有哪一份结果，以及必须停在哪条边界上；它不规定生产实现采用哪种工具、厂商或操作系统。

## 当前结论

```text
Node Framework Contract
├─ 状态：Accepted
├─ Fake 流程：Complete
├─ 生产 Adapter：Not started
└─ 原则：先复用现有 Contract，不重复创建接口
```

状态含义：

| 状态 | 含义 |
|---|---|
| `Accepted` | 公开形状已被框架采用；没有 `CONTRACT_GAP` 证据时不得修改 |
| `Framework Only` | Contract、Fake 和接线已存在，但不代表生产实现完成 |
| `Production Ready` | 真实实现和人类验收均已完成；本节当前不声明任何能力达到此状态 |
| `Contract Gap` | 现有 Contract 无法表达已证明的必要行为；必须单独升级 |

## Contract Inventory

| Integration Queue 名称 | 代码中的真实 Contract | Owner | 状态 | 文档 |
|---|---|---|---|---|
| Model Resolver | `ModelResolver` | Supply | Accepted / Framework Only | [ModelResolver](./model-resolver) |
| Hardware Probe | `HardwareProbe` | Platform Node | Accepted / Framework Only | [HardwareProbe](./hardware-probe) |
| Artifact Downloader | `ArtifactPreparer` | Platform Node | Accepted / Framework Only | [ArtifactPreparer](./artifact-preparer) |
| Runtime Preparer | `RuntimePreparer` | Platform Node | Accepted / Framework Only | [RuntimePreparer](./runtime-preparer) |
| Runtime Adapter | `RuntimeAdapter` | Platform Node | Accepted / Framework Only | [RuntimeAdapter](./runtime-adapter) |
| Process Manager | `ProcessManager` | Platform Node | Accepted / Framework Only | [ProcessManager](./process-manager) |
| Readiness Probe | `ReadinessProbe` | Platform Node | Accepted / Framework Only | [ReadinessProbe](./readiness-probe) |
| Health Probe | `HealthProbe` | Platform Node | Accepted / Framework Only | [HealthProbe](./health-probe) |
| Channel Adapter | 没有独立 trait；当前是 application seam | Interfaces Server + Traffic | Accepted / Framework Only | [Local Route Attachment](./local-route-attachment) |

### 名称校正规则

```text
队列中的概念名称
        ↓
代码里存在同名公开 Contract？
        │
        ├─ 是 → 使用代码中的准确名称
        │
        └─ 否 → 记录映射或缺口
                 ↓
              不得为了对齐队列名称而新建 trait
```

因此：

- 当前代码是 `ArtifactPreparer`，不是 `ArtifactDownloader`；下载只是某种可能的实现方式。
- 当前没有 `ChannelAdapter` trait；Local Channel 通过应用层接线函数进入 Existing ModelRouter。
- `DemandReconciler`、`NodeOrchestrator` 和 `NodeComposition` 是框架协调者，不是伙伴需要各自实现的 Adapter Contract。

## 完整调用顺序

```text
ModelDemand
    ↓
HardwareProbe.inspect()
    ↓ HardwareProfile
ModelResolver.resolve(...)
    ├─ Unsupported → LocalUnsupported → STOP
    └─ Local(ResolvedModel)
            ↓
ArtifactPreparer.prepare(...)
            ↓ PreparedArtifact
RuntimePreparer.prepare(...)
            ↓ PreparedRuntime
RuntimeAdapter.plan(runtime, artifact)
            ↓ ProcessPlan
ProcessManager.start(plan.process)
            ↓ ProcessHandle
ReadinessProbe.wait_ready(plan.readiness)
            ↓ ready
HealthProbe.is_healthy(plan.readiness)
            ↓ healthy
Local Route Attachment
            ↓ LocalRouteAttachmentId
Routable
```

任一步返回 Error：

```text
当前步骤失败
    ↓
记录 Failed evidence
    ↓
不得调用后续 Contract
    ↓
不得制造 READY 或 Routable
```

## Receipt 所有权

每一步只拥有自己产生的 Receipt，不能替别的 Owner 猜结果。

| Contract / Seam | 拥有的输出或证明 | 禁止伪造的结果 |
|---|---|---|
| `HardwareProbe` | `HardwareProfile` | 模型选择、路由选择 |
| `ModelResolver` | `ResolvedModel` 或 `LocalUnsupported` | 下载完成、Runtime 可用 |
| `ArtifactPreparer` | `PreparedArtifact` | Runtime、Process、READY |
| `RuntimePreparer` | `PreparedRuntime` | 启动参数、进程已启动 |
| `RuntimeAdapter` | `ProcessPlan` | 进程已启动、健康、已路由 |
| `ProcessManager` | `ProcessHandle` | READY、Healthy、Routable |
| `ReadinessProbe` | readiness success/error | 长期健康、路由注册 |
| `HealthProbe` | 当前 healthy/unhealthy | 路由注册或摘除 |
| Local Route Attachment | `LocalRouteAttachmentId` / `DetachedRoute` | Runtime 和进程事实 |

## 共同禁止项

```text
所有 Contract 都禁止
├─ 读取或修改不归自己所有的业务数据表
├─ 绕过上游 Receipt 自己猜测成功
├─ 在 Orchestrator 中加入具体 Runtime / OS 分支
├─ 把 Fake 成功当成 Production Ready
├─ 因为未来可能需要而扩大 Contract
└─ 在没有 CONTRACT_GAP 证据时修改 Accepted Contract
```

## 代码来源

```text
crates/supply/service-models/src/resolver.rs
crates/platform/node/src/contracts.rs
crates/platform/node/src/preparation.rs
crates/platform/node/src/fake.rs
crates/platform/node/src/composition.rs
crates/interfaces/server/src/node_orchestrator.rs
crates/interfaces/server/src/node_attachment.rs
```

## 文档与代码冲突时怎么办

```text
发现文档和 main 代码不一致
        ↓
先确认代码是否经过 Accepted Contract 变更流程
        │
        ├─ 是 → 同一个 PR 更新文档
        └─ 否 → STOP
                 ↓
              不用文档为越界代码背书
```

