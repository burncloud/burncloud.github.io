---
title: "NODE-203：根据 Hardware / Runtime 选择 Variant"
slug: /burncloud-node/implementation-plan/node-203/
---

# NODE-203：根据 Hardware / Runtime 选择 Variant

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Model Resolver**  
**功能依赖：NODE-101、NODE-102、NODE-103、NODE-201、NODE-202**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `main` 并通过 READY Gate。

### TL;DR

NODE-203 要根据 canonical model、Model Manifest、HardwareProfile 和资源/兼容性视图，选择当前机器真正能执行的 Variant。这个选择必须确定、可解释、可测试；没有合适 Variant 时明确失败。完成后，Node 不需要让用户手工挑 GGUF，也不会靠随机 fallback“碰运气”。

### 背景与动机（Why）

同一个逻辑模型可能有多个量化、不同 Artifact 和不同 Runtime 需求。若选择规则散落在下载器、Runtime 或 CLI 里，系统就无法解释“为什么这台机器选了这个文件”，也很难在硬件不足时正确失败。

NODE-203 是 Resolver 真正做决策的地方，但权限必须非常窄：**只选择，不下载、不启动、不路由。** 选择逻辑只消费已经确认的事实，不允许自己重新检测硬件或从文件名猜兼容性。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 根据硬件与 Manifest 筛选 Variant | 不下载 Artifact |
| 检查 resource fit / compatibility | 不启动 llama.cpp |
| 给出可解释 selection reason | 不修改 Router |
| 无可行 Variant 时结构化失败 | 不静默选随机 GGUF |
| 固定输入得到确定结果 | 不重新调用硬件探测 |

### 风险与安全网（Risk）

> 这是**纯决策层**：最坏结果应是 `NO_COMPATIBLE_VARIANT`，而不是为了让请求成功而偷偷下载、改 Router 或选择未经证明兼容的文件。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Resolver 只做选择，不拥有任何执行副作用？
2. 是否同意选择必须基于 Manifest + Hardware/Compatibility facts，而不是文件名猜测？
3. 是否同意没有兼容 Variant 时 fail closed，不做随机降级？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
canonical Model ID
+ validated Manifest variants
+ HardwareProfile
+ ResourceSnapshot / RuntimeCompatibility
             ↓
 deterministic Variant selection
             ↓
 selection result + reason
```

### 2. Evidence

- NODE-201/202 计划提供稳定逻辑身份和 Variant 声明事实。
- NODE-101~103 计划提供 canonical hardware facts 与 resource/compatibility view。
- 当前 `InferenceService` 仍要求调用方直接提供 `file_path`、`gpu_layers`，说明 current main 尚缺“逻辑模型 → 当前机器可执行 Variant”的独立选择层。
- 当前 `ModelService` 能筛选 GGUF，但 GGUF 列表本身不等于兼容性选择策略。

### 3. Entry / Starting Point

实现前重新检查：

```text
NODE-201 Manifest
NODE-202 canonical identity
NODE-101 HardwareProfile
NODE-103 compatibility/resource view
current model/runtime types in main
```

### 4. Reuse Targets / Do Not Recreate

Reuse：Manifest facts、HardwareProfile、ResourceSnapshot / Compatibility facts。  
Do Not Recreate：hardware detection、download manager、runtime/process manager、Router policy。

### 5. Scope

#### Allowed

- candidate filtering；
- format/runtime compatibility checks；
- resource-fit checks；
- deterministic ordering / tie-break policy；
- selection explanation / reason；
- structured selection errors；
- pure unit tests。

#### Avoid

- network/download；
- local file mutation；
- process spawn；
- runtime binary installation；
- Channel registration；
- Router / Billing / Auth；
- hidden hardware detection。

### 6. Behavior Contract

#### Inputs

```text
canonical_model_id
manifest_variants[]
hardware_profile
resource_snapshot
runtime_compatibility_view
```

#### Output

一个明确的 Variant selection result，供 NODE-204 封装成稳定 `ResolvedModel`。

Selection 必须满足：

```text
same facts => same selection
unsupported format => candidate rejected with reason
insufficient resources => candidate rejected with reason
unknown required compatibility => not treated as confirmed compatible
no candidate => structured NO_COMPATIBLE_VARIANT-like error
```

若 Manifest 明确允许 CPU fallback，可以参与 policy；若未声明，不得自行 fallback。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
no compatible variant => choose smallest file
no GPU => assume CPU fallback
unknown compatibility => treat as compatible
missing artifact => download it here
selection failure => route to Provider
selection failure => mutate Manifest
call nvidia-smi / OS tools directly
```

### 8. Impact / Invariants

```text
persistence: none
external_calls: none
billing/auth/routing: none
process/runtime side effects: none
```

Candidate invariant：**Resolver 只选择，不执行副作用。**  
必须保持 `INV-ROUTER-001`：本地模型未来仍通过 existing Router 接入，不由 Resolver 直接路由。

### 9. Dependencies

前置：`NODE-101~103`、`NODE-201~202`。  
直接后续：`NODE-204`。

### 10. Stop Conditions

```text
STOP IF:
- selection requires network/download/process side effects
- required compatibility is unavailable but implementation wants to guess
- Router/Provider fallback must be changed
- hardware must be re-detected inside Resolver
- Manifest facts are insufficient and would need silent mutation
- selection contract cannot remain deterministic/testable
```

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] Resolver 能基于固定 facts 选择可执行 Variant。
- [ ] selection reason 可被测试/诊断。
- [ ] resource insufficient / unsupported / unknown 均有明确拒绝原因。
- [ ] 无可行 Variant 返回结构化失败。

### ✅ 边界保护

- [ ] Resolver 无下载、网络、进程、Router side effect。
- [ ] 未重新检测硬件。
- [ ] 未静默 CPU fallback 或随机选择 Artifact。
- [ ] 未直接返回 PID、port、download state 等执行状态。

### ✅ 回归与验证

- [ ] tests 覆盖资源充足、显存不足、多个可行 Variant、完全不兼容、unknown compatibility。
- [ ] tie-break policy 对固定输入确定。
- [ ] Manifest 未允许时 CPU fallback 不发生。
- [ ] Provider routing 行为不受影响。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 锁定选择输入/输出合同。
- [ ] 只通过分支 + Pull Request 合并。
