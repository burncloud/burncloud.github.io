---
title: "NODE-103：生成 Runtime Compatibility 与资源快照"
slug: /burncloud-node/implementation-plan/node-103/
---

# NODE-103：生成 Runtime Compatibility 与资源快照

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Hardware Profile**  
**功能依赖：NODE-101、NODE-102**

> 这是实施计划，不是 Codex 的直接开发授权。实现前必须重新核对 current `main` 并通过 READY Gate。

### TL;DR

NODE-103 要把“这台机器是什么硬件”进一步整理成“当前有哪些资源、Runtime 已知具备哪些兼容条件”的只读快照。它给 Resolver / Runtime 一个稳定视图，但仍然不替它们选择模型或参数。完成后，下游不需要直接解释原始 `nvidia-smi`、Memory 或 Driver 数据。

### 背景与动机（Why）

NODE-101/102 负责采集事实，但静态身份和动态资源不是一回事：一张 24GB GPU 不代表此刻还有 24GB 可用显存；Driver 存在也不等于任意 Runtime 都一定兼容。

如果 Resolver 直接读取所有原始字段并自己推导资源状态，Runtime 又做一套相同判断，很快就会产生两份兼容性逻辑。NODE-103 因此只负责生成**事实派生视图**，而真正“选哪个 Variant”仍然只在 NODE-203。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 形成 available RAM / VRAM 资源快照 | 不选择模型 Variant |
| 表达已知 Runtime/backend compatibility facts | 不决定 CPU/GPU fallback 策略 |
| 区分静态身份与动态资源 | 不下载模型 |
| 对 unknown compatibility 明确建模 | 不启动 Runtime / Process |
| 给 Resolver / Runtime 提供统一 view | 不直接修改 Router |

### 风险与安全网（Risk）

> 这是**只读派生层**：如果某项兼容性无法由真实硬件/Runtime evidence 得出，就保持 unknown；不能为了让后续选择成功而“猜兼容”。

### 审批者关注点（Reviewer Focus）

1. 是否同意 HardwareProfile 是事实源，而 Compatibility / ResourceSnapshot 是派生 view？
2. 是否同意 NODE-103 不拥有 Variant selection？
3. 是否同意动态 available 资源不能覆盖静态硬件身份？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
HardwareProfile
   + current resource facts
   + known runtime/backend capabilities
                ↓
ResourceSnapshot + RuntimeCompatibilityView
                ↓
Resolver / Runtime consumers
```

### 2. Evidence

- 当前 Monitor 已有 `MemoryInfo.available`、`DiskInfo.available` 等动态系统资源事实。
- NODE-102 计划补齐 NVIDIA GPU / VRAM / Driver facts。
- 当前 `InferenceService` 直接接收 `gpu_layers` 并启动 llama-server，尚无统一的 compatibility/resource view 作为前置输入。

### 3. Entry / Starting Point

重新检查：

```text
NODE-101 HardwareProfile
NODE-102 NVIDIA facts
crates/service/crates/monitor/src/types.rs
current llama.cpp/runtime capability representation, if any
```

### 4. Reuse Targets / Do Not Recreate

Reuse：HardwareProfile、Monitor 的 available resource facts、已有 runtime facts。  
Do Not Recreate：第二套 detection、Resolver policy、Runtime process manager。

### 5. Scope

#### Allowed

- `ResourceSnapshot` / equivalent view；
- available RAM / disk / VRAM 表达；
- backend / Driver / runtime compatibility facts；
- static-vs-dynamic separation；
- unknown / unsupported semantics；
- deterministic derivation tests。

#### Avoid

- Model Manifest lookup；
- Variant ranking；
- CPU fallback policy；
- Runtime argument generation；
- download / process / Router。

### 6. Behavior Contract

Inputs：canonical HardwareProfile + current resource facts + 已确认 runtime/backend facts。  
Outputs：可被 Resolver / Runtime 读取的只读快照。

必须满足：

```text
static identity != dynamic availability
unknown compatibility != compatible
resource snapshot is time-bound / refreshable
view derivation has no model-specific selection side effect
```

NODE-103 owns 派生事实；不拥有决策策略。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
unknown driver => compatible
missing available VRAM => use total VRAM
resource insufficient => silently pick smaller model
compatibility view => embed model-specific priority
re-run hardware detection inside consumers
```

无法派生时必须返回 unknown / unavailable，而不是制造确定结果。

### 8. Impact / Invariants

```text
persistence: none required
external_calls: none beyond reused local facts
billing/auth/routing: none
runtime/process: no spawn
```

Candidate invariant：**Detection 产生事实，NODE-103 产生派生 view，Resolver 才做模型选择。**

### 9. Dependencies

前置：`NODE-101`、`NODE-102`。  
后续：`NODE-203`、`NODE-401`。

### 10. Stop Conditions

STOP IF：需要做 model-specific selection、需要隐藏 unknown、需要复制 detection、需要启动 Runtime、或必须让 dynamic availability 覆盖静态硬件身份。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] 能表达 available RAM / disk / VRAM 等动态资源。
- [ ] 能表达 runtime/backend 的 known compatible / unsupported / unknown facts。
- [ ] 静态 HardwareProfile 与动态快照明确分离。
- [ ] Resolver / Runtime 可只读取统一 view，不直接解释原始 detector 输出。

### ✅ 边界保护

- [ ] 未实现 Variant selection 或模型 fallback。
- [ ] 未启动 Runtime / Process。
- [ ] 未复制硬件检测逻辑。
- [ ] unknown 没有被当成 compatible。

### ✅ 回归与验证

- [ ] tests 覆盖资源充足、不足、unknown compatibility、资源变化。
- [ ] snapshot derivation 对固定输入是确定的。
- [ ] existing Monitor / HardwareProfile contracts 不被破坏。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确真实 runtime capability evidence 来源。
- [ ] 只通过分支 + Pull Request 合并。
