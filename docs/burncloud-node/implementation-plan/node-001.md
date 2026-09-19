---
title: "NODE-001：建立 Node Core 启动入口与生命周期合同"
slug: /burncloud-node/implementation-plan/node-001/
---

# NODE-001：建立 Node Core 启动入口与生命周期合同

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Node Core**  
**功能依赖：无**

> 这是实施计划，不是 Codex 的直接开发授权。真正开始实现前，仍需基于当时的 `burncloud/burncloud/main` 重新做 Evidence Audit，并创建通过 READY Gate 的 Engineering Issue。

### TL;DR

我们要给 BurnCloud 增加一个正式的 `burncloud node` 启动入口，并定义 Node 从启动到关闭的基本生命周期。这样后续硬件检测、模型解析和本地 Runtime 都能挂在同一个稳定入口上，而不是各自发明启动方式。完成后，BurnCloud Node 会成为现有 BurnCloud 的一种运行形态，而不是第二套系统。

### 背景与动机（Why）

现在 BurnCloud 已经有统一的可执行入口，`server` 和 `router` 也共享现有 Server startup，但还没有一个和它们同级的 Node runtime 入口。

如果这个边界现在不先划清楚，后续开发很容易出现几个问题：有人把 Node 当成新的 Server，有人直接把本地模型逻辑塞进 CLI，还有人可能重新创建 Router、Database 或进程管理体系。短期看都能“跑起来”，长期却会形成两套启动链和重复的系统职责。

所以 NODE-001 只做一件事：**先把 Node 的门口和生命周期立起来。** 至于配置上下文、Server / Router 组合、本地模型执行，全部交给后续 Issue。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 增加一等 `burncloud node` runtime 入口 | 不创建第二个 BurnCloud 可执行程序 |
| 定义 initialize / start / shutdown 生命周期 | 不在本 Issue 里接入 Server / Router |
| 建立最小 Node Core 编排层 | 不建立 NodeConfig / NodeContext |
| 处理 Node 自己的启动失败与退出清理 | 不做 Hardware / Resolver / Download / Runtime |
| 保持现有 `server` / `router` 行为不变 | 不修改 Billing / Auth / Router / Database 语义 |

### 风险与安全网（Risk）

> 这是一个**加性、低侵入**改动：最坏结果应该只是新的 Node 入口无法正常启动；一旦实现需要跨进 Router、Billing、Database 或其它未授权领域，Codex 必须停止并报告，而不是继续硬改现有系统。

### 审批者关注点（Reviewer Focus）

你只需要确认 3 个核心决策，其余实现细节由 Task Contract、测试和 CI 约束：

1. **是否同意 `burncloud node` 成为一等运行入口，而不是普通管理 CLI 命令？**
2. **是否同意 Node Core 只负责生命周期编排，不负责 Server、Router、模型和进程业务？**
3. **是否同意 NODE-001 明确止步于生命周期，NodeConfig 留给 NODE-002，Server / Router 组合留给 NODE-003？**

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立一个一等的 `burncloud node` runtime entry，以及最小 Node Core 生命周期合同：

```text
burncloud node
      ↓
initialize
      ↓
start
      ↓
RUNNING
      ↓
shutdown
      ↓
STOPPED
```

NODE-001 只授权 Node runtime entry 与生命周期编排。

- `NODE-002`：NodeConfig / NodeContext。
- `NODE-003`：复用现有 Server / Router 形成 Node 模式。

### 2. Evidence

以下证据基于当前 `burncloud/burncloud/main`。

#### STATIC CONFIRMED — 顶层 CLI 已有统一入口

`src/main.rs :: main` 是当前可执行程序入口，并统一完成：

- `.env` 加载；
- `MASTER_KEY` 检查 / 生成；
- logging 初始化；
- CLI dispatch。

结论：Node 必须复用现有 executable / bootstrap，不创建第二套启动体系。

#### STATIC CONFIRMED — `server` 与 `router` 共享 Server startup

`src/main.rs :: main` 将 `server` 与 `router` 分发到 `run_async_server()`，后者调用：

```text
burncloud_server::start_server(...)
```

对应：`INV-RUNTIME-001`。

#### STATIC CONFIRMED — 当前没有一等 Node runtime 分支

当前顶层 runtime dispatch 明确处理：

```text
client
server
router
```

不存在与 `server` / `router` 同级的 Node lifecycle entry。

#### STATIC CONFIRMED — 当前 workspace 没有 `crates/node`

当前 `crates/` 已有 Server、Router、Database、Download、Service 等 crate，但没有 `crates/node`。

此事实**不构成创建 `crates/node` 的预先授权**。实现位置必须在 READY Issue / Task Contract 阶段根据当时源码确定；如新增 `crates/node`，其职责只能是薄的 orchestration / lifecycle 层。

#### STATIC CONFIRMED — Server 已是统一 Axum App

`crates/server/src/lib.rs :: create_app` 已组合 management routes、internal routes、可选 LiveView 与 data-plane router fallback。

对应：`INV-RUNTIME-002`。

NODE-001 不得重建或改变该 Server 结构。

### 3. Entry / Starting Point

当前调查起点：

```text
src/main.rs :: main
src/main.rs :: run_async_server
src/main.rs :: run_async_cli
```

目标产品入口：

```text
burncloud node
```

实现前必须先从 `src/main.rs :: main` 重新确认 current-main CLI dispatch。

### 4. Reuse Targets / Do Not Recreate

#### Reuse

- 现有 BurnCloud 单一 executable；
- 现有 process bootstrap；
- 现有 `.env` / `MASTER_KEY` / logging 初始化顺序；
- 现有 workspace dependency / crate 组织方式。

#### Do Not Recreate

```text
second BurnCloud binary
second logging bootstrap
second HTTP server
NodeGateway
NodeRouter
NodeDatabase
```

若现有结构无法承载 Node lifecycle，必须触发 Stop Condition；不得以“实现方便”为理由创建平行体系。

### 5. Scope

#### Allowed

- 顶层 CLI 增加一等 `burncloud node` runtime dispatch；
- 最小 Node Core lifecycle abstraction / composition root；
- initialize / start / shutdown 生命周期；
- 最小 shutdown signal plumbing；
- Node Core 自己创建的生命周期任务清理；
- 与上述行为直接相关的 targeted tests；
- 经 current-main 证据证明必要的最小 workspace wiring。

#### Avoid

- NODE-002：NodeConfig / NodeContext；
- NODE-003：Server / Router Node profile；
- HardwareProfile；
- Model Resolver；
- Model Preparation / Download；
- Runtime adapter；
- model child-process management；
- Local Channel registration；
- Billing / Auth / quota；
- Router 行为变化；
- Database schema / persistence；
- 第二套 Gateway / Router / Database。

### 6. Behavior Contract

#### Inputs

- `burncloud node` 启动意图；
- 已由现有顶层 bootstrap 准备的 process environment；
- process-level shutdown request / termination signal。

#### State semantics

正常状态机：

```text
CREATED
  ↓ initialize
INITIALIZED
  ↓ start
RUNNING
  ↓ shutdown requested
STOPPING
  ↓ cleanup complete
STOPPED
```

失败状态：

```text
initialize failure → FAILED
start failure      → FAILED
shutdown failure   → failure must be surfaced
```

`FAILED` 不得被伪装成 `RUNNING` 或 `STOPPED`。

#### Ownership

Node Core owns：

- Node runtime 生命周期顺序；
- Node 级启动 / 停止编排；
- 自己创建的 lifecycle resources 的清理。

Node Core does not own：

- HTTP request handling；
- Provider / Local route selection；
- Database 业务状态；
- Model Resolution；
- Artifact 下载；
- llama.cpp 参数；
- 模型子进程生命周期。

#### Side Effects

允许：

- CLI runtime dispatch；
- process-local lifecycle state；
- shutdown signal handling；
- Node Core 自身 lifecycle task 创建 / 清理。

禁止新增：

- database schema；
- network protocol；
- model artifact；
- model subprocess；
- billing / quota side effect。

### 7. Failure / Forbidden Fallbacks

#### Initialize failure

- 返回明确错误；
- 不进入 RUNNING；
- 清理已经由 Node Core 创建的部分资源。

#### Start failure

- 返回明确错误；
- 不宣称 Node 已启动；
- 不 fallback 到 `server` 或 `router`。

#### Shutdown failure

- 暴露未完成 / 失败状态；
- 不忽略错误后宣称正常停止。

#### Forbidden fallbacks

```text
do not silently run `burncloud server`
do not silently run `burncloud router`
do not create a second HTTP server
do not create a second Router
do not start model runtime/processes as a workaround
do not modify unrelated modules to make Node appear startable
do not pull NODE-002 / NODE-003 responsibilities into NODE-001
```

### 8. Impact / Invariants

```text
persistence: none
external_calls: none newly owned by NODE-001
billing_usage_quota: none
auth_authorization: none
routing_provider: none
concurrency_transactions: process-local lifecycle coordination only
public_api_cli: yes — add first-class `burncloud node`
process_runtime_lifecycle: yes — define Node Core lifecycle
```

必须保持：

- `INV-RUNTIME-001` — `server` / `router` 现有 startup 语义不变；
- `INV-RUNTIME-002` — 现有 Server 继续是统一 Axum application；
- `INV-WORKSPACE-001` — 新增 workspace wiring 时遵循现有依赖组织方式。

架构约束：

- Node Core = orchestration / lifecycle layer；
- Node Core 不进入每个 inference request 的 data plane；
- Node Core 不成为 Router / Downloader / Runtime / Process Manager 的第二实现。

若必须改变以上任一边界：

```text
ARCHITECTURE / INVARIANT CHANGE REQUIRED
```

然后停止普通 Feature 实现流程。

### 9. Dependencies

功能依赖：无。

后续依赖本合同：

```text
NODE-002
NODE-003
```

真正进入实现前必须：

1. 针对当时 `burncloud/burncloud/main` 重新执行 Evidence Audit；
2. 创建正式 Engineering Issue；
3. 通过 READY Gate；
4. 生成 current-main Task Contract 后才能编码。

### 10. Stop Conditions

```text
STOP IF:
- current main already has a materially different Node runtime entry / Node Core
- implementing `burncloud node` requires changing Billing / Auth / Router semantics
- implementation requires a second HTTP server or Router
- implementation requires new persistent schema/state ownership
- implementation pulls NODE-002 or NODE-003 responsibility into NODE-001
- implementation requires Hardware / Resolver / Download / Runtime / model process lifecycle
- an INV-* must change without explicit architecture authorization
- existing `server` / `router` behavior cannot be preserved inside this scope
- meaningful targeted/regression verification cannot be performed
```

触发后必须输出：

```text
SCOPE / ARCHITECTURE CONFLICT DETECTED
No out-of-scope code changed.
Evidence: ...
Conflict: ...
Decision required: ...
```

---

## 第三层：验收层（Definition of Done）

只有以下项目全部满足，NODE-001 对应的 Engineering Issue 才可验收。

### ✅ 功能结果

- [ ] 存在明确的一等 `burncloud node` runtime entry。
- [ ] `burncloud node` 进入 Node Core，而不是普通管理 CLI、`server` 或 `router` 的别名。
- [ ] Node Core 具有可测试的 initialize / start / shutdown 生命周期。
- [ ] 正常状态满足 `CREATED → INITIALIZED → RUNNING → STOPPING → STOPPED`。
- [ ] initialize / start 失败会明确进入失败路径，不会被伪装成成功。
- [ ] shutdown 有明确完成 / 失败语义，并清理 Node Core 自己拥有的生命周期资源。

### ✅ 边界保护

- [ ] 未创建第二个 BurnCloud binary。
- [ ] 未创建第二套 logging bootstrap、HTTP Server、Router 或 Database。
- [ ] 未实现 NODE-002 的 NodeConfig / NodeContext。
- [ ] 未实现 NODE-003 的 Server / Router Node profile。
- [ ] 未引入 Hardware、Resolver、Download、Runtime、model process 或 Local Channel 职责。
- [ ] Node Core 仍然只是 orchestration / lifecycle layer。

### ✅ 回归验证

- [ ] `burncloud server` 保持现有 startup 行为。
- [ ] `burncloud router` 保持现有 startup 行为。
- [ ] `burncloud client` 的现有 dispatch 未被 NODE-001 改写。
- [ ] `INV-RUNTIME-001` 保持成立。
- [ ] `INV-RUNTIME-002` 保持成立。
- [ ] 如涉及 workspace wiring，`INV-WORKSPACE-001` 保持成立。

### ✅ Targeted / Runtime 验证

- [ ] 有测试证明 `burncloud node` 被识别为一等 runtime entry。
- [ ] 有测试证明 initialize failure 不会进入 RUNNING。
- [ ] 有测试证明 start failure 会向上传播。
- [ ] 有测试证明 shutdown request 进入明确停止流程。
- [ ] 有测试证明不会静默 fallback 到 `server` / `router`。
- [ ] 在可执行环境中完成一次 `burncloud node → RUNNING → shutdown → STOPPED` 的 runtime 验证。

### ✅ 工程流程

- [ ] 开发前已针对 current `main` 重新完成 Evidence Audit。
- [ ] 正式 Engineering Issue 已通过 READY Gate。
- [ ] Task Contract 未获得比 Issue 更大的架构权限。
- [ ] 没有未解决的 Stop Condition。
- [ ] 所有实现通过 feature/fix branch + Pull Request 进入 `main`，没有直接提交实现到 `main`。


---

## 第四层：人类验收（Human Acceptance）

> 本节由 [Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/) 生成。机器测试、CI 或 AI Review 不能替代这里的人工验收。

### NODE-001 — Node Core 启动入口与生命周期

**验收者：** 产品负责人 + Runtime 工程师。

**人工步骤：**
1. 在可执行环境中直接运行 `burncloud node`。
2. 确认它进入独立 Node runtime，而不是打印后偷偷转成 `burncloud server` / `burncloud router`。
3. 发出正常停止信号（例如 Ctrl+C / SIGTERM）。
4. 再分别启动现有 `burncloud server`、`burncloud router`，确认原行为没有被改坏。

**人类通过标准：** Node 能明确启动、运行、停止；停止后没有由 Node Core 自己遗留的生命周期任务；现有 server/router 仍可正常启动。

**人工判定失败：** Node 启动即静默 fallback 到其它模式、停止无响应、退出后仍残留 Node 自己创建的长期任务，或现有 server/router 行为变化。

**建议证据：** 启动输出 + 停止输出 + 三种 runtime 的人工运行记录。
