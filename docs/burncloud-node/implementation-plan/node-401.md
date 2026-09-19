---
title: "NODE-401：llama.cpp Runtime Adapter 与 ProcessSpec"
slug: /burncloud-node/implementation-plan/node-401/
---

# NODE-401：llama.cpp Runtime Adapter 与 ProcessSpec

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**功能依赖：NODE-400、NODE-103、NODE-204、NODE-303**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-401 要把“一个已经解析并验证好的模型应该如何运行”转换成无副作用 `ProcessSpec`。它只能使用 NODE-400 提供的 VERIFIED Runtime Artifact 和 NODE-303 提供的 READY Model Artifact；用户不需要提供 llama-server 路径、GGUF 路径、端口或命令参数。

### 背景与动机（Why）

当前 InferenceService 把找 binary、拼命令、spawn、health 和 Channel 注册混在一起。Demand-driven Node 需要把这些职责拆开：Runtime Adapter 只回答“怎么运行”，Process Manager 才真正执行。否则后台自动准备链无法稳定重试和诊断。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| VERIFIED Runtime + READY Artifact → ProcessSpec | 不实际 spawn |
| 自动生成 llama.cpp args/env/workdir | 不让用户填写参数 |
| 描述 port requirement / health probes | 不持有 PID / Child |
| 参数不兼容时明确失败 | 不下载 Runtime / Model |
| 固定输入生成确定 spec | 不注册 Router / Channel |

### 风险与安全网（Risk）

> ProcessSpec 生成不了就失败；不能通过“先启动看看”来验证配置，也不能绕过 Runtime/Artifact verification。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Runtime Adapter 不拥有进程？
2. 是否同意用户不提供任何底层运行参数？
3. 是否同意只有 VERIFIED Runtime + READY Artifact 才能生成 spec？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
ResolvedModel
+ READY Model Artifact
+ VERIFIED Runtime Artifact
+ Hardware/Compatibility facts
          ↓
llama.cpp Runtime Adapter
          ↓
ProcessSpec
```

### 2. Evidence

current InferenceService 会构造 `llama-server -m <file> --port <port> -c <ctx> -ngl <gpu_layers> --nobrowser` 并直接 spawn；current main 尚无独立 ProcessSpec contract。

### 3. Reuse Targets / Do Not Recreate

Reuse：current llama-server CLI knowledge、NODE-400 RuntimeArtifact、NODE-204 ResolvedModel、NODE-303 READY Artifact。  
Do Not Recreate：runtime download、model download、Process Manager、Router registration。

### 4. Scope

#### Allowed

- llama.cpp adapter；
- binary/path consumption from VERIFIED RuntimeArtifact；
- args/env/workdir generation；
- context/GPU-related explicit policy；
- port binding requirement/placeholder；
- readiness/health probe description；
- ProcessSpec schema；
- pure tests。

#### Avoid

- `Command::spawn()`；
- PID/Child state；
- runtime/model acquisition；
- actual port allocation（NODE-402）；
- readiness polling（NODE-403）；
- Channel registration；
- vLLM/SGLang/general plugin abstraction。

### 5. Behavior Contract

ProcessSpec 至少表达：

```text
runtime kind/version
verified executable path
model artifact path/reference
args
env
working directory
port binding requirement
readiness endpoint/semantics
health endpoint/semantics
```

spec generation 无网络、下载或 process side effect。

### 6. Failure / Forbidden Fallbacks

禁止：

```text
missing verified runtime => use PATH directly
missing READY artifact => use raw user path
unsupported format => try anyway
spec generation => spawn for validation
llama incompatibility => silently switch provider
```

### 7. Impact / Invariants

```text
persistence: none
external_calls: none
billing/auth/routing: none
process side effect: none
```

Candidate invariant：**Runtime Adapter 决定如何运行；Process Manager 决定如何管理运行中的进程。**

### 8. Dependencies

前置：NODE-400、NODE-103、NODE-204、NODE-303。  
后续：NODE-402、NODE-504。

### 9. Stop Conditions

STOP IF：必须 spawn 才能生成 spec、需要绕过 verified runtime/artifact、需要添加通用多 Runtime framework、或需要修改 Router/Billing/Auth。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] VERIFIED Runtime + READY Artifact 可生成稳定 ProcessSpec。
- [ ] 用户无需提供 executable/model path/port/gpu args。
- [ ] ProcessSpec 包含明确 health/readiness semantics。
- [ ] spec generation 不启动进程。

### ✅ 边界保护

- [ ] 未持有 PID/Child。
- [ ] 未重新下载 Runtime/Model。
- [ ] 未使用未验证 PATH binary 作为正常产品 fallback。
- [ ] 未实现 NODE-402/403/501 的职责。

### ✅ 回归与验证

- [ ] pure tests 覆盖正常 GGUF、unsupported format、missing verified runtime、resource incompatibility。
- [ ] 固定输入得到确定 ProcessSpec。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 锁定 current llama-server CLI contract。
- [ ] 只通过分支 + Pull Request 合并。


---

## 第四层：人类验收（Human Acceptance）

> 本节由 [Node 人类验收标准](/burncloud-node/implementation-plan/human-acceptance/) 生成。机器测试、CI 或 AI Review 不能替代这里的人工验收。

### NODE-401 — llama.cpp Runtime Adapter + ProcessSpec

**验收者：** Runtime 工程师。

**人工步骤：**
1. 给 Adapter 一个 READY Artifact + HardwareProfile。
2. 查看生成的 ProcessSpec。
3. 确认用户没有提供 GGUF 绝对路径、gpu_layers、内部端口或原始 CLI 参数。
4. 用明显非法配置验证明确失败。

**人类通过标准：** ProcessSpec 可执行、参数可解释、由 Runtime contract 产生，不把 PID/Child ownership混进 Runtime Adapter。

**人工判定失败：** 需要用户拼 CLI、Adapter 自己长期持有进程、或非法配置静默纠正成不可解释值。

**建议证据：** 一份有效 ProcessSpec + 一份非法配置失败。
