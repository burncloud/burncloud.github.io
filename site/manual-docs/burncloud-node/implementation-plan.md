---
title: "BurnCloud Node 实施计划"
slug: /burncloud-node/implementation-plan/
hide_table_of_contents: false
---

# BurnCloud Node 实施计划

本文档定义 BurnCloud Node v0.1 的实施边界与产品行为。

> **BurnCloud Node 不是一个需要用户手工下载、启动、停止模型的本地模型管理器。用户只声明 `model`；BurnCloud 负责决定当前请求走 Local 还是现有 Provider，并在后台把可本地运行的模型自动准备成 READY Local Channel。**

## 1. 核心产品合同

用户只需要继续调用现有 BurnCloud API：

```text
POST http://localhost:3000/v1/...
model = qwen-4b
```

用户不需要知道或管理：

```text
GGUF 文件
量化版本
Hugging Face 地址
llama-server 路径
启动参数
内部端口
PID / Child Handle
下载任务 ID
启动 / 停止命令
```

BurnCloud 自动管理这些内部事实。

## 2. 请求时行为

### 场景 A：本地模型已经 READY

```text
/v1 request: qwen-4b
      ↓
Local Channel READY + healthy
      ↓
Existing ModelRouter
      ↓
优先选择 Local Channel
      ↓
本地推理响应
```

“本地存在”不等于“本地可用”。只有真实 `READY + healthy` 的 Runtime 才能成为可路由 Local Channel。

### 场景 B：本地没有，但现有 Provider 有该模型

```text
/v1 request: qwen-4b
      ↓
Local not READY
      +
Provider qwen-4b available
      ↓
当前请求立即走 Provider
      ↓
同时异步产生一个 Model Demand
      ↓
后台自动 Resolve → Download → Verify → Start → READY
      ↓
注册 Local Channel
      ↓
后续请求自然优先 Local
```

**当前请求不能等待大型模型下载。** Provider fallback 与后台本地准备并行发生。

### 场景 C：Local 和 Provider 都暂时不可用，但本机可以运行

```text
/v1 request: qwen-4b
      ↓
no current route candidate
      ↓
Model Demand accepted
      ↓
background preparation active
      ↓
503 MODEL_PREPARING
Retry-After: ...
```

BurnCloud 明确告诉客户端模型正在准备，而不是返回模糊的“模型不存在”。

### 场景 D：本机无法准备模型

如果没有可立即服务的 Provider，并且本地准备被真实资源条件阻止，返回结构化原因，例如：

```text
INSUFFICIENT_VRAM
INSUFFICIENT_RAM
INSUFFICIENT_DISK
UNSUPPORTED_RUNTIME
NO_COMPATIBLE_VARIANT
ARTIFACT_NOT_AVAILABLE
```

如果 Provider 已成功服务当前请求，本地准备失败不应破坏正常响应；失败原因进入 Node 的结构化诊断 / 状态事实。

## 3. 最重要的架构边界

BurnCloud Node 必须把“当前请求怎么走”和“未来本地模型怎么 READY”分开。

```text
                 /v1 request
                     ↓
             Existing ModelRouter
              /              \
       Local READY           Provider
          Channel             Channel
              \              /
               \            /
                 response

同时：

Observed Model Demand
        ↓
Model Demand Reconciler
        ↓
Resolver
        ↓
Resource / Disk checks
        ↓
Model Preparation
        ↓
Runtime / Process
        ↓
READY
        ↓
Local Channel
```

### Router 负责

- 选择当前可用 Channel；
- 保持现有 priority / availability / scorer / affinity / failover 语义；
- Local READY 后把它当正常 Channel 候选。

### Router 不负责

- 下载模型；
- 选择 GGUF；
- 启动 llama.cpp；
- 等待模型 READY；
- 管理 PID；
- 重试下载。

### Model Demand Reconciler 负责

- 观察模型需求；
- 将并发需求去重；
- 驱动本地模型从 `ABSENT` 收敛到 `READY`；
- 失败时保留可诊断状态；
- Node 重启后清理 stale local state，并根据新的真实需求继续收敛。

硬约束：

```text
1000 requests for qwen-4b
        ↓
1 logical Model Demand
        ↓
1 active preparation pipeline
        ↓
1 managed runtime instance
        ↓
1 Local Channel identity
```

## 4. Node 与现有 BurnCloud 的关系

BurnCloud Node **不是第二套 BurnCloud**。必须复用现有：

```text
Server
Router
Database
Settings
Models
Download
Monitor
Inference prototype
Logging
Auto Update
```

明确禁止：

```text
第二个 HTTP Server
第二个 Router
第二个 Downloader
第二个 Database
第二套模型系统
```

## 5. 七项核心能力

```text
1. Node Core
2. Hardware Profile
3. Model Resolver
4. Model Preparation
5. Runtime / Process Lifecycle
6. Local Channel Integration
7. Model Demand Reconciliation
```

其中前六项提供执行能力，第七项把 `/v1` 中真实出现的模型需求自动收敛成 Local READY 能力。

## 6. Node Core

Node Core 是薄的编排 / lifecycle 层：初始化 Node、共享上下文、组合现有 Server / Router、协调子系统并处理 shutdown。

Node Core 不进入每个 inference request 的数据面，不实现第二个 Router，也不直接承担下载或 llama.cpp 细节。

## 7. Hardware Profile

Node 维护唯一 authoritative Hardware Profile，并区分静态硬件身份与动态可用资源：

```text
OS / CPU / RAM / Disk
GPU Vendor / Model / Count / VRAM
Driver
Available RAM / VRAM / Disk
Runtime Compatibility
```

Hardware 层产生事实；Resolver 才做模型选择。

## 8. Model Resolver

Resolver 输入：

```text
Model ID
+
Model Manifest
+
Hardware Profile
+
Resource Snapshot
+
Runtime Capabilities
```

输出 `ResolvedModel` 或结构化失败诊断。

Resolver 只选择，不下载、不启动、不路由。

v0.1 必须随 BurnCloud 提供一组真实、可用、版本明确的 curated Model Manifest；不能只交付 Schema 和测试 fixture。

## 9. Model Preparation

Model Preparation 复用 Model Service + Download Manager，把 `ResolvedModel` 收敛成经过验证的 READY Artifact。

它必须：

- 由后台 Model Demand 自动触发；
- 并发去重；
- 下载前检查磁盘空间；
- 支持断点恢复；
- 下载完成后完成完整性校验；
- 不在 `/v1` 请求线程内阻塞等待大型下载。

## 10. Runtime / Process Lifecycle

v0.1 首先支持：

```text
GGUF + llama.cpp / llama-server
```

BurnCloud 负责 Runtime 可用性、ProcessSpec、内部端口、spawn、readiness、health、stop、crash、bounded restart 和日志。

```text
Process Spawned != Model READY
```

用户不需要手工执行 llama-server，也不需要管理进程退出和关闭。

## 11. Local Channel Integration

只有 READY Runtime 才能注册为 existing Channel / Ability：

```text
READY Runtime
   ↓
127.0.0.1:<port>
   ↓
Local Channel / Ability
   ↓
Existing ModelRouter
```

Local 默认应通过现有 Router 的合法 priority / availability 机制获得本地优先，而不是通过 `if local { bypass_router }` 特判。

Runtime stop / crash / unhealthy 后必须自动失去 routable 状态。

## 12. Model Demand Reconciliation

这是自动化产品体验的关键层。

```text
Observed model=qwen-4b
      ↓
Demand dedup
      ↓
Local READY?
  ├─ yes → no-op
  └─ no
       ↓
Preparation already active?
  ├─ yes → no-op
  └─ no
       ↓
Resolve local candidate
       ↓
Check hardware / disk / runtime
       ↓
Prepare Artifact
       ↓
Start Runtime
       ↓
READY
       ↓
Register Local Channel
```

它是 orchestration，不是新的 Router。

## 13. Node v0.1 暂不实施

- BurnCloud Network / P2P；
- Node-to-Node Routing；
- 多机任务调度；
- 复杂 GPU Scheduler；
- 大规模 multi-runtime framework；
- inference request 同步阻塞等待大型模型下载；
- 第二套 Router / Gateway / Downloader / Database；
- 要求用户先进入管理页手工“下载 → 启动 → 运行”模型。

## 14. 实施阶段

### Phase 1：Node Core
NODE-001~003。

### Phase 2：Hardware + Resolver
NODE-101~103、NODE-201~204。

### Phase 3：Model Preparation
NODE-301~303。

### Phase 4：Runtime + Process
NODE-400~404。

### Phase 5：Local Channel
NODE-501~502。

### Phase 6：Demand Reconciliation + E2E
NODE-504 驱动自动收敛，NODE-503 做最终系统级验收。

## 15. Node v0.1 完成定义

必须至少稳定通过四个系统场景：

1. **Local READY**：请求直接通过 existing Router 使用 Local Channel。
2. **Local absent + Provider available**：当前请求由 Provider 正常响应，同时后台只启动一条本地准备链；本地 READY 后后续请求自动优先 Local。
3. **Local absent + Provider unavailable + local feasible**：返回 `MODEL_PREPARING`，后台完成后重试可成功。
4. **Local impossible**：没有 Provider 可服务时，返回结构化的 Hardware / Disk / Runtime / Artifact 失败原因。

同时：

- 用户只声明 `model`；
- 用户不提供 GGUF path / port / PID / llama.cpp args；
- 用户不手工下载、启动、停止模型；
- 并发请求不会产生重复下载或重复 Runtime；
- 未 READY 模型不接真实流量；
- Local 失效后 Provider failover 仍按现有 Router 语义工作；
- 不破坏现有 API / Auth / Billing 行为。

> **BurnCloud Node v0.1 的最终目标不是“能启动一个本地模型”，而是“用户只调用 `/v1`，BurnCloud 自动管理模型实际在哪里、何时下载、何时启动、何时切换 Local、何时失败和何时退出”。**
