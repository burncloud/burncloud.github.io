---
title: "NODE-401：llama.cpp Runtime Adapter 与 ProcessSpec"
slug: /burncloud-node/implementation-plan/node-401/
---

# NODE-401：llama.cpp Runtime Adapter 与 ProcessSpec

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**功能依赖：NODE-103、NODE-204、NODE-303**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-401 要把“一个已经解析并验证好的模型，应该用什么 llama.cpp 命令运行”收敛成 `Runtime Adapter → ProcessSpec`。Adapter 只生成 binary、args、env 和健康检查等运行说明，不真正启动进程。完成后，Runtime 决策和 Process 生命周期会彻底分开，也为以后扩展其它 Runtime 留下稳定边界。

### 背景与动机（Why）

当前 `InferenceService::start_instance()` 同时负责找 `llama-server`、拼命令、spawn、健康检查、状态更新和 Local Channel 注册。这个原型证明本地 llama.cpp 路径可行，但职责过于集中，任何参数变化都会和进程/Router 生命周期纠缠在一起。

NODE-401 只抽出其中一层：**Runtime 决定“怎么运行”，Process Manager 决定“如何管理运行中的进程”。** v0.1 只做 llama.cpp / llama-server，不趁机设计庞大的多 Runtime framework。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 定义 llama.cpp Runtime Adapter | 不实际 spawn 进程 |
| 根据 ResolvedModel / hardware facts 生成 args | 不持有 PID / Child |
| 输出无副作用 `ProcessSpec` | 不注册 Router / Channel |
| 定义 binary/env/workdir/readiness contract | 不扩展 vLLM / SGLang |
| 参数不兼容时明确失败 | 不重新下载/验证 Artifact |

### 风险与安全网（Risk）

> 这是**纯运行规格生成层**：生成不了合法 ProcessSpec 就明确失败；它没有权限通过 spawn、下载或改 Router 来验证“也许能跑”。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Runtime Adapter 只输出 ProcessSpec，不拥有进程？
2. 是否同意 Node v0.1 先锁定 llama.cpp，而不是提前做多 Runtime 抽象？
3. 是否同意所有模型输入必须来自已验证的 ResolvedModel / Artifact READY？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
ResolvedModel
+ READY Artifact
+ Hardware / Compatibility facts
           ↓
llama.cpp Runtime Adapter
           ↓
ProcessSpec
```

### 2. Evidence

- 当前 `InferenceService::start_instance()` 会查找 `llama-server`，构造 `-m <file> --port <port> -c <ctx> -ngl <gpu_layers> --nobrowser`，随后直接 spawn。
- 当前 `InferenceConfig` 混合 model/file/port/context/gpu_layers，说明 Runtime spec 与 Process lifecycle 尚未分离。
- current main 已证明 llama-server 可作为 OpenAI-compatible 本地 endpoint，但尚无独立 `ProcessSpec` contract。

### 3. Entry / Starting Point

重新检查：

```text
crates/service/crates/inference/src/lib.rs
NODE-204 ResolvedModel
NODE-303 READY Artifact
NODE-103 compatibility/resource view
current llama-server binary discovery/config
```

### 4. Reuse Targets / Do Not Recreate

Reuse：现有 llama-server binary discovery/CLI knowledge、ResolvedModel、Hardware facts。  
Do Not Recreate：download/verification、Process Manager、Router registration。

### 5. Scope

#### Allowed

- llama.cpp / llama-server Runtime Adapter；
- binary resolution contract；
- args/env/working-dir generation；
- model path/context/GPU-related 参数的显式规则；
- readiness/health probe description；
- `ProcessSpec` schema；
- pure adapter tests。

#### Avoid

- actual `Command::spawn()`；
- PID/Child state；
- internal port allocation（NODE-402；可接受由 ProcessSpec 使用 port placeholder/requirement）；
- readiness polling implementation（NODE-403）；
- Local Channel registration；
- vLLM/SGLang/general plugin framework。

### 6. Behavior Contract

Inputs：ResolvedModel + verified Artifact + hardware/compatibility facts。  
Output：无副作用 `ProcessSpec`。

ProcessSpec 至少表达：

```text
runtime kind
binary / executable requirement
args
optional env
working directory if required
port binding requirement / placeholder
readiness endpoint/semantics
health endpoint/semantics
```

Runtime Adapter owns 参数与兼容性到运行规格的转换；不拥有进程生命周期。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
binary unavailable => spawn another runtime
unsupported model format => try anyway
missing READY artifact => use raw file path
spec generation => start process for validation
llama.cpp incompatibility => silently switch provider/router
add vLLM/SGLang abstraction to solve one llama.cpp case
```

### 8. Impact / Invariants

```text
persistence: none
external_calls: none during spec generation
billing/auth/routing: none
process side effect: none
filesystem: read validated artifact/runtime location only
```

Candidate invariant：**Runtime 决定如何运行；Process Manager 决定如何管理进程。**

### 9. Dependencies

前置：`NODE-103`、`NODE-204`、`NODE-303`。  
后续：`NODE-402`。

### 10. Stop Conditions

STOP IF：必须 spawn 才能生成 spec、需要重新下载/验证 Artifact、需要添加多 Runtime framework、需要修改 Router/Billing/Auth、或 current main 的 llama.cpp execution contract 已发生根本变化。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] llama.cpp Runtime Adapter 可由 ResolvedModel + facts 生成 ProcessSpec。
- [ ] ProcessSpec 包含明确 binary/args/env/workdir/health semantics。
- [ ] 参数/格式不兼容时返回结构化错误。
- [ ] spec generation 本身不启动进程。

### ✅ 边界保护

- [ ] 未持有 PID / Child。
- [ ] 未实现 NODE-402/403/501 的职责。
- [ ] 未扩展 vLLM/SGLang/general runtime framework。
- [ ] 未绕过 READY Artifact。

### ✅ 回归与验证

- [ ] pure tests 覆盖正常 GGUF、unsupported format、缺 binary、hardware/resource constraints。
- [ ] 固定输入生成确定 ProcessSpec。
- [ ] current InferenceService/Provider routing 不因本 Issue 被破坏。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 锁定真实 llama-server 参数与 binary discovery 行为。
- [ ] 只通过分支 + Pull Request 合并。
