---
title: "BurnCloud Node 实施计划"
slug: /burncloud-node/implementation-plan/
hide_table_of_contents: false
---

# BurnCloud Node 实施计划

本文档用于说明：**基于现有 `burncloud/burncloud` 代码，BurnCloud Node 已经具备哪些基础能力、还缺少哪些关键能力，以及接下来按什么顺序补齐。**

本文档不是重新设计一套 BurnCloud，也不是把所有未来设想一次性加入 Node。

BurnCloud Node 的实施原则是：

> **复用现有 BurnCloud，补齐本地 AI Runtime 链，最终形成一个可以独立运行、管理本地模型并通过现有 Router 提供稳定 AI API 的 Node。**

## 1. 本次开发目标

BurnCloud Node v0.1 首先完成一条稳定的本地模型执行链：

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

## 2. Node 与现有 BurnCloud 的关系

BurnCloud Node **不是第二套 BurnCloud**。

现有 `burncloud/burncloud` 已经拥有可以直接复用的基础能力：

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

Node 应在这些能力之上增加本地节点编排层，并补齐目前不完整的 Local Runtime 能力。

明确不做：

```text
第二个 HTTP Server
第二个 Router
第二个 Downloader
第二个 Database
第二套模型系统
```

## 3. 当前已经具备的能力

### 3.1 Server / API 入口

现有 `burncloud-server` 已经负责统一 Axum 应用、管理 API、内部 API、Data Plane fallback、Request ID、Tracing、CORS 和安全边界。

**结论：** Node 不重新创建 HTTP Gateway；复用现有 Server / Router 作为稳定 API 边界。

状态：**已存在，主要复用。**

### 3.2 Model Router

现有 `burncloud-router` 已经具备基于 Model、Channel Ability、可用性、优先级、调度器、Affinity 和 Failover 的路由能力。

**结论：** 不创建 `NodeRouteEngine`。本地模型应作为现有 Router 可以选择的一种 Channel 进入数据面。

状态：**已存在，主要复用。**

### 3.3 Local Inference 雏形

现有 `InferenceService` 已经可以启动 `llama-server`、保存进程句柄、等待 `/v1/models` 健康检查，并在启动成功后创建 Local Channel 与 Channel Ability。

这证明以下路径已经可行：

```text
Local Runtime
   ↓
Local Endpoint
   ↓
Channel
   ↓
Existing Router
```

但当前 `InferenceService` 同时承担 Runtime、Process、Health Check 和 Router Registration 等多个职责，需要继续整理。

状态：**已有原型，需要拆清职责并增强。**

### 3.4 Models / Download / Monitor

现有 BurnCloud 已经具备模型记录、Hugging Face 文件发现、GGUF 筛选、下载 URL、aria2 下载、断点续传、下载状态恢复，以及 CPU / Memory / Disk 监控等能力。

**结论：** Node 应复用这些能力，不重写下载器和基础监控。

## 4. 需要补齐的六项核心能力

```text
1. Node Core
2. Hardware Profile
3. Model Resolver
4. Model Preparation
5. Runtime / Process Lifecycle
6. Local Channel Integration
```

这六项共同构成本地 Node 的最小完整闭环。

## 5. Node Core

Node Core 是 BurnCloud Node 的编排层。

主要负责：

- 初始化 Node 所需组件
- 读取 Node 配置
- 建立共享状态
- 初始化 Hardware Profile
- 协调模型准备流程
- 协调 Runtime / Process 生命周期
- 将 READY 的本地模型接入现有 Router
- 处理 Node 启动与关闭

Node Core 不实现新的 HTTP Router、Provider Router、下载器，也不直接承担 llama.cpp 细节。

## 6. Hardware Profile

Node 需要统一的 `HardwareProfile`，至少覆盖：

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

关键原则：**Node 内只保留一份权威 Hardware Profile。** Resolver、Runtime、诊断和未来 UI 都读取同一份硬件事实。

## 7. Model Resolver

用户面对逻辑模型：

```text
qwen3-8b
```

Node 内部根据：

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

`ResolvedModel` 至少应明确 Canonical Model ID、Variant、Format、Quantization、Artifact、Runtime 和 Resource Requirements。

关键原则：

> **Resolver 负责选择，不负责下载，不负责启动进程。**

## 8. Model Preparation

Model Preparation 把 `ResolvedModel` 变成经过验证、可供 Runtime 使用的本地 Artifact。

优先复用：

```text
Model Service
+
Download Manager
```

主要职责：判断 Artifact 是否存在、避免重复下载、追踪状态、完成校验，并维护 Local Model State。

## 9. Runtime Manager

Runtime Manager 回答：**这个模型应该用什么 Runtime、以什么参数运行？**

Node v0.1 首先只支持：

```text
GGUF
+
llama.cpp / llama-server
```

Runtime Manager 负责查找或准备 Runtime、检查兼容性、构建启动参数和环境变量，并生成 Process Spec。

Runtime Manager 不长期持有 PID 或进程句柄。

## 10. Process Manager

Process Manager 只负责运行中的模型进程：

- 内部端口
- Spawn Process
- PID / Process Handle
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

只有完成 readiness 与 health check 后，模型才允许注册到 Router 接收真实请求。

## 11. Local Channel Integration

本地模型进入 READY 后：

```text
Local Model READY
      ↓
127.0.0.1:<port>
      ↓
Local Channel
      ↓
Channel Ability
      ↓
Existing ModelRouter
```

本地模型不是 Router 的特殊旁路。Router 不需要知道模型运行在 llama.cpp、vLLM 还是其他 Runtime 上。

## 12. Node v0.1 暂不实施

为了控制边界，以下能力暂不作为 v0.1 前置条件：

- BurnCloud Network
- P2P Transport
- Node-to-Node Routing
- 多机任务调度
- 复杂 GPU Resource Scheduler
- 同时支持大量 Runtime
- 第一次推理请求自动阻塞等待大型模型下载
- 第二套 Router / Gateway / Downloader / Database

## 13. 实施阶段

### Phase 1：Node Core

建立 Node 生命周期、状态、配置入口，以及与现有 Server / Router 的组合方式。

### Phase 2：Hardware + Model Resolver

完成 Hardware Profile、GPU / VRAM / Driver detection、Model Manifest、Model Resolver 和 ResolvedModel。

### Phase 3：Model Preparation

复用 Model Service 与 Download Manager，完成 Artifact 状态、下载去重、校验和 Local Model State。

### Phase 4：Runtime + Process

完成 llama.cpp Runtime Adapter、Process Spec、内部端口、Readiness / Health、停止、恢复和日志。

### Phase 5：Local Channel Integration

完成 Local Channel / Channel Ability 注册、健康状态联动和完整请求链验证。

## 14. Node v0.1 完成定义

只有以下链路稳定运行，才认为 BurnCloud Node v0.1 完成：

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
- 未 READY 的模型不能接收真实路由流量
- 不破坏现有 Provider Routing
- 不破坏现有 API / Auth / Billing 行为

## 15. 实施边界

在 Node 开发过程中，任何新增实现都优先回答两个问题：

1. 现有 BurnCloud 是否已经拥有同类能力？
2. 这个能力是否真的属于 Node v0.1 的必要闭环？

如果现有能力可以复用，就不创建第二套实现；如果功能不属于 v0.1 必要闭环，就暂不扩大架构。
