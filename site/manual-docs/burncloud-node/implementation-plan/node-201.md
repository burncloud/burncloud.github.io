---
title: "NODE-201：定义 Model Manifest"
slug: /burncloud-node/implementation-plan/node-201/
---

# NODE-201：定义 Model Manifest

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Model Resolver**  
**功能依赖：无**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须基于当时的 `burncloud/burncloud/main` 重做 Evidence Audit 并通过 READY Gate。

### TL;DR

NODE-201 要定义一份声明式 `Model Manifest`，明确“逻辑模型、Variant、Artifact、Runtime requirement”之间的关系。这样 BurnCloud 不再通过 GGUF 文件名猜模型身份，也能让同一个逻辑模型安全地拥有多个量化 / Runtime 变体。完成后，Resolver 会有稳定的事实输入，而不是临时规则集合。

### 背景与动机（Why）

现有 BurnCloud `ModelService` 能管理模型记录、访问 Hugging Face、筛选 GGUF 和构造下载 URL，但这些能力并没有定义“一个逻辑模型有哪些可选 Variant，以及每个 Variant 需要什么 Runtime / 资源”。如果直接从远端文件树或文件名推断，模型身份会和具体 Artifact 绑死，后续 alias、不同量化和不同 Runtime 会不断产生特殊判断。

因此 NODE-201 只负责建立**声明事实**：哪些 Variant 属于这个模型、它们是什么格式、指向什么 Artifact、需要什么 Runtime。下载、选择和执行都不属于本 Issue。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 定义 canonical model + Variant schema | 不下载 Artifact |
| 描述 format / quantization / artifact identity | 不启动 Runtime |
| 描述 runtime / resource requirements | 不做 Hardware-aware 选择 |
| 支持一个模型多个 Variant | 不自动抓取全部 Hugging Face 内容 |
| 校验 Manifest 冲突和缺失字段 | 不把文件名当模型身份 |

### 风险与安全网（Risk）

> 这是**声明式元数据合同**：错误 Manifest 应直接校验失败，而不是让 Resolver 在运行时靠猜测修补；不会改变现有 Provider routing。

### 审批者关注点（Reviewer Focus）

1. 是否同意 canonical Model ID 与 Artifact 文件名彻底分离？
2. 是否同意一个逻辑模型可声明多个 Variant？
3. 是否同意 Manifest 只描述事实和 requirements，不做下载或选择？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
Model Manifest
├─ canonical model identity
├─ aliases (identity facts only)
└─ variants[]
   ├─ format
   ├─ quantization
   ├─ artifact reference
   ├─ runtime requirement
   └─ resource requirement
```

### 2. Evidence

- `crates/service/crates/models/src/lib.rs` 当前提供模型 CRUD、Hugging Face model/file tree、GGUF filter、data dir 和 download URL 能力。
- 当前 `InferenceConfig` 仍直接接收 `model_id + file_path + gpu_layers`，说明逻辑模型与 Artifact/Runtime 尚未通过统一 resolver contract 分开。
- current main 尚无一份 Node 专用 Model Manifest 作为 Resolver 的 authoritative input。

### 3. Entry / Starting Point

实现前重新检查：

```text
crates/service/crates/models/
current model database schema / ModelInfo
NODE implementation location at current main
```

### 4. Reuse Targets / Do Not Recreate

Reuse：现有 model identity / storage 能力中可复用的部分、serde/workspace conventions。  
Do Not Recreate：下载器、Hugging Face crawler、Runtime manager、第二套模型数据库。

### 5. Scope

#### Allowed

- Manifest schema；
- canonical model fields；
- Variant schema；
- format / quantization / Artifact reference；
- runtime / resource requirements；
- schema validation；
- 最小 fixtures / examples。

#### Avoid

- alias resolution algorithm（NODE-202）；
- Hardware-aware selection（NODE-203）；
- ResolvedModel output（NODE-204）；
- download / verification；
- process/runtime startup；
- provider routing。

### 6. Behavior Contract

Inputs：静态/受控 Manifest 数据。  
Outputs：已校验的 model facts。

必须支持：

```text
one canonical model -> N variants
variant identity != artifact filename
requirements are declarative facts
invalid/ambiguous manifest -> explicit validation error
```

Manifest parsing/validation 不得产生网络、下载、进程或 Router side effect。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
missing format => infer from filename silently
missing quantization => guess from artifact name
missing runtime requirement => assume llama.cpp
invalid variant => ignore it and continue silently
manifest load => automatically download model metadata from internet
```

### 8. Impact / Invariants

```text
persistence: optional only if current architecture requires; no second model DB
external_calls: none required
billing/auth/routing: none
runtime/process: none
```

Candidate invariant：**Model ID 是稳定逻辑身份，Artifact 是可替换实现细节。**

### 9. Dependencies

前置：无。  
后续：`NODE-202`、`NODE-203`、`NODE-204`。

### 10. Stop Conditions

STOP IF：必须把文件名当唯一模型身份、必须启动下载/Runtime 才能解析 Manifest、必须建立第二套模型数据库、或 scope 扩展到 alias/selection/process execution。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] 定义稳定、可校验的 Model Manifest schema。
- [ ] 一个 canonical model 可声明多个 Variant。
- [ ] Variant 可表达 format、quantization、Artifact、runtime/resource requirements。
- [ ] Artifact 文件名不承担模型身份职责。

### ✅ 边界保护

- [ ] Manifest parser 无下载、网络、Runtime 或 Router side effect。
- [ ] 未实现 NODE-202/203/204 的职责。
- [ ] 未创建第二套模型数据库。

### ✅ 回归与验证

- [ ] tests 覆盖 valid、缺字段、重复 Variant、冲突 identity、多个 Variant。
- [ ] 非法 Manifest 明确失败，不通过字符串猜测修复。
- [ ] 现有 ModelService 行为不被破坏。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确 Manifest 的 authoritative storage/location。
- [ ] 只通过分支 + Pull Request 合并。
