---
title: "NODE-002：建立 Node 配置与共享上下文"
slug: /burncloud-node/implementation-plan/node-002/
---

# NODE-002：建立 Node 配置与共享上下文

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Node Core**  
**功能依赖：NODE-001**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对当时的 `burncloud/burncloud/main`，创建通过 READY Gate 的 Engineering Issue，并生成 current-main Task Contract。

### TL;DR

NODE-002 要给 BurnCloud Node 建立一份统一配置 `NodeConfig` 和一个共享上下文 `NodeContext`。这样后面的硬件、模型、Runtime 和 Process 模块都从同一个组合根拿依赖，不再各自读取全局状态或偷偷创建 Database / Router。完成后，Node 的依赖关系会变得可见、可测试，也更难被 AI 写成多套平行系统。

### 背景与动机（Why）

现有 BurnCloud 已经有 Database、Settings、Monitor、Router 等成熟组件，但 Node 以后会把更多能力组合在同一个本地运行形态里。如果每个新模块都自行读取环境变量、自行连接数据库、自行 new 服务，短期很方便，长期却会出现多份配置、多份状态和无法判断谁真正拥有生命周期的问题。

所以 NODE-002 不增加业务能力，而是先建立一个清晰的“接线盒”：**NodeConfig 描述 Node 运行所需配置，NodeContext 持有已明确创建的共享依赖。** Context 本身不下载模型、不路由请求、不启动模型进程。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 定义最小 `NodeConfig` | 不复制现有 Settings 数据库 |
| 定义唯一 `NodeContext` / composition root | 不创建第二个 Database / Router |
| 通过显式依赖注入共享服务句柄 | 不把业务逻辑塞进 Context |
| 明确依赖的创建与所有权 | 不实现 Hardware / Resolver / Runtime |
| 对缺失配置和初始化失败明确报错 | 不用隐藏全局单例兜底 |

### 风险与安全网（Risk）

> 这是**结构性但低业务风险**的改动：它只决定依赖如何被组织，不改变现有 API、Router、Billing 或 Auth；如果实现需要复制状态系统或扩大到后续功能，AI 必须停止而不是继续扩权。

### 审批者关注点（Reviewer Focus）

你只需要确认 3 个决策：

1. **是否同意 Node 只有一个明确的 composition root，而不是多个模块自行组装依赖？**
2. **是否同意 NodeContext 只保存/提供依赖，不承载模型、路由、下载、进程等业务逻辑？**
3. **是否同意优先复用现有 Settings / Database / Service 实例，不为 Node 建第二套状态体系？**

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立 Node 级配置与共享上下文合同：

```text
existing bootstrap
      ↓
NodeConfig
      ↓
NodeContext / composition root
      ↓
shared dependencies
      ↓
future Node subsystems
```

NODE-002 只授权配置与依赖组合，不授权任何具体 Node 业务能力。

### 2. Evidence

以下证据基于当前 `burncloud/burncloud/main`。

#### STATIC CONFIRMED — 顶层 bootstrap 已统一处理进程级环境

`src/main.rs :: main` 已负责 `.env`、`MASTER_KEY`、logging 和 CLI dispatch。NodeConfig 不得复制这套 bootstrap。

#### STATIC CONFIRMED — Server 已有共享 AppState 模式

`crates/server/src/lib.rs` 中 `AppState` 已持有 `Database`、`SystemMonitorService`、`UserService`、Cache 和 data-plane Router 等共享对象，证明现有系统已经使用显式共享状态，而不是要求每个 handler 自行创建依赖。

#### STATIC CONFIRMED — 现有 Server startup 会创建 Database / Router

`burncloud_server::start_server()` 创建默认 Database，随后 `create_app()` 组合 Router 和其它服务。NodeContext 应优先组合/复用现有能力，不能平行创建 NodeDatabase / NodeRouter。

#### PLANNED GAP — 当前没有 Node 专用的统一配置与组合根

当前 main 尚无 `NodeConfig` / `NodeContext` 作为 Node 子系统统一依赖边界。具体代码位置必须在 READY Audit 时决定。

### 3. Entry / Starting Point

实现前至少重新检查：

```text
src/main.rs :: main
src/main.rs :: run_async_server
crates/server/src/lib.rs :: AppState
crates/server/src/lib.rs :: start_server / create_app
```

以及当时 workspace 中已经存在的 Settings / Database / Service construction path。

### 4. Reuse Targets / Do Not Recreate

#### Reuse

- 现有顶层 process bootstrap；
- 现有 Settings 语义；
- 现有 Database 类型与初始化路径；
- 已存在的 Service / Router handles；
- workspace 现有 `Arc` / async ownership 模式。

#### Do Not Recreate

```text
NodeSettingsDatabase
NodeDatabase
NodeRouter
second env/bootstrap loader
global mutable Node singleton
business-service container with hidden side effects
```

### 5. Scope

#### Allowed

- 最小 `NodeConfig`；
- 最小 `NodeContext` / composition root；
- 必需的 shared handle 类型和 wiring；
- 对 required / optional dependency 的明确区分；
- 初始化错误传播；
- 与 composition root 直接相关的 targeted tests。

#### Avoid

- NODE-003 的 Server / Router Node profile；
- HardwareProfile；
- Model Manifest / Resolver；
- Download / Artifact preparation；
- llama.cpp Runtime；
- child-process lifecycle；
- Local Channel registration；
- Billing / Auth / quota 语义；
- 新 Database schema；
- Context 内业务方法膨胀。

### 6. Behavior Contract

#### Inputs

- 已完成 NODE-001 生命周期初始化的 Node Core；
- process/environment 中经现有 bootstrap 认可的配置来源；
- 当前 main 已存在、且 Node 后续真正需要共享的服务构造能力。

#### Outputs

`NodeConfig`：只表达 Node runtime 必需配置，不复制业务数据库内容。  
`NodeContext`：作为 Node 的唯一 composition root，显式持有或引用共享依赖。

#### Ownership

NodeContext owns：

- Node 级依赖组合关系；
- 共享对象的明确生命周期引用；
- 配置到依赖构造所需的最小 wiring。

NodeContext does not own：

- routing decisions；
- model selection；
- download execution；
- runtime argument selection；
- child-process lifecycle；
- billing/auth business rules。

#### Side Effects

允许：构造 Node 所需共享对象、读取现有配置源。  
禁止：隐式创建平行 Database / Router、执行模型下载、启动 Runtime 或修改外部 API 行为。

### 7. Failure / Forbidden Fallbacks

缺少 required config / dependency：明确失败，不用默认值掩盖必需配置。  
共享依赖初始化失败：向上传播，不返回半初始化 Context。  
optional capability 缺失：必须显式表达 unavailable / None，不伪造可用实例。

禁止：

```text
silently create a second Database
silently create a second Router
fall back to global mutable singleton
let each subsystem reload config independently
put model/download/process behavior into NodeContext
pull NODE-003+ responsibilities into this Issue
```

### 8. Impact / Invariants

```text
persistence: no new schema
external_calls: none required by the contract itself
billing_usage_quota: none
auth_authorization: none
routing_provider: none
concurrency_transactions: shared dependency ownership only
public_api_cli: no new public command beyond NODE-001
process_runtime_lifecycle: composition only
```

必须保持：

- `INV-WORKSPACE-001` — shared dependency versions / workspace wiring 继续遵循现有规则；
- `INV-RUNTIME-001` — 现有 `server` / `router` startup 不因 NodeContext 被改写；
- `INV-RUNTIME-002` — 不通过 NodeContext 创建第二个统一 Server。

Candidate architecture invariant：

> **Node 只有一个明确的 composition root；业务模块不得绕过它自行构造平行核心依赖。**

### 9. Dependencies

前置：`NODE-001`。  
直接后续：`NODE-003`、`NODE-101` 及需要共享 Node 依赖的后续能力。

### 10. Stop Conditions

```text
STOP IF:
- current main already has an authoritative Node config/context abstraction with different ownership
- implementation requires a second Database / Router / Settings store
- Context must contain routing, download, model or process business logic to make progress
- required dependency ownership cannot be determined from current main
- implementation changes Billing / Auth / Provider routing semantics
- an INV-* must change without explicit architecture authorization
- scope must be widened into NODE-003 or later Node issues
```

触发时必须报告冲突，并保持所有越界代码未修改。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] `NodeConfig` 有明确、最小、可测试的配置合同。
- [ ] `NodeContext` 成为 Node 唯一明确的 composition root。
- [ ] required / optional dependencies 的语义明确。
- [ ] 依赖初始化失败不会产生“半可用” Context。
- [ ] 后续 Node 模块可以通过显式依赖获得所需共享对象。

### ✅ 边界保护

- [ ] 未创建第二套 Settings、Database、Router 或 process bootstrap。
- [ ] Context 内未加入 Router / Resolver / Download / Runtime / Process 业务逻辑。
- [ ] 未提前实现 NODE-003 及后续 Issue。
- [ ] 未引入全局可变 Node singleton 作为依赖逃生口。

### ✅ 回归与验证

- [ ] 有 targeted tests 覆盖正常构造、required dependency failure、optional dependency unavailable。
- [ ] 现有 `server` / `router` startup 行为保持不变。
- [ ] `INV-WORKSPACE-001`、`INV-RUNTIME-001`、`INV-RUNTIME-002` 保持成立。
- [ ] current-main Task Contract 明确列出真实 construction path 和改动文件。

### ✅ 工程流程

- [ ] 开发前完成 current-main Evidence Audit。
- [ ] 对应 Engineering Issue 已通过 READY Gate。
- [ ] 实现只通过分支 + Pull Request 进入 `main`。
- [ ] PR 中能说明依赖所有权，没有靠隐藏 fallback 扩大范围。


---

## 第四层：人类验收（Human Acceptance）

> 本节由 [Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/) 生成。机器测试、CI 或 AI Review 不能替代这里的人工验收。

### NODE-002 — Node 配置与共享上下文

**验收者：** 架构负责人 + Runtime 工程师。

**人工步骤：**
1. 用一份最小合法 Node 配置启动 Node。
2. 故意缺失一个必需配置，确认启动失败原因清晰。
3. 查看运行诊断或调试输出，确认核心依赖来自同一个 NodeContext / composition root，而不是多个模块各自重新创建 Database / Router / Settings。
4. 修改一个 Node 配置值并重启，确认所有依赖该值的模块看到一致结果。

**人类通过标准：** 配置来源唯一、错误可解释、共享依赖只初始化一次，Context 不表现为业务逻辑容器。

**人工判定失败：** 不同模块读到不同配置、缺失配置被隐藏默认值掩盖、出现第二份 Database/Router/Settings，或 Context 开始承担下载/路由/进程业务。

**建议证据：** 正常启动记录 + 缺失配置错误 + 初始化日志/诊断。
