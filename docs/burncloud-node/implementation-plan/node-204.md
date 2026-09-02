---
title: "NODE-204：定义 ResolvedModel 与失败诊断合同"
slug: /burncloud-node/implementation-plan/node-204/
---

# NODE-204：定义 ResolvedModel 与失败诊断合同

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Model Resolver**  
**功能依赖：NODE-203**

> 这是实施计划，不是 Codex 的直接开发授权。实现前必须基于当时的 `burncloud/burncloud/main` 重做 Evidence Audit 并通过 READY Gate。

### TL;DR

NODE-204 要把 Resolver 的成功结果和失败原因都固定成稳定合同。成功时，Preparation / Runtime 能直接知道要准备什么；失败时，Demand Reconciler 能区分显存不足、Runtime 不支持、没有兼容 Variant 等真实原因。这样 `/v1` 无法立即服务时可以返回准确状态，而不是靠解析错误字符串。

### 背景与动机（Why）

Demand-driven Node 会自动做很多事情，因此模块之间更不能靠“猜”。如果 Resolver 只返回临时 tuple 或自由文本错误，后续后台准备和 API error mapping 很容易重新解释同一事实。NODE-204 用一个最小、稳定的合同切断这种耦合。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 定义稳定 `ResolvedModel` | 不包含 PID / Child handle |
| 固定 Artifact / Runtime / Resource facts | 不包含下载进度 |
| 定义结构化 ResolutionFailure | 不包含内部端口 |
| 为 Preparation / Reconciler 提供唯一输入 | 不启动/下载任何东西 |
| 支持机器可读 failure code | 不决定 Provider fallback |

### 风险与安全网（Risk）

> 这是边界合同：字段不够就回到架构审查，不能把整个 Node 的运行状态塞进 `ResolvedModel`。

### 审批者关注点（Reviewer Focus）

1. 是否同意 `ResolvedModel` 只描述“要准备什么”？
2. 是否同意 Resolver failure 必须机器可读？
3. 是否确认 Provider/Router 状态不进入这个合同？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
NODE-203 selection
      ↓
ResolvedModel | ResolutionFailure
      ↓
Preparation / Runtime / Demand Reconciler
```

### 2. Evidence

- current InferenceConfig 混合 `model_id`、`file_path`、`port`、`gpu_layers`，说明模型事实与运行状态尚未分离。
- NODE-203 将产生纯 selection + diagnostics；NODE-204 将它收敛成稳定 contract。

### 3. Reuse Targets / Do Not Recreate

Reuse：canonical model、Variant、Artifact、runtime/resource 类型。  
Do Not Recreate：process config、download state、Router/channel state。

### 4. Scope

#### Allowed

- `ResolvedModel` schema；
- `ResolutionFailure` / equivalent enum；
- stable field ownership；
- conversion from NODE-203；
- serialization/debug/equality as needed；
- contract tests。

#### Avoid

- PID / Child / internal port；
- download GID/progress；
- process/readiness status；
- Local Channel ID；
- Provider availability；
- Router/Billing/Auth state。

### 5. Behavior Contract

`ResolvedModel` 最低语义：

```text
canonical_id
selected_variant_id
model_format
quantization
artifact_reference
artifact_expected_size (when known)
runtime_requirement
resource_requirement / execution constraints
```

`ResolutionFailure` 至少能够稳定表达：

```text
MODEL_UNKNOWN
NO_COMPATIBLE_VARIANT
INSUFFICIENT_VRAM
INSUFFICIENT_RAM
UNSUPPORTED_RUNTIME
UNSUPPORTED_FORMAT
COMPATIBILITY_UNKNOWN
```

下游不得重新访问 Resolver 内部对象才能理解成功或失败。

### 6. Failure / Forbidden Fallbacks

禁止：

```text
failure => free-form string only
resolved model => include PID/port
resolved model => include download state
failure => include Provider fallback decision
missing contract field => let downstream guess
Preparation/Runtime => re-run Resolver internally
```

### 7. Impact / Invariants

```text
persistence: none required
external_calls: none
billing/auth/routing: none
process/runtime side effects: none
```

Candidate invariant：**Resolution truth 与 execution state 分离。**

### 8. Dependencies

前置：NODE-203。  
后续：NODE-301、NODE-302、NODE-401、NODE-504。

### 9. Stop Conditions

STOP IF：合同必须包含 PID/port/download/router state 才能工作、下游必须重新执行 Resolver、或 failure 无法稳定映射成机器可读诊断。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] `ResolvedModel` 有稳定最小字段合同。
- [ ] `ResolutionFailure` 有稳定机器可读 codes。
- [ ] NODE-203 result 可直接转换。
- [ ] NODE-301/302/401/504 不需要读取 Resolver 内部状态。

### ✅ 边界保护

- [ ] 不包含 PID、port、Child、download progress、Channel ID。
- [ ] 不包含 Provider/Router/Billing/Auth 状态。
- [ ] 错误处理不依赖字符串匹配。

### ✅ 回归与验证

- [ ] contract tests 覆盖成功对象和主要 failure variants。
- [ ] 固定 selection result 得到稳定结果。
- [ ] downstream 无需重新 Resolve。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确真实下游字段需求。
- [ ] 只通过分支 + Pull Request 合并。
