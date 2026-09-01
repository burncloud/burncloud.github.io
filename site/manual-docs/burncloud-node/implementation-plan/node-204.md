---
title: "NODE-204：定义 ResolvedModel 与失败诊断合同"
slug: /burncloud-node/implementation-plan/node-204/
---

# NODE-204：定义 ResolvedModel 与失败诊断合同

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Model Resolver**  
**功能依赖：NODE-203**

> 这是实施计划，不是 Codex 的直接开发授权。实现前必须基于当时的 `burncloud/burncloud/main` 重新做 Evidence Audit 并通过 READY Gate。

### TL;DR

NODE-204 要把 Resolver 的最终结果固定成一个稳定合同 `ResolvedModel`。后面的 Model Preparation 和 Runtime 只依赖这个合同，不需要知道 Resolver 内部怎么筛 Variant。完成后，模型选择层和执行层之间会有清楚的边界，错误也不再靠字符串判断。

### 背景与动机（Why）

即使 NODE-203 已经能选出 Variant，如果输出只是临时 tuple 或散落字段，Preparation、Runtime 很快又会直接读取 Manifest、HardwareProfile 或 Resolver 内部状态，造成耦合回流。

因此 NODE-204 的任务是把“选择结果”变成**稳定、可审查、可序列化/测试的边界对象**。它只包含后续真正需要的模型事实，不允许混入 PID、端口、下载进度等运行状态。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 定义稳定 `ResolvedModel` | 不包含 PID / Child handle |
| 固定 canonical ID / Variant / Artifact / Runtime requirements | 不包含动态内部端口 |
| 定义结构化 resolver error | 不包含下载进度 |
| 为 Preparation / Runtime 提供唯一输入 | 不启动/下载任何东西 |
| 避免字符串匹配错误 | 不让下游读取 Resolver 内部状态 |

### 风险与安全网（Risk）

> 这是**合同收口**改动：如果某字段属于运行时状态而不是解析结果，就必须留在后续模块；宁可合同暂时小，也不能把整个 Node 状态塞进 `ResolvedModel`。

### 审批者关注点（Reviewer Focus）

1. 是否同意 `ResolvedModel` 成为 Resolver 与执行层之间的唯一稳定边界？
2. 是否同意它只描述“要准备/运行什么”，不描述“现在运行到哪”？
3. 是否同意失败必须结构化，不能依赖错误字符串解析？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
NODE-203 selection
      ↓
ResolvedModel
      ├─ canonical model ID
      ├─ selected variant
      ├─ format / quantization
      ├─ artifact reference
      ├─ runtime requirement
      └─ resource requirement
      ↓
NODE-301 Preparation
NODE-401 Runtime Adapter
```

### 2. Evidence

- 当前 `InferenceConfig` 直接混合 `model_id`、`file_path`、`port`、`context_size`、`gpu_layers`，其中既有模型事实也有进程运行参数，说明现有原型还没有清晰的 Resolver → Runtime 边界。
- NODE-203 计划产生纯 Variant selection；NODE-204 必须把该结果封装成稳定 contract，而不是继续传播内部选择结构。
- current main 尚无 authoritative `ResolvedModel` 类型。

### 3. Entry / Starting Point

实现前重新检查：

```text
NODE-203 selection output
NODE-201 Manifest fields
current model/inference types
future NODE-301 / NODE-401 input needs
```

### 4. Reuse Targets / Do Not Recreate

Reuse：canonical model/Variant/Artifact/runtime requirement 类型中可复用部分。  
Do Not Recreate：process config、download state、Router channel state。

### 5. Scope

#### Allowed

- `ResolvedModel` schema；
- semantic resolver error types；
- stable field ownership；
- serialization/equality/debug contract（如后续需要）；
- conversion from NODE-203 result；
- contract tests。

#### Avoid

- PID / Child handle；
- internal port；
- download GID/progress；
- process/readiness status；
- Local Channel ID；
- Router / Billing / Auth state。

### 6. Behavior Contract

Inputs：NODE-203 已完成的 selection result。  
Output：稳定 `ResolvedModel` 或结构化 resolver failure。

`ResolvedModel` 最低语义：

```text
canonical_id
selected_variant_id
model_format
quantization (if applicable)
artifact_reference
runtime_requirement
resource_requirement / execution constraints
```

不得要求下游重新访问 Resolver 内部对象才能理解结果。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
error => free-form string only
resolved model => include runtime PID/port
resolved model => include download progress/GID
missing field => let downstream guess
Preparation/Runtime => re-run Resolver internally
```

若合同字段不足，应回到架构审查，而不是把所有后续状态都塞进该类型。

### 8. Impact / Invariants

```text
persistence: none required
external_calls: none
billing/auth/routing: none
process/runtime side effects: none
```

Candidate invariants：
- Artifact selection 与 Process state 分离；
- Preparation / Runtime 只消费稳定 ResolvedModel，不依赖 Resolver 内部选择过程。

### 9. Dependencies

前置：`NODE-203`。  
后续：`NODE-301`、`NODE-401`。

### 10. Stop Conditions

STOP IF：合同必须包含 PID/port/download state 才能工作、下游必须重新执行 Resolver、需要修改 Router/Billing/Auth、或 current main 已有 authoritative contract 与本设计冲突。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] `ResolvedModel` 有稳定、明确、最小的字段合同。
- [ ] NODE-203 selection 可转换为 ResolvedModel。
- [ ] Resolver failures 使用结构化错误类型。
- [ ] NODE-301 / NODE-401 可只依赖 ResolvedModel 获得所需模型事实。

### ✅ 边界保护

- [ ] ResolvedModel 不包含 PID、port、Child handle、download progress、Channel ID。
- [ ] 未加入 Router / Billing / Auth state。
- [ ] 下游不需要读取 Resolver 内部状态。

### ✅ 回归与验证

- [ ] contract tests 覆盖成功对象和主要 failure variants。
- [ ] 错误处理不依赖字符串匹配。
- [ ] 固定 selection result 得到稳定 ResolvedModel。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确 NODE-301 / NODE-401 的真实输入需求。
- [ ] 只通过分支 + Pull Request 合并。
