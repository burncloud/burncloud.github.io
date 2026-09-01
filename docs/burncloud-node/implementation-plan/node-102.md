---
title: "NODE-102：检测 NVIDIA GPU / VRAM / Driver"
slug: /burncloud-node/implementation-plan/node-102/
---

# NODE-102：检测 NVIDIA GPU / VRAM / Driver

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Hardware Profile**  
**功能依赖：NODE-101**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对当时的 `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-102 要在受支持的 NVIDIA 主机上可靠识别 GPU 型号、数量、显存和 Driver，并写入 NODE-101 定义的 HardwareProfile。重点不是“尽量猜到 GPU”，而是让检测成功、检测失败、工具缺失都得到明确结构化结果。完成后，Resolver 和 Runtime 不需要自己再调用 `nvidia-smi`。

### 背景与动机（Why）

现有 Monitor 只有 CPU / Memory / Disk，没有 GPU。若后续每个模块自己检测 NVIDIA，就会产生多套命令解析、不同错误语义和不同的“GPU 是否存在”判断。

因此 NODE-102 只负责**把 NVIDIA 环境变成硬件事实**。它不决定某个模型能不能跑，也不决定用多少 GPU layer；这些策略属于后续 Compatibility / Resolver / Runtime。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 检测 NVIDIA GPU 型号与数量 | 不选择模型 Variant |
| 检测 VRAM 与 Driver | 不计算 llama.cpp 参数 |
| 明确区分 unavailable / unknown / detected | 不把命令失败当成“没有 GPU” |
| 将结果写入 HardwareProfile | 不让 Resolver 自己调 `nvidia-smi` |
| 覆盖多 GPU 与异常输出 | 不扩展到 AMD / Intel GPU |

### 风险与安全网（Risk）

> 这是**只读硬件探测**：最坏结果应是 GPU facts 显示 unavailable，而不是错误地宣布一块不存在或参数错误的 GPU 可用。

### 审批者关注点（Reviewer Focus）

1. 是否同意 v0.1 先把 NVIDIA detection 做成一个明确 adapter？
2. 是否同意“检测失败”与“确实没有 GPU”必须是不同状态？
3. 是否同意 Resolver / Runtime 不得绕过 HardwareProfile 重复探测？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
NVIDIA host facts
      ↓
NVIDIA detection adapter
      ↓
structured GPU facts
      ↓
canonical HardwareProfile
```

### 2. Evidence

- `crates/service/crates/monitor/src/types.rs` 当前 `SystemMetrics` 仅有 CPU、Memory、Disks、timestamp，没有 GPU。
- `crates/server/src/lib.rs` 已共享 `SystemMonitorService`，所以 NODE-102 应作为现有硬件事实链的扩展，而不是新建第二套 System Monitor。
- 当前本地推理原型 `InferenceConfig` 只有 `gpu_layers` 参数，并不提供 authoritative GPU detection。

### 3. Entry / Starting Point

实现前重新检查：

```text
crates/service/crates/monitor/
NODE-101 HardwareProfile
platform-specific command/runtime helpers already present in current main
```

### 4. Reuse Targets / Do Not Recreate

Reuse：HardwareProfile、现有 monitor/service 组织、标准 process execution 工具。  
Do Not Recreate：Resolver-owned detection、Runtime-owned detection、第二套 Monitor。

### 5. Scope

#### Allowed

- Linux/NVIDIA detection adapter；
- GPU model/count、VRAM、Driver 解析；
- multi-GPU representation；
- command unavailable / failed / malformed output diagnostics；
- fixture-based parser tests。

#### Avoid

- AMD / Intel GPU support；
- model compatibility policy；
- Variant selection；
- Runtime argument generation；
- GPU scheduling；
- Router / Billing / Auth。

### 6. Behavior Contract

Inputs：host environment + NVIDIA detection capability。  
Outputs：HardwareProfile 可消费的 NVIDIA facts。

必须区分：

```text
Detected      = 成功确认 GPU facts
NoDevice      = 成功执行且确认无设备
Unavailable   = detection tool / interface unavailable
Failed        = interface exists but execution/parse failed
Unknown(field)= device 存在，但某字段无法确认
```

Detection owns facts acquisition；不拥有 compatibility / model selection。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
command failure => assume no GPU
missing VRAM => use 0 as real VRAM
unknown driver => mark compatible
Resolver/Runtime calls nvidia-smi again
hard-code "GPU X can run model Y"
```

错误必须携带足够上下文用于诊断，但不得泄露无关敏感环境信息。

### 8. Impact / Invariants

```text
persistence: none required
external_calls: local host detection only
billing/auth/routing: none
process lifecycle: short-lived detection command only, if command-based
```

Candidate invariants：
- Detection 只产生硬件事实；
- Resolver / Runtime 不重复拥有 NVIDIA detection。

### 9. Dependencies

前置：`NODE-101`。  
后续：`NODE-103`、`NODE-203`、`NODE-401`。

### 10. Stop Conditions

STOP IF：需要在 Resolver/Runtime 重复探测、需要把未知值猜成确定值、需要引入 GPU scheduler、需要改变现有 Monitor 业务语义、或需要扩展到非 NVIDIA 平台才能完成本 Issue。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] 支持环境能产生结构化 NVIDIA GPU / VRAM / Driver facts。
- [ ] 多 GPU 能稳定表达。
- [ ] Detected / NoDevice / Unavailable / Failed 语义明确。
- [ ] 结果进入 canonical HardwareProfile。

### ✅ 边界保护

- [ ] Resolver / Runtime 未新增自己的 NVIDIA 探测。
- [ ] 未实现 model compatibility / Variant policy。
- [ ] 未引入 GPU scheduler 或非 NVIDIA 支持。

### ✅ 回归与验证

- [ ] tests 覆盖正常、多 GPU、工具不存在、命令失败、字段缺失、malformed output。
- [ ] unknown 不会被序列化成伪造的确定值。
- [ ] 现有 CPU / RAM / Disk Monitor 行为不受破坏。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确真实 detection interface 与测试夹具。
- [ ] 只通过分支 + Pull Request 合并。
