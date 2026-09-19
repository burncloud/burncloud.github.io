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

NODE-203 要让 Node 在用户只给出逻辑 `model` 时，自动选出本机可运行的 Variant，并且把“不为什么能跑”或“为什么不能跑”都说清楚。它仍然只做决策，不下载、不启动、不路由。这样自动准备失败时，BurnCloud 能给出真实的 VRAM / RAM / Runtime 诊断，而不是一句“模型不存在”。

### 背景与动机（Why）

Demand-driven Node 不会让用户自己挑 GGUF，因此 Resolver 的责任更重要：它既要选对 Variant，也要给后台 Reconciler 一个可靠的失败原因。若硬件不够却只返回一个自由文本错误，API 层就无法稳定区分“正在下载”和“这台机器根本跑不了”。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 自动筛选可执行 Variant | 不下载 Artifact |
| 检查格式、Runtime、VRAM/RAM fit | 不检查动态下载进度 |
| 输出可解释 selection/rejection reasons | 不启动 llama.cpp |
| 明确 no-compatible 原因 | 不修改 Router / Provider fallback |
| 固定输入得到确定结果 | 不重新调用硬件探测 |

### 风险与安全网（Risk）

> Resolver 宁可明确拒绝，也不能猜兼容性。自动化不等于“尽量试着跑”。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Resolver 只决策、不执行副作用？
2. 是否同意硬件不足必须输出结构化原因？
3. 是否同意 Provider fallback 仍由现有 Router 决定，而不是 Resolver 决定？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
canonical Model ID
+ validated Manifest variants
+ HardwareProfile
+ ResourceSnapshot
+ RuntimeCompatibility
             ↓
deterministic selection
             ↓
Selected Variant + Diagnostics
```

### 2. Evidence

- NODE-201/202 提供稳定模型身份与 Variant 声明事实。
- NODE-101~103 提供 authoritative hardware/resource/compatibility facts。
- current InferenceConfig 仍要求调用方直接提供 `file_path`、`gpu_layers`，说明 current main 尚缺自动 Variant selection。

### 3. Reuse Targets / Do Not Recreate

Reuse：Manifest、HardwareProfile、ResourceSnapshot、RuntimeCompatibility。  
Do Not Recreate：hardware detection、download manager、runtime/process manager、Router policy。

### 4. Scope

#### Allowed

- candidate filtering；
- format/runtime compatibility；
- VRAM/RAM/resource-fit checks；
- deterministic ordering/tie-break；
- structured selection diagnostics；
- pure unit tests。

#### Avoid

- network/download；
- filesystem mutation；
- disk admission for actual download（NODE-302）；
- process spawn；
- Channel registration；
- Router/Billing/Auth；
- hidden hardware detection。

### 5. Behavior Contract

输入：

```text
canonical_model_id
manifest_variants[]
hardware_profile
resource_snapshot
runtime_compatibility_view
```

成功输出：明确 Selected Variant + reason。  
失败输出：结构化 reject reason，至少可表达：

```text
NO_COMPATIBLE_VARIANT
INSUFFICIENT_VRAM
INSUFFICIENT_RAM
UNSUPPORTED_RUNTIME
UNSUPPORTED_FORMAT
COMPATIBILITY_UNKNOWN
```

必须满足：

```text
same facts => same selection
unknown compatibility != compatible
insufficient resource => explicit rejection
no candidate => explicit diagnosis
```

若 Manifest 明确允许 CPU fallback，才可参与选择；未声明不得自行 fallback。

### 6. Failure / Forbidden Fallbacks

禁止：

```text
no compatible variant => choose smallest file
no GPU => assume CPU fallback
unknown compatibility => treat as compatible
missing artifact => download here
selection failure => route to Provider
selection failure => mutate Manifest
call nvidia-smi / OS tools directly
```

### 7. Impact / Invariants

```text
persistence: none
external_calls: none
billing/auth/routing: none
process/runtime side effects: none
```

Candidate invariant：**Resolver 只选择并诊断，不执行副作用。**

### 8. Dependencies

前置：NODE-101~103、NODE-201~202。  
后续：NODE-204、NODE-504。

### 9. Stop Conditions

STOP IF：需要下载/process/router side effect、需要猜测未知兼容性、需要在 Resolver 内决定 Provider fallback、或无法给出稳定结构化 reject reasons。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] 固定 facts 能确定选择可执行 Variant。
- [ ] 成功 selection reason 可测试。
- [ ] VRAM/RAM/Runtime/Format/Unknown 均有稳定 reject reason。
- [ ] 无可行 Variant 返回结构化失败。

### ✅ 边界保护

- [ ] Resolver 无下载、网络、进程、Router side effect。
- [ ] 未重新检测硬件。
- [ ] 未静默 CPU fallback 或随机选 Artifact。
- [ ] 未决定 Provider fallback。

### ✅ 回归与验证

- [ ] tests 覆盖资源充足、显存不足、内存不足、多 Variant、完全不兼容、unknown compatibility。
- [ ] tie-break 对固定输入确定。
- [ ] Provider routing 行为不受影响。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 锁定输入/输出/diagnostic contract。
- [ ] 只通过分支 + Pull Request 合并。


---

## 第四层：人类验收（Human Acceptance）

> 本节由 [Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/) 生成。机器测试、CI 或 AI Review 不能替代这里的人工验收。

### NODE-203 — Hardware/Runtime 驱动的 Variant 选择

**验收者：** 模型负责人 + GPU/Runtime 工程师。

**人工步骤：**
1. 在至少两种资源档位上解析同一个逻辑模型。
2. 确认选择的 Variant 与 HardwareProfile/Runtime 能力相符。
3. 制造显存不足或 Runtime 不支持，确认返回结构化 reject reason。

**人类通过标准：** 用户只选择模型，不选择 GGUF；可运行时选出可解释 Variant，不可运行时解释真实原因。

**人工判定失败：** 任意挑最小 GGUF 兜底、资源不足仍输出可运行 Variant，或 Resolver 自己触发下载/启动。

**建议证据：** 不同机器/资源档位的解析对比。
