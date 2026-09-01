---
title: "NODE-101：定义 canonical HardwareProfile"
slug: /burncloud-node/implementation-plan/node-101/
---

# NODE-101：定义 canonical HardwareProfile

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Hardware Profile**  
**功能依赖：NODE-002**

> 这是实施计划，不是 Codex 的直接开发授权。实现前必须重新核对当时 `burncloud/burncloud/main`，并通过 READY Gate。

### TL;DR

NODE-101 要定义 Node 内唯一权威的硬件画像 `HardwareProfile`。它把 CPU、内存、磁盘、GPU、显存和驱动等硬件事实放进统一合同，避免 Resolver、Runtime、UI 各自理解一套硬件。完成后，后续所有“这台机器能不能跑这个模型”的判断都有同一个输入来源。

### 背景与动机（Why）

BurnCloud 已经有 System Monitor，可以采集 CPU、Memory、Disk，但当前这些数据主要是监控指标，还不是为本地模型选择设计的硬件合同。更重要的是，GPU / VRAM / Driver 目前还没有统一进入一个 Node 级数据结构。

如果不先定义 canonical HardwareProfile，后续很容易出现 Resolver 自己调 `nvidia-smi`、Runtime 又自己解析显存、UI 再维护第三份字段。最终同一台机器会出现多个“硬件真相”。

NODE-101 只负责定义**硬件事实长什么样**，具体 NVIDIA 探测留给 NODE-102，动态资源与兼容性视图留给 NODE-103。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 定义唯一 `HardwareProfile` 数据合同 | 不在 Resolver 内重新探测硬件 |
| 映射现有 CPU / Memory / Disk 数据 | 不实现 NVIDIA 探测细节 |
| 为 GPU / VRAM / Driver 预留明确字段 | 不决定哪个模型 Variant 可运行 |
| 显式表达 unknown / unavailable | 不伪造默认 GPU 或显存 |
| 区分硬件身份与后续动态资源视图 | 不做 Runtime 参数选择 |

### 风险与安全网（Risk）

> 这是**纯事实合同优先**的改动：最坏结果应该是某些硬件字段仍为 unknown，而不是系统猜出一个“看起来合理”的 GPU；无法确认的事实必须保持未知。

### 审批者关注点（Reviewer Focus）

1. **是否同意 Node 只有一份 canonical HardwareProfile？**
2. **是否同意“未知”是合法状态，不能用默认值冒充真实硬件？**
3. **是否同意 Detection 只产生事实，模型选择必须留给 Resolver？**

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

定义 Node 内唯一权威硬件画像合同：

```text
system / existing monitor facts
        ↓
HardwareProfile
        ↓
NODE-102 detection extension
        ↓
NODE-103 resource / compatibility view
        ↓
Resolver / Runtime consumers
```

### 2. Evidence

#### STATIC CONFIRMED — 现有 Monitor 已有 CPU / Memory / Disk 类型

`crates/service/crates/monitor/src/types.rs` 当前定义 `CpuInfo`、`MemoryInfo`、`DiskInfo` 和 `SystemMetrics`，其中包含 CPU core/brand/frequency、RAM total/used/available、disk total/used/available 等数据。

#### STATIC CONFIRMED — Monitor 当前公共合同没有 GPU 字段

`SystemMetrics` 目前只包含 `cpu`、`memory`、`disks` 和 `timestamp`。因此 Node 的 GPU / VRAM / Driver 输入仍缺少统一合同。

#### STATIC CONFIRMED — Server 已持有共享 SystemMonitorService

`crates/server/src/lib.rs :: AppState` 当前共享 `SystemMonitorService`，说明 Node 应复用现有监控能力，不建立第二套 CPU/RAM/Disk collector。

#### PLANNED GAP — canonical Node hardware contract 尚不存在

当前 main 尚无一份同时服务 Resolver / Runtime 的 Node 级 HardwareProfile。

### 3. Entry / Starting Point

实现前重新检查：

```text
crates/service/crates/monitor/src/lib.rs
crates/service/crates/monitor/src/types.rs
crates/service/crates/monitor/src/service.rs
NODE-002 NodeContext wiring
```

### 4. Reuse Targets / Do Not Recreate

#### Reuse

- `SystemMonitorService`；
- `SystemMetrics` 的 CPU / Memory / Disk 事实；
- 现有 serde / workspace 类型习惯。

#### Do Not Recreate

```text
NodeCpuCollector
NodeMemoryCollector
NodeDiskCollector
resolver-owned hardware detection
runtime-owned hardware detection
UI-owned canonical hardware model
```

### 5. Scope

#### Allowed

- `HardwareProfile` schema；
- OS / architecture / CPU / RAM / disk / GPU / VRAM / Driver 等字段合同；
- explicit unknown / unavailable semantics；
- 从现有 Monitor facts 到 HardwareProfile 的适配；
- schema / mapping targeted tests。

#### Avoid

- NODE-102 的 NVIDIA command / API detection；
- NODE-103 的 compatibility / dynamic resource policy；
- NODE-203 Variant selection；
- llama.cpp 参数计算；
- model downloading；
- Router / Billing / Auth。

### 6. Behavior Contract

#### Inputs

- 现有可确认的系统静态/监控事实；
- 后续 detector 可提供的 GPU 事实。

#### Outputs

`HardwareProfile` 至少能表达：

```text
OS
CPU architecture
CPU cores / identity
RAM total
Disk free/total relevant to model storage
GPU vendor
GPU model
GPU count
VRAM total per device or normalized device facts
Driver identity/version
fact availability / unknown state
```

具体动态 available RAM / VRAM 与 runtime compatibility 由 NODE-103 负责。

#### Ownership

HardwareProfile owns：**facts schema**。  
HardwareProfile does not own：探测命令、模型选择、runtime selection、调度策略。

### 7. Failure / Forbidden Fallbacks

采集不到字段：明确 `unknown` / `unavailable`。  
现有 Monitor 数据无效：返回可诊断错误或 unknown，不制造数值。

禁止：

```text
assume NVIDIA when GPU vendor is unknown
assume 0 VRAM when VRAM cannot be detected
infer model compatibility inside HardwareProfile
call nvidia-smi from Resolver/Runtime as a workaround
create duplicate CPU/RAM/Disk collectors
```

### 8. Impact / Invariants

```text
persistence: none required by contract
external_calls: none in NODE-101 itself
billing_usage_quota: none
auth_authorization: none
routing_provider: none
process_runtime_lifecycle: none
public_api: no required external API change
```

必须保持 `INV-WORKSPACE-001`。  
Candidate invariant：**Node 内只有一份 canonical HardwareProfile；所有下游硬件判断从它或其派生 view 获取事实。**

### 9. Dependencies

前置：`NODE-002`。  
后续：`NODE-102`、`NODE-103`、`NODE-203`、`NODE-401`。

### 10. Stop Conditions

```text
STOP IF:
- implementation requires duplicate CPU/RAM/Disk collectors
- HardwareProfile starts owning model selection or runtime policy
- unknown hardware must be converted into guessed values
- current main already has another authoritative hardware contract that conflicts
- implementation requires Router/Billing/Auth changes
- scope expands into NODE-102/103/203
```

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] 存在唯一、可测试的 `HardwareProfile` 合同。
- [ ] 现有 CPU / RAM / Disk facts 可映射到 HardwareProfile。
- [ ] GPU / VRAM / Driver 有明确字段与未知状态表达。
- [ ] static hardware identity 与 NODE-103 的动态资源 view 边界明确。

### ✅ 边界保护

- [ ] 未复制 CPU / Memory / Disk collector。
- [ ] 未在本 Issue 实现 NVIDIA detection、Variant selection 或 Runtime policy。
- [ ] 未用默认 GPU / VRAM 冒充未知事实。

### ✅ 回归与验证

- [ ] mapping tests 覆盖正常数据和缺失数据。
- [ ] unknown / unavailable 可以被稳定序列化/比较（如合同需要）。
- [ ] 现有 Monitor 行为不因 HardwareProfile 被破坏。
- [ ] `INV-WORKSPACE-001` 保持成立。

### ✅ 工程流程

- [ ] current-main Evidence Audit 已完成。
- [ ] Engineering Issue 已通过 READY Gate。
- [ ] Task Contract 明确 HardwareProfile 的真实归属位置。
- [ ] 只通过分支 + Pull Request 合并。
