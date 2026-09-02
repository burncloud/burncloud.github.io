---
title: "NODE-201：定义 Model Manifest 与首批可用模型目录"
slug: /burncloud-node/implementation-plan/node-201/
---

# NODE-201：定义 Model Manifest 与首批可用模型目录

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Model Resolver**  
**功能依赖：无**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须基于当时的 `burncloud/burncloud/main` 重做 Evidence Audit 并通过 READY Gate。

### TL;DR

NODE-201 要定义稳定的 `Model Manifest`，并随 BurnCloud v0.1 交付一组真实可用的模型目录。用户只写 `model=qwen-4b`，Node 就能知道有哪些 Variant、Artifact、Runtime 和资源要求，而不是让用户自己找 GGUF。只有 Schema 没有真实模型数据，不算完成。

### 背景与动机（Why）

自动化 Node 的前提是系统自己知道“这个模型是什么、有哪些可运行版本、从哪里获得、需要什么资源”。如果这些事实靠文件名、Hugging Face 搜索结果或运行时猜测，后续 Resolver、下载和 Runtime 都会产生不同答案。

因此 Manifest 是模型事实源；v0.1 还必须附带首批 curated manifests，让真实 `/v1` 模型需求可以直接进入 Resolver，而不是要求用户先配置模型文件。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 定义 canonical model + Variant schema | 不下载 Artifact |
| 描述 Artifact source / identity / size | 不启动 Runtime |
| 描述 runtime / resource requirements | 不做 Hardware-aware 选择 |
| 随 v0.1 提供真实 curated manifests | 不让用户填写 GGUF 路径 |
| 校验 Manifest 冲突和缺失字段 | 不在线抓取后静默猜字段 |

### 风险与安全网（Risk）

> 这是声明事实，不是执行逻辑：错误 Manifest 必须校验失败；未知事实保持 unknown，不能为了自动化而猜测。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Model ID 与 Artifact 文件名彻底分离？
2. 是否同意 v0.1 必须附带首批真实 manifests，而不是只有 schema？
3. 是否同意 Manifest 只描述事实，不承担下载、选择或启动？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
canonical model
├─ aliases[]
└─ variants[]
   ├─ format / quantization
   ├─ artifact identity
   ├─ artifact source
   ├─ expected size / integrity facts
   ├─ runtime requirement
   └─ resource requirement
```

同时提供一组版本明确、可在 v0.1 E2E 中真实使用的 curated manifests。

### 2. Evidence

- current ModelService 已有 Hugging Face model/file tree、GGUF filter、data dir 和 download URL 能力。
- current InferenceConfig 仍直接接收 `model_id + file_path + gpu_layers`，逻辑模型与 Artifact/Runtime 尚未解耦。
- current main 没有 Node authoritative Model Manifest catalog。

### 3. Reuse Targets / Do Not Recreate

Reuse：现有 model identity/storage、serde/workspace conventions、可复用的 Hugging Face source knowledge。  
Do Not Recreate：第二套 model DB、下载器、Runtime manager、在线搜索引擎。

### 4. Scope

#### Allowed

- Manifest schema；
- canonical ID / alias facts；
- Variant schema；
- artifact source / expected size / integrity metadata；
- runtime/resource requirements；
- schema validation；
- curated manifest storage/versioning；
- 首批真实可用模型 fixtures/catalog。

#### Avoid

- alias resolution algorithm（NODE-202）；
- Variant selection（NODE-203）；
- download / verification；
- Runtime / Process；
- Provider routing。

### 5. Behavior Contract

```text
one canonical model -> N variants
variant identity != artifact filename
artifact source is explicit
requirements are declarative facts
invalid/ambiguous manifest -> explicit validation error
```

Manifest parsing不得产生网络、下载、进程或 Router side effect。

### 6. Failure / Forbidden Fallbacks

禁止：

```text
missing format => infer silently from filename
missing quantization => guess from artifact name
missing runtime => assume llama.cpp
missing size => invent estimate
invalid variant => ignore silently
unknown model => search internet and auto-trust result
```

### 7. Impact / Invariants

```text
persistence: curated/static source or existing model storage only
external_calls: none required for parsing
billing/auth/routing: none
runtime/process: none
```

Candidate invariant：**Model ID 是稳定逻辑身份，Artifact 是声明式实现细节。**

### 8. Dependencies

前置：无。  
后续：NODE-202、NODE-203、NODE-204、NODE-504。

### 9. Stop Conditions

STOP IF：必须把文件名当唯一身份、必须执行下载/Runtime 才能理解 Manifest、必须建立第二套模型数据库、或 curated catalog 无法给出真实可验证来源。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] 存在稳定、可校验的 Model Manifest schema。
- [ ] 一个 canonical model 可声明多个 Variant。
- [ ] Variant 可表达 source、size、format、quantization、Artifact、runtime/resource requirements。
- [ ] BurnCloud v0.1 随包/仓库提供一组真实可用、版本明确的 curated manifests。
- [ ] NODE-503 的测试模型可完全由 catalog 解析，不需要人工填写 GGUF URL/path。

### ✅ 边界保护

- [ ] Manifest parser 无网络、下载、Runtime、Router side effect。
- [ ] 未实现 NODE-202/203/204 的执行职责。
- [ ] 未创建第二套 model DB。

### ✅ 回归与验证

- [ ] tests 覆盖 valid、缺字段、重复 Variant、冲突 identity、多个 Variant。
- [ ] 非法 Manifest 明确失败，不通过字符串猜测修复。
- [ ] curated manifests 的 source/identity 可被验证。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 锁定 authoritative catalog location/versioning。
- [ ] 只通过分支 + Pull Request 合并。
