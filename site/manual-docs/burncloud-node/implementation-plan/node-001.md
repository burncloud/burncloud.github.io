---
title: "NODE-001：建立 Node Core 启动入口与生命周期合同"
slug: /burncloud-node/implementation-plan/node-001/
---

# NODE-001：建立 Node Core 启动入口与生命周期合同

**状态：PLANNED**  
**类别：Node Core**  
**主要结果：为 BurnCloud Node 建立唯一、明确、可停止的运行生命周期入口**  
**功能依赖：无**

> 本页是 Implementation Plan，不是实现授权。即使本页规格已经完整，也必须在准备开发时依据当时的 `burncloud/burncloud` `main` 重新执行 Evidence Audit，创建通过 READY Gate 的 Engineering Issue 后，才能交给 Codex 实现。

## 1. 目标（Goal）

为 BurnCloud 增加一个一等的 **Node 运行入口与 Node Core 生命周期合同**，使 `BurnCloud Node` 成为现有 BurnCloud 的一种受控运行形态，而不是另一套独立程序体系。

本 Issue 只解决：

```text
burncloud node
      ↓
Node Core lifecycle
      ↓
initialize
      ↓
start
      ↓
shutdown
```

本 Issue **不负责**把 Server / Router 真正组合进 Node 模式；该职责属于 `NODE-003`。

本 Issue **不负责**建立 NodeConfig / NodeContext；该职责属于 `NODE-002`。

## 2. 当前事实与证据（Current Evidence）

以下事实基于当前 `burncloud/burncloud` `main`：

### `STATIC CONFIRMED` — 顶层 CLI 已有统一入口

`src/main.rs :: main` 是当前 BurnCloud 可执行程序的顶层入口，并在进入具体子命令前统一完成：

- `.env` 加载；
- `MASTER_KEY` 检查 / 生成；
- logging 初始化；
- CLI 子命令分发。

这意味着 Node 不需要创建第二个二进制启动体系或第二套 logging bootstrap。

### `STATIC CONFIRMED` — `server` 与 `router` 当前共享 Server startup

`src/main.rs :: main` 将 `server` 与 `router` 都分发到 `run_async_server()`；`run_async_server()` 最终调用：

```text
burncloud_server::start_server(...)
```

对应现有工程不变量：`INV-RUNTIME-001`。

### `STATIC CONFIRMED` — 当前顶层入口没有一等的 Node runtime 分支

`src/main.rs :: main` 当前一等处理：

```text
client
server
router
```

其他命令进入通用 `run_async_cli()` / `handle_command()` 路径。当前顶层启动代码中不存在与 `server` / `router` 同级的 Node runtime lifecycle 分支。

### `STATIC CONFIRMED` — 当前 workspace 没有 `crates/node`

当前 `crates/` 包含现有 Server、Router、Database、Download、Service 等 crate，但没有独立 `crates/node`。

这只是当前事实，**不代表本 Issue 已经批准必须创建 `crates/node`**。具体实现位置应在 Task Contract 阶段基于当前源码决定；若创建 `crates/node`，它必须保持为薄的 orchestration / lifecycle 层。

### `STATIC CONFIRMED` — 现有 Server 已经是统一 Axum App

`crates/server/src/lib.rs :: create_app` 已组合 management plane、internal routes、可选 LiveView 与 data-plane router fallback。

对应现有工程不变量：`INV-RUNTIME-002`。

本 Issue 不应重建或改变这一 Server 结构。

## 3. 入口 / 调查起点（Entry / Starting Point）

### 当前真实入口

```text
src/main.rs :: main
src/main.rs :: run_async_server
src/main.rs :: run_async_cli
```

### 目标产品入口

```text
burncloud node
```

Codex 在实现前必须从 `src/main.rs :: main` 开始确认当前 CLI dispatch，而不是从全仓库自由搜索后自行发明第二个入口。

## 4. 复用目标（Reuse Targets）

### 必须优先复用

- 现有 BurnCloud 单一可执行程序入口；
- `src/main.rs` 已有的 process bootstrap；
- 现有 `.env` / `MASTER_KEY` / logging 初始化顺序；
- 现有 workspace 依赖和 crate 组织方式；
- 后续由 `NODE-003` 复用的 `burncloud-server` / `burncloud-router`。

### 不得重新创建

```text
第二个 BurnCloud Node binary
第二套 logging bootstrap
第二套 HTTP Server
NodeGateway
NodeRouter
NodeDatabase
```

如果现有结构无法承载 Node lifecycle，必须先给出源码证据并触发 Stop Condition；不能因为实现方便而创建平行体系。

## 5. 期望行为（Expected Behavior）

完成后：

1. BurnCloud 有一个明确的一等 Node 运行入口；
2. `burncloud node` 进入 Node Core，而不是伪装成 `server`、`router` 或普通管理 CLI 命令；
3. Node Core 有明确的 initialize / start / shutdown 生命周期语义；
4. 初始化失败时不得继续进入 RUNNING；
5. shutdown 完成后不得遗留由 Node Core 自己拥有的后台生命周期任务；
6. Node Core 只负责生命周期编排，不承担 Server、Router、模型下载、模型选择或进程执行职责。

本 Issue 完成时 **不要求 Node 已经提供 AI API**。AI API 组合属于 `NODE-003`。

## 6. 行为合同（Behavior Contract）

### Inputs

- 用户 / 运维启动意图：`burncloud node`；
- 现有顶层 bootstrap 已准备的 process environment；
- 进程级 shutdown request / termination signal。

### Output semantics

Node Core 必须提供以下语义，而不强制具体 Rust struct / trait 名称：

```text
initialize succeeds
    ↓
start
    ↓
RUNNING
    ↓
shutdown requested
    ↓
STOPPING
    ↓
STOPPED
```

如果 initialize 或 start 失败：

```text
FAILED
```

并向调用方返回明确错误 / 非成功退出结果。

### Ownership

Node Core 只拥有：

- Node runtime 的生命周期顺序；
- Node 级启动 / 停止编排；
- 自己创建的生命周期任务的清理责任。

Node Core 不拥有：

- HTTP 请求处理；
- Provider / Local route selection；
- Database 业务状态；
- Model Resolution；
- Artifact 下载；
- llama.cpp 参数构造；
- 模型子进程生命周期。

这些职责必须由对应现有组件或后续 Node Issue 拥有。

### Side effects

本 Issue 允许的新增副作用仅限：

- CLI runtime dispatch；
- process-local Node lifecycle state；
- shutdown signal handling；
- Node Core 自己的生命周期任务启动与清理。

本 Issue不应新增数据库 schema、网络协议、模型文件、副进程或计费副作用。

## 7. 失败行为（Failure Behavior）

### 初始化失败

- 返回明确错误；
- 不进入 RUNNING；
- 清理已经由 Node Core 创建的部分生命周期资源。

### 启动失败

- 返回明确错误；
- 不把失败状态伪装成 Node 已启动；
- 不静默 fallback 到普通 `server` 或 `router` 模式。

### shutdown 失败

- 必须暴露失败 / 未完成状态；
- 不允许通过直接忽略错误来宣称正常停止。

### Forbidden fallbacks

```text
do not silently run `burncloud server`
do not silently run `burncloud router`
do not create a second HTTP server
do not start model runtime/processes as a workaround
do not modify unrelated modules merely to make Node appear startable
```

## 8. 范围（Scope）

### Allowed

- 顶层 CLI 对 `burncloud node` 的一等 dispatch；
- 最小 Node Core lifecycle abstraction / composition root；
- initialize / start / shutdown 的生命周期合同；
- 最小 shutdown signal plumbing；
- 为上述行为增加必要的 targeted tests；
- 若源码证明确有必要，进行最小且不改变现有行为的 workspace wiring。

实现位置不在本计划页预先锁死。一个薄的 `crates/node` 是允许的候选，但不是本 Issue 的既定结论。

### Avoid

- `NODE-002` 的 NodeConfig / NodeContext；
- `NODE-003` 的 Server / Router Node profile 组合；
- HardwareProfile；
- Model Resolver；
- Model Preparation / Download；
- Runtime adapter；
- model child-process management；
- Local Channel registration；
- Billing / Auth / quota 语义变化；
- Router 行为变化；
- Database schema / persistence 变化；
- 第二套 Gateway / Router / Database。

## 9. 影响面（Impact）

```text
persistence: none
external_calls: none newly owned by NODE-001
billing_usage_quota: none
auth_authorization: none
routing_provider: none
concurrency_transactions: process-local lifecycle coordination only
public_api_cli: yes — add first-class `burncloud node` runtime entry
process_runtime_lifecycle: yes — define Node Core initialize/start/shutdown semantics
```

如果实现过程中发现必须改变上述 `none` 项，本 Issue 的当前边界不再成立，必须触发 Stop Condition。

## 10. Invariants / Architecture

### 必须保持

- `INV-RUNTIME-001` — `server` 与 `router` 现有 CLI 语义继续共享当前 Server startup；NODE-001 不应改变它们。
- `INV-RUNTIME-002` — 现有 Server 继续保持统一 Axum application；NODE-001 不创建平行 Server。
- `INV-WORKSPACE-001` — 如果新增 workspace crate / dependency，继续遵守现有 workspace dependency 组织方式。

### Node 架构约束

- Node Core 是 orchestration / lifecycle 层，不是业务 God Object；
- Node Core 不进入每一个 inference request 的数据面执行路径；
- Node Core 不成为 Router、Downloader、Runtime 或 Process Manager 的第二实现。

如果实现要求改变上述边界，必须标记：

```text
ARCHITECTURE / INVARIANT CHANGE REQUIRED
```

并停止普通 Feature 实现流程。

## 11. 依赖与阻塞（Dependencies / Blockers）

### 功能前置依赖

无。

`NODE-001` 是 Node Core 后续工作的基础，后续：

```text
NODE-002
NODE-003
```

依赖本 Issue 的稳定生命周期合同。

### 工程流程依赖

在真正交给 Codex 前：

- Canonical Issue Standard 必须已经生效；
- `burncloud/burncloud` 的 Issue / Task Contract enforcement 必须可用；
- 必须针对当时的 `main` 再执行一次 Evidence Audit。

## 12. 停止条件（Stop Conditions）

Codex 必须在以下任一条件出现时停止，而不是扩大 Diff：

```text
STOP IF:
- current main already contains a materially different Node runtime entry or Node Core implementation
- `burncloud node` requires changing Billing / Auth / Router semantics
- implementation requires a second HTTP server or second Router
- implementation requires new persistent schema/state ownership
- implementation requires NODE-002 or NODE-003 responsibilities to be pulled into NODE-001
- implementation requires model download, resolver, runtime adapter, or model process lifecycle
- an existing INV-* must be changed but the Engineering Issue did not authorize it
- preserving existing `server` / `router` behavior becomes impossible within this Issue scope
- meaningful targeted/regression verification cannot be performed
```

触发后必须报告：

```text
SCOPE / ARCHITECTURE CONFLICT DETECTED
No out-of-scope code changed.
Evidence: ...
Conflict: ...
Decision required: ...
```

## 13. 验证目标（Verification Targets）

### Targeted

验证：

- `burncloud node` 被识别为一等 runtime entry；
- lifecycle 顺序满足 initialize → start → shutdown；
- initialize failure 不会进入 RUNNING；
- start failure 被向上传播；
- shutdown request 能进入明确停止流程；
- Node Core 不静默 fallback 到 `server` / `router`。

具体测试文件和命令必须在创建 READY Engineering Issue / Task Contract 时根据当前仓库确定。

### Regression

至少保护：

- `burncloud server` 继续走现有 Server startup；
- `burncloud router` 继续保持现有行为；
- `burncloud client` 现有 dispatch 不被 NODE-001 改写；
- `INV-RUNTIME-001` 保持成立；
- `INV-RUNTIME-002` 保持成立。

### Runtime / E2E

在可执行测试环境中验证：

```text
start `burncloud node`
      ↓
Node Core reaches its running lifecycle state
      ↓
request process shutdown
      ↓
Node Core completes shutdown without silently switching runtime mode
```

NODE-001 的 Runtime/E2E **不要求** `/v1/...` 已经可用；Server / Router 接入属于 NODE-003。

### Protected behavior

- 一个 BurnCloud executable / bootstrap；
- 不创建第二套 HTTP Gateway / Router；
- Node lifecycle failure 必须显式失败；
- 不通过扩大 Issue Scope 来“修通”启动链。

## 14. 完成条件（Done When）

只有以下条件全部满足，NODE-001 对应的 Engineering Issue 才可验收：

- 存在明确的一等 `burncloud node` runtime entry；
- Node Core 有稳定、可测试的 initialize / start / shutdown 生命周期语义；
- 初始化或启动失败不会被伪装成成功；
- shutdown 有明确完成语义；
- Node Core 仍然只是生命周期 / orchestration 层；
- 没有创建第二套 Server、Router、Database、logging bootstrap 或 Node binary；
- 没有提前实现 NODE-002 / NODE-003 或后续模型执行职责；
- 现有 `server` / `router` / `client` 关键启动行为保持回归；
- 要求的 targeted / regression / runtime verification 已完成；
- 实现通过 branch + Pull Request 进入 `main`。

## 15. 从 PLANNED 转成 READY

本页面继续保持 `PLANNED`，因为 Implementation Plan 本身不提供实现授权。

准备开发 NODE-001 时，应执行：

```text
本计划页
   ↓
重新审计 burncloud/burncloud current main
   ↓
确认 Entry / Reuse Targets / Invariants / tests 仍成立
   ↓
创建 GitHub Engineering Issue
   ↓
通过 READY Gate
   ↓
Codex 创建 Task Contract
   ↓
开始实现
```

尤其需要在 READY 前重新确认：

- 当前 `main` 是否仍无一等 Node runtime entry；
- 是否已经出现新的 Node Core / `crates/node` 实现；
- 真实测试入口在哪里；
- `burncloud node` 的最小实现是否仍可在不侵入 NODE-002 / NODE-003 的情况下完成。
