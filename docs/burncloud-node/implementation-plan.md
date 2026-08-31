---
title: "BurnCloud Node 实施计划"
hide_table_of_contents: false
---

# BurnCloud Node 实施计划

本文档用于说明：**基于现有 `burncloud/burncloud` 代码，BurnCloud Node 已经具备哪些基础能力、还缺少哪些关键能力，以及接下来按什么顺序补齐。**

本文档不是重新设计一套 BurnCloud，也不是把所有未来设想一次性加入 Node。

BurnCloud Node 的实施原则是：

> **复用现有 BurnCloud，补齐本地 AI Runtime 链，最终形成一个可以独立运行、管理本地模型并通过现有 Router 提供稳定 AI API 的 Node。**

---

## 1. 本次开发目标

BurnCloud Node v0.1 的目标不是实现 BurnCloud Network，也不是重新实现 Gateway、Router、Downloader 或 Database。

本次开发首先完成一条稳定的本地模型执行链：

```text
Model ID
   ↓
Hardware Profile
   ↓
Model Resolver
   ↓
Model Preparation
   ↓
Runtime Preparation
   ↓
Process Lifecycle
   ↓
Local Endpoint
   ↓
Local Channel
   ↓
Existing BurnCloud Router
   ↓
http://localhost:3000
```

完成后，用户不需要手工管理 GGUF 文件名、内部端口、PID 或 llama.cpp 启动参数。

---

## 2. BurnCloud Node 与现有 BurnCloud 的关系

BurnCloud Node **不是第二套 BurnCloud**。

现有 `burncloud/burncloud` 已经拥有大量可以直接复用的基础能力：

```text
burncloud/burncloud
│
├── Server
├── Router
├── Database
├── Settings
├── Models
├── Download
├── Monitor
├── Inference
├── Logging
└── Auto Update
```

BurnCloud Node 应当在这些能力之上增加一个本地节点编排层，并补齐目前不完整的 Local Runtime 能力。

因此，Node 的主要职责是：

```text
Node Core
   ↓
组织已有 BurnCloud 组件
   +
补齐 Local Model Runtime
```

而不是：

```text
Node
├── 第二个 HTTP Server
├── 第二个 Router
├── 第二个 Downloader
├── 第二个 Database
└── 第二套模型系统
```

---

## 3. 当前已经具备的能力

以下能力在现有 BurnCloud 中已经存在，Node 应优先复用。

### 3.1 统一 Server / API 入口

现有 `burncloud-server` 已经负责统一 Axum 应用、管理 API、内部 API、Data Plane fallback、Request ID、Tracing、CORS 和安全边界。

**实施结论：** Node 不重新创建 HTTP Gateway；Node 应复用现有 Server / Router 作为稳定 API 边界。

状态：**已存在，主要复用。**

### 3.2 Model Router

现有 `burncloud-router` 已经具备基于 Model、Channel Ability、可用性、优先级、调度器、Affinity 和 Failover 的路由能力。

**实施结论：** 不创建 `NodeRouteEngine`。本地模型应该作为现有 Router 可以选择的一种 Channel 进入数据面。

状态：**已存在，主要复用。**

### 3.3 Local Inference 雏形

现有 `InferenceService` 已经可以：

- 启动 `llama-server`
- 保存运行中的进程句柄
- 等待 `/v1/models` 健康检查
- 在启动成功后创建 Local Channel
- 创建 Channel Ability
- 在停止时注销 Local Channel

这证明了以下路径是可行的：

```text
Local Runtime
   ↓
Local Endpoint
   ↓
Channel
   ↓
Existing Router
```

但当前 `InferenceService` 同时承担 Runtime、Process、Health Check 和 Router Registration 等多个职责，仍需整理。

状态：**已有原型，需要拆清职责并增强。**

### 3.4 模型服务

现有 Model Service 已经具备：

- 模型记录管理
- Hugging Face 模型查询
- 模型文件列表
- GGUF 文件筛选
- 模型数据目录
- 下载 URL 构造
- 模型删除和本地文件清理

状态：**已存在，需要被 Node Model Preparation 复用。**

### 3.5 下载能力

现有 Download Manager 已经具备：

- aria2 下载
- 断点续传
- Pause / Resume / Remove
- 下载进度
- 数据库状态记录
- 重启后恢复未完成下载

状态：**已存在，不重新开发 Node Downloader。**

### 3.6 系统监控

现有 System Monitor 已经具备 CPU、Memory、Disk 等系统指标能力。

状态：**已有基础，需要扩展为 Node 使用的 Hardware Profile。**

---

## 4. BurnCloud Node 需要补齐的核心能力

结合现有代码，本次 Node 工作重点集中在以下六项。

```text
1. Node Core
2. Hardware Profile
3. Model Resolver
4. Model Preparation
5. Runtime / Process Lifecycle
6. Local Channel Integration
```

这六项共同构成本地 Node 的最小完整闭环。

---

## 5. Node Core

Node Core 是 BurnCloud Node 的编排层。

它负责组织 Node 生命周期，而不是重新实现具体业务组件。

### 主要职责

- 初始化 Node 所需组件
- 读取 Node 配置
- 建立共享状态
- 初始化 Hardware Profile
- 协调模型准备流程
- 协调 Runtime / Process 生命周期
- 将 READY 的本地模型接入现有 Router
- 处理 Node 启动与关闭

### 不负责

- 不实现新的 HTTP Router
- 不实现新的 Provider Router
- 不自行下载文件
- 不直接实现 llama.cpp 细节
- 不直接持有所有底层业务逻辑

Node Core 应保持为一个较薄的 Orchestration Layer。

---

## 6. Hardware Profile

现有 System Monitor 提供基础系统信息，但 Model Resolver 需要一个稳定、统一的硬件事实对象。

Node 需要补齐统一的 `HardwareProfile`，至少覆盖：

```text
OS
CPU Architecture
CPU Cores
RAM
Available RAM
GPU Vendor
GPU Model
GPU Count
VRAM
Available VRAM
Driver
Runtime Compatibility
Disk Free Space
```

### 关键原则

Node 内只能有一个权威 Hardware Profile。

Model Resolver、Runtime、诊断和未来 UI 都应读取同一份硬件事实，而不是各自重新检测硬件。

### 当前缺口

- GPU 识别
- VRAM 识别
- Driver 信息
- CUDA / Runtime compatibility
- 静态信息与动态资源信息的刷新策略

---

## 7. Model Resolver

Model Resolver 是本次 Node 最重要的新能力之一。

当前本地推理仍然要求上层明确提供具体模型文件路径和 Runtime 参数。Node 的目标是让用户请求**逻辑模型**，而不是具体 Artifact。

用户面对：

```text
qwen3-8b
```

Node 内部解析：

```text
Model ID
  +
Hardware Profile
  +
Model Manifest
  +
Local Model State
  +
Runtime Capabilities
        ↓
Resolved Model
```

`ResolvedModel` 应明确：

- Canonical Model ID
- Variant
- Model Format
- Quantization
- Artifact
- Runtime
- Resource Requirements

### 关键原则

> **Resolver 负责选择，不负责下载，不负责启动进程。**

---

## 8. Model Preparation

Model Preparation 负责把 `ResolvedModel` 变成一个经过验证、可供 Runtime 使用的本地 Artifact。

它应优先复用现有：

```text
Model Service
+
Download Manager
```

### 主要职责

- 判断 Artifact 是否已存在
- 避免重复下载同一个 Artifact
- 发起下载
- 追踪下载状态
- 完成后校验 Artifact
- 维护 Local Model State
- 输出可供 Runtime 使用的本地路径

### 不重新实现

- HTTP 下载器
- aria2 管理
- 下载状态数据库

---

## 9. Runtime Manager

Runtime Manager 回答的问题是：

> **这个模型应该用什么 Runtime、以什么参数运行？**

Node v0.1 首先只支持：

```text
GGUF
+
llama.cpp / llama-server
```

Runtime Manager 负责：

- 查找或准备 Runtime
- 判断 Runtime 与硬件是否兼容
- 判断 Runtime 是否支持目标模型 Format
- 构建启动参数
- 构建环境变量
- 生成 Process Spec

Runtime Manager 不应该长期持有 PID 或进程句柄。

后续可以再扩展：

- vLLM
- SGLang
- 其他 Runtime

但这些不属于 Node v0.1 的完成条件。

---

## 10. Process Manager

Process Manager 只负责运行中的模型进程。

### 主要职责

- 分配内部端口
- Spawn Process
- 保存 PID / Process Handle
- Readiness Check
- Health Check
- Stop
- Crash Detection
- Restart Policy
- Runtime Logs

必须明确：

```text
Process Spawned
      ≠
Model Ready
```

只有完成：

```text
spawn
  ↓
process alive
  ↓
readiness success
  ↓
health success
  ↓
READY
```

模型才允许被注册到 Router 接收真实请求。

---

## 11. Local Channel Integration

当本地模型进入 READY 状态后，将其接入现有 BurnCloud Router。

目标流程：

```text
Local Model READY
      ↓
Internal Endpoint
127.0.0.1:<port>
      ↓
Local Channel
      ↓
Channel Ability
      ↓
Existing ModelRouter
```

### 关键原则

本地模型不是 Router 的特殊旁路。

Router 不需要知道模型到底运行在 llama.cpp、vLLM 还是其他 Runtime 上。

对 Router 来说，本地 Runtime 应尽可能表现为一个正常、健康、可调度的 Route Target / Channel。

这样可以最大程度复用现有：

- Model Routing
- Priority
- Availability
- Scheduling
- Failover
- Logging

---

## 12. Node v0.1 暂不实施的内容

为了避免再次扩大系统边界，以下能力暂不作为 Node v0.1 的前置条件：

- BurnCloud Network
- P2P Transport
- Node-to-Node Routing
- 多机任务调度
- 复杂 GPU Resource Scheduler
- 同时支持大量 Runtime
- 自动把第一次推理请求阻塞到大型模型下载完成
- 新建第二套 Router
- 新建第二套 Gateway
- 新建第二套 Download System
- 新建第二套 Database / State System

这些能力只有在本地 Node 的基本执行链稳定后，才进入下一阶段讨论。

---

## 13. 实施阶段

### Phase 1：Node Core

目标：建立 BurnCloud Node 的生命周期和编排边界。

需要完成：

- Node 初始化
- Node 状态
- Node 配置入口
- 启动 / 停止生命周期
- 与现有 Server / Router 的组合方式

### Phase 2：Hardware + Model Resolver

目标：用户只提供逻辑 Model ID，Node 能确定本机应该运行哪个 Variant。

需要完成：

- Hardware Profile
- GPU / VRAM / Driver detection
- Model Manifest
- Model Resolver
- ResolvedModel
- 明确的 Resolver 错误

### Phase 3：Model Preparation

目标：ResolvedModel 可以被稳定准备成本地 Artifact。

需要完成：

- 复用 Model Service
- 复用 Download Manager
- Artifact 状态
- 下载去重
- 完成校验
- Local Model State

### Phase 4：Runtime + Process

目标：本地 Artifact 可以稳定变成一个 READY 的内部推理 Endpoint。

需要完成：

- llama.cpp Runtime Adapter
- Process Spec
- Internal Port
- Process Lifecycle
- Readiness / Health
- Stop / Recovery
- Logs

### Phase 5：Local Channel Integration

目标：本地 READY 模型通过现有 BurnCloud Router 对外提供服务。

需要完成：

- Local Channel 注册
- Channel Ability 注册
- Runtime 停止后的注销
- Health 与 Router Availability 联动
- 完整请求链验证

---

## 14. Node v0.1 完成定义

只有以下完整链路可以稳定运行，才认为 BurnCloud Node v0.1 完成：

```text
选择逻辑模型
      ↓
检测本机硬件
      ↓
选择兼容 Variant
      ↓
准备 / 下载 Artifact
      ↓
准备 llama.cpp Runtime
      ↓
启动模型进程
      ↓
Readiness + Health Check
      ↓
注册 Local Channel
      ↓
Existing BurnCloud Router
      ↓
http://localhost:3000/v1/...
      ↓
客户端获得正常模型响应
```

同时必须满足：

- 用户不需要填写 GGUF 绝对路径
- 用户不需要手工选择内部端口
- 用户不需要管理 PID
- 用户不需要手工执行 llama-server
- Node 重启后不会把不存在的模型错误标记为 READY
- 未 READY 的模型不能接收真实路由流量
- 不破坏现有 Provider Routing
- 不破坏现有 API / Auth / Billing 行为

---

## 15. 实施过程中必须保持的边界

为了防止 BurnCloud Node 开发再次制造第二套系统，本计划先固定以下边界：

```text
1. Existing Server remains the API container.
2. Existing Router remains the routing engine.
3. Local model enters Router through a Local Channel.
4. Existing Download Manager remains the download engine.
5. Hardware facts must converge into one HardwareProfile.
6. Model Resolver selects but does not download.
7. Runtime Manager prepares execution but does not own long-lived process state.
8. Process Manager owns process lifecycle and readiness.
9. Node Core orchestrates components but does not absorb their implementation.
10. BurnCloud Network is not a prerequisite for Node v0.1.
```

如果未来需要改变这些边界，应作为明确的架构变更单独讨论，而不应在普通功能开发中顺手修改。

---

## 16. 当前实施重点

当前最重要的不是增加更多功能，而是完成以下收敛：

```text
Existing BurnCloud
        ↓
识别可复用能力
        ↓
补齐 Local Runtime 缺口
        ↓
统一 Local Channel
        ↓
复用 Existing Router
        ↓
形成 BurnCloud Node v0.1
```

下一步实施讨论应从 **Node Core 的职责与边界** 开始，然后按 Phase 1 → Phase 5 顺序逐层展开。