---
title: "BurnCloud Node 实施计划"
slug: /burncloud-node/implementation-plan/
hide_table_of_contents: false
---

# BurnCloud Node 实施计划

本文档用于说明：**基于现有 `burncloud/burncloud` 代码，BurnCloud Node 的产品功能如何被拆成可执行、可验证、可由人最终签收的 Engineering Issue。**

本计划不是第二套 BurnCloud，也不是把所有未来能力一次性加入 Node。

核心原则：

> **复用现有 BurnCloud，补齐本地 AI Runtime 链；每一个 Node 产品功能都必须能追溯到明确 Issue；每一个 Issue 最终必须通过机器验收 + 人类验收。**

## 1. Node v0.1 的产品目标

用户只声明正常 AI 请求与 `model`：

```text
Client /v1 request
      ↓
Local API Gateway
      ↓
Protocol Detection
      ↓
model_id
      ↓
Existing ModelRouter
      ↓
Local READY? / Provider available?
      ↓
current request served
```

并行：

```text
model demand
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
READY Local Channel
    ↓
Existing ModelRouter
```

用户不需要管理 GGUF 文件名、Artifact URL、内部端口、PID、`gpu_layers` 或 llama.cpp 启动命令。

## 2. Node 与现有 BurnCloud 的关系

BurnCloud Node **不是第二套 BurnCloud**。

优先复用：

```text
Server
Router
Database
Settings
Models / ModelService
DownloadManager
Monitor
Inference prototype
Logging
Auto Update
```

明确禁止默认创建：

```text
第二个 HTTP Server
第二个 Gateway
第二个 Router
第二个 Downloader
第二个 Database
第二套模型 / Cache 真相
```

## 3. 七个产品功能与 Issue 覆盖矩阵

BurnCloud Node 首页定义七个核心产品功能。v0.1 Implementation Plan 必须做到 1:1 可追溯，而不能用“现有代码应该已经有”代替验收责任。

| 产品功能 | Implementation Plan | 覆盖状态 |
|---|---|---|
| Local API Gateway | NODE-003 + **NODE-004** + NODE-503 | ✅ 有组合合同、协议兼容 Gate、最终 E2E |
| Protocol Routing | **NODE-004** + NODE-503 | ✅ Raw Proxy / Translator / protocol matrix 有独立责任人 |
| Hardware Detection | NODE-101~103 | ✅ vendor-neutral Profile；v0.1 NVIDIA-first |
| Model Resolver | NODE-201~204 | ✅ Manifest / ID / Variant / Result contract |
| Model Manager | NODE-301~**304** | ✅ state / download / verify / inventory / cache / delete |
| Runtime Manager | NODE-400~401 | ✅ managed llama.cpp + Runtime Adapter / ProcessSpec |
| Process Manager | NODE-402~404 | ✅ admission / spawn / readiness / health / stop / crash / restart / logs |

此外，Node 的核心自动化体验由：

```text
NODE-501 Local Channel registration
NODE-502 health linkage
NODE-504 demand reconciliation
NODE-503 final E2E
```

负责把以上七个能力收敛成“User declares intent; BurnCloud manages reality”。

## 4. Issue Standard 与人类验收

所有 NODE Issue 继承：

- [Canonical Issue Standard](/burncloud-node/implementation-plan/issue-standard/)
- [Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/)

每个 Issue 页面最终必须包含：

```text
第一层：Human Readable Layer
第二层：Machine Executable Specification
第三层：Definition of Done / Machine Verification
第四层：Human Acceptance
```

第四层不是 AI Review，也不是“CI 绿了”。它要求产品负责人、架构负责人或指定工程师按真实产品路径亲自操作并留下证据。

```text
AI says done    != Human accepted
CI green        != Human accepted
Tests pass      != Human accepted
```

## 5. Phase 1 — Node Core + Data Plane Compatibility

| ID | 目标 | 依赖 | 状态 |
|---|---|---|---|
| [NODE-001](./implementation-plan/node-001) | Node 一等启动入口与生命周期 | 无 | PLANNED |
| [NODE-002](./implementation-plan/node-002) | NodeConfig + NodeContext | NODE-001 | PLANNED |
| [NODE-003](./implementation-plan/node-003) | 复用现有 Server / Router 形成 Node 模式 | NODE-001, NODE-002 | PLANNED |
| [NODE-004](./implementation-plan/node-004) | Gateway / Protocol Routing Compatibility Gate | NODE-003 | PLANNED |

NODE-004 是 Compatibility Gate，不是第二 Gateway / Router 的实现授权。

它负责证明：

```text
URL / Path → Protocol Detection
model_id   → Existing ModelRouter
same protocol      → Raw Proxy First
different protocol → Protocol Translator
```

## 6. Phase 2 — Hardware Profile

| ID | 目标 | 依赖 | 状态 |
|---|---|---|---|
| [NODE-101](./implementation-plan/node-101) | canonical HardwareProfile | NODE-002 | PLANNED |
| [NODE-102](./implementation-plan/node-102) | NVIDIA GPU / VRAM / Driver Detection | NODE-101 | PLANNED |
| [NODE-103](./implementation-plan/node-103) | Runtime Compatibility + Resource Snapshot | NODE-101, NODE-102 | PLANNED |

范围明确：

```text
HardwareProfile abstraction = vendor-neutral
v0.1 GPU detection          = NVIDIA-first
AMD / Apple Metal / others  = Future
```

未实现某 GPU Vendor 检测时必须表达 `unsupported / unknown`，不能伪造成“没有 GPU”或填 0。

## 7. Phase 3 — Model Resolver

| ID | 目标 | 依赖 | 状态 |
|---|---|---|---|
| [NODE-201](./implementation-plan/node-201) | Model Manifest + v0.1 curated catalog | NODE-101~103 | PLANNED |
| [NODE-202](./implementation-plan/node-202) | Canonical Model ID / Alias | NODE-201 | PLANNED |
| [NODE-203](./implementation-plan/node-203) | Hardware / Runtime 驱动 Variant 选择 | NODE-201, NODE-202, NODE-103 | PLANNED |
| [NODE-204](./implementation-plan/node-204) | ResolvedModel / ResolutionFailure 合同 | NODE-203 | PLANNED |

关键边界：

> **Resolver 负责选择，不负责下载、不负责启动、不负责当前请求路由。**

## 8. Phase 4 — Model Preparation / Artifact Lifecycle

| ID | 目标 | 依赖 | 状态 |
|---|---|---|---|
| [NODE-301](./implementation-plan/node-301) | Local Artifact State | NODE-204 | PLANNED |
| [NODE-302](./implementation-plan/node-302) | Background Prepare / Disk Admission / Download Dedup | NODE-301, NODE-103, NODE-204 | PLANNED |
| [NODE-303](./implementation-plan/node-303) | Artifact Verification / Failure / Recovery | NODE-302 | PLANNED |
| [NODE-304](./implementation-plan/node-304) | Artifact Inventory / Cache / Safe Delete | NODE-301, NODE-303 | PLANNED |

NODE-304 补齐 Model Manager 产品文档的：

```text
cache
list
delete
status
```

但 v0.1 不建设复杂 LRU、自动容量调度、历史 demand warm-set 或任意文件系统清理器。

## 9. Phase 5 — Runtime + Process

| ID | 目标 | 依赖 | 状态 |
|---|---|---|---|
| [NODE-400](./implementation-plan/node-400) | llama.cpp Runtime 自动可用 | Hardware/Profile + Artifact facts | PLANNED |
| [NODE-401](./implementation-plan/node-401) | llama.cpp Runtime Adapter + ProcessSpec | NODE-303, NODE-400 | PLANNED |
| [NODE-402](./implementation-plan/node-402) | Resource Admission / Port / Spawn | NODE-401 | PLANNED |
| [NODE-403](./implementation-plan/node-403) | Readiness / Health | NODE-402 | PLANNED |
| [NODE-404](./implementation-plan/node-404) | Stop / Crash / Restart / Logs | NODE-402, NODE-403 | PLANNED |

必须保持：

```text
Process Spawned != Model READY
```

只有 readiness / health 成功后才能产生 routable Local Channel。

## 10. Phase 6 — Local Channel + Demand Reconciliation

| ID | 目标 | 依赖 | 状态 |
|---|---|---|---|
| [NODE-501](./implementation-plan/node-501) | READY Runtime 自动注册 Local Channel / Ability | Runtime READY | PLANNED |
| [NODE-502](./implementation-plan/node-502) | Health Linkage / Removal / Recovery | NODE-501, NODE-403/404 | PLANNED |
| [NODE-504](./implementation-plan/node-504) | Model Demand Reconciliation | Resolver + Preparation + Runtime + Channel | PLANNED |
| [NODE-503](./implementation-plan/node-503) | Demand-driven 本地推理完整 E2E | Node v0.1 全部前置 Issue | PLANNED |

当前请求仍由 Existing ModelRouter 决定：

```text
/v1 request
    ↓
Existing ModelRouter
  ├─ Local READY
  └─ Provider
```

后台：

```text
model demand
    ↓
NODE-504
    ↓
Resolve → Prepare → Runtime → READY → Local Channel
```

Reconciler 不是第二个 Router。

## 11. Node v0.1 明确不实施

为了控制边界，以下能力不作为 v0.1 完成条件：

```text
BurnCloud Network
P2P Transport
Node-to-Node Routing
Multi-node Scheduling
AMD / Apple Metal 自动 GPU Detection
复杂 GPU Resource Scheduler
复杂 Artifact LRU / 自动缓存调度
同时支持大量 Runtime
第一次请求同步等待大型模型下载
第二套 Router / Gateway / Downloader / Database
```

### BurnCloud Network 的正确位置

v0.1：

```text
Route Targets
├── Local Runtime
└── External Provider
```

Future：

```text
Existing ModelRouter
└── BurnCloud Network Channel / Route Target
```

Network 未来接入现有 Router，不改变 `URL → Protocol → model_id → Route Engine → Raw Proxy / Translator` 的数据面边界。

## 12. Node v0.1 完成定义

### 机器闭环

```text
normal /v1 request
      ↓
protocol recognized
      ↓
model_id
      ↓
Existing ModelRouter
      ↓
current request served when reality allows
```

并行：

```text
model demand
      ↓
HardwareProfile
      ↓
ResolvedModel
      ↓
Artifact Prepare / Verify
      ↓
Managed llama.cpp Runtime
      ↓
Process Spawn
      ↓
Readiness + Health
      ↓
Local Channel
      ↓
Existing ModelRouter
```

同时必须满足：

- 用户不填写 GGUF 绝对路径；
- 用户不手工选择 Variant；
- 用户不手工安装/寻找 llama-server 作为正常流程；
- 用户不选择内部端口；
- 用户不管理 PID；
- 相同 model demand 不产生重复下载 / Runtime / Channel；
- Provider 可用时当前请求不等待 Local 下载；
- 无 Provider但正在准备时返回 `MODEL_PREPARING`；
- 不可准备时返回真实 Hardware / Disk / Runtime diagnosis；
- 未 READY Runtime 永不接真实流量；
- 不破坏现有 Provider Routing / Auth / Billing / Quota；
- Model Manager 的 inventory / status / safe delete 有明确产品合同；
- NODE-004 协议兼容 Gate 通过批准的 v0.1 协议矩阵。

### 人类完成定义

只有当对应 [Human Acceptance Registry](/burncloud-node/implementation-plan/human-acceptance/) 中 **NODE-001~NODE-504 的 24 个 Issue 人工验收全部完成**，才允许宣称 Node v0.1 产品完成。

最终 NODE-503 必须由产品负责人参与人工签收，且客户端全程只提供：

```text
base URL
normal BurnCloud credential
model
normal request body
```

客户端不得提供：

```text
GGUF path
artifact URL
llama-server path
internal port
PID
gpu_layers
download task ID
manual start/stop command
```

## 13. 执行顺序

```text
NODE-001 → 002 → 003 → 004
                    ↓
NODE-101 → 102 → 103
                    ↓
NODE-201 → 202 → 203 → 204
                    ↓
NODE-301 → 302 → 303 → 304
                    ↓
NODE-400 → 401 → 402 → 403 → 404
                    ↓
NODE-501 → 502
        ↘
          NODE-504
              ↓
          NODE-503
```

实际进入编码前仍必须执行：

```text
Implementation Plan (PLANNED)
      ↓
current-main Evidence Audit
      ↓
READY Engineering Issue
      ↓
Task Contract
      ↓
Branch / Pull Request
      ↓
Machine Verification
      ↓
Human Acceptance
      ↓
DONE
```

## 14. 实施边界

任何新增实现都先回答：

1. 现有 BurnCloud 是否已经拥有同类能力？
2. 这个能力是否属于 Node v0.1 必要闭环？
3. 对应产品承诺是否已经有明确 NODE Issue owner？
4. 机器验证通过后，人类应该如何独立证明产品真的成立？

如果现有能力可以复用，就不创建第二套实现；如果功能属于 Future，就不扩大 v0.1；如果产品承诺没有 Issue owner，则先补 Implementation Plan，不让 Codex 自行承担未授权职责。
