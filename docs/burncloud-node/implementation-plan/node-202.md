---
title: "NODE-202：建立 Canonical Model ID 与 Alias 解析"
slug: /burncloud-node/implementation-plan/node-202/
---

# NODE-202：建立 Canonical Model ID 与 Alias 解析

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Model Resolver**  
**功能依赖：NODE-201**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须基于当时的 `burncloud/burncloud/main` 重新做 Evidence Audit，并通过 READY Gate。

### TL;DR

NODE-202 要把用户提交的模型名称稳定归一到唯一 canonical Model ID。Alias 只解决“你说的是哪个逻辑模型”，不决定具体 GGUF、量化或 Runtime。完成后，后续 Resolver 不再处理一堆同义名字，而只面对一个稳定身份。

### 背景与动机（Why）

如果 `qwen3-8b`、某个友好名称、历史名称甚至远端仓库名称都能各自成为内部身份，后面的 Model Resolver、模型状态、Local Channel 和日志就会出现多套 key。更危险的是，AI 很容易把 alias 解析顺手和“选择哪个文件”混在一起，让身份和实现再次耦合。

所以 NODE-202 只负责一个问题：**这个请求最终对应哪个 canonical model？** 至于当前机器跑哪个 Variant，必须等 NODE-203。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| canonical Model ID lookup | 不选择 Variant / Artifact |
| alias normalization | 不检测硬件 |
| 检测 alias 冲突 | 不下载模型 |
| unknown model 明确失败 | 不推断 Provider identity |
| 统一下游内部身份 | 不修改 Router 的 Provider model semantics |

### 风险与安全网（Risk）

> 这是**纯身份归一化**：解析不了就明确 `MODEL_NOT_FOUND` / 冲突错误，不能为了“尽量成功”去猜某个相近模型。

### 审批者关注点（Reviewer Focus）

1. 是否确认 Alias 只映射逻辑身份，不映射 Artifact？
2. 是否确认 canonical Model ID 与 Provider identity 是两个概念？
3. 是否确认未知/冲突 alias 必须 fail closed，而不是模糊匹配？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
requested model name
        ↓
normalize / alias lookup
        ↓
canonical Model ID
```

### 2. Evidence

- NODE-201 计划定义 canonical model 与 aliases 的声明事实。
- 当前 `ModelRouter` 直接按请求 `model` 查询 `channel_abilities`，但 NODE-202 的职责是 Node 本地模型身份解析，不得改写 Provider routing 的现有 model semantics。
- 当前 `InferenceService` 直接使用字符串 `model_id` 作为进程和 Local Channel key，进一步说明需要在本地执行链前先建立稳定 identity contract。

### 3. Entry / Starting Point

实现前重新检查：

```text
NODE-201 Manifest schema
current model registry/storage
existing model naming conventions
Router model mapping semantics (read-only evidence)
```

### 4. Reuse Targets / Do Not Recreate

Reuse：NODE-201 Manifest / registry、现有 model identity 数据中可复用部分。  
Do Not Recreate：Provider routing model mapper、Artifact resolver、fuzzy model search engine。

### 5. Scope

#### Allowed

- canonical ID lookup；
- alias normalization；
- alias uniqueness / conflict validation；
- explicit error types；
- deterministic resolver tests。

#### Avoid

- Variant / Hardware selection；
- Artifact / filename mapping；
- download；
- Runtime / Process；
- Provider identity inference；
- Router model-mapping behavior changes。

### 6. Behavior Contract

Inputs：requested model identifier + validated Model Manifest registry。  
Output：唯一 canonical Model ID。

确定性要求：

```text
canonical input -> same canonical output
known alias     -> exactly one canonical output
conflicting alias -> explicit error
unknown input     -> MODEL_NOT_FOUND-like structured error
```

Alias resolution 必须无外部 side effect。

### 7. Failure / Forbidden Fallbacks

禁止：

```text
unknown model => fuzzy nearest model
alias conflict => first one wins
alias => choose a specific GGUF file
alias => infer provider/model pair
missing registry => scan local files as identity source
```

### 8. Impact / Invariants

```text
persistence: none beyond reuse of manifest/registry
external_calls: none
billing/auth: none
provider routing: must remain unchanged
process/runtime: none
```

Candidate invariants：
- Alias 解析后只存在一个 canonical Model ID；
- Model ID != Provider identity；
- Model ID != Artifact filename。

### 9. Dependencies

前置：`NODE-201`。  
后续：`NODE-203`、`NODE-204`。

### 10. Stop Conditions

STOP IF：需要修改 Provider routing model mapping、需要 fuzzy guessing 才能解析、需要从文件名/本地文件扫描推断身份、或 scope 扩展到 Variant selection / download / Runtime。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] canonical Model ID 可以直接解析为自身。
- [ ] 已声明 alias 稳定映射到唯一 canonical ID。
- [ ] 冲突 alias 明确失败。
- [ ] 未知模型返回结构化诊断。

### ✅ 边界保护

- [ ] Alias 未决定 Artifact / Variant。
- [ ] 未修改 Provider routing 的 model semantics。
- [ ] 未增加 fuzzy guessing 或本地文件名推断。

### ✅ 回归与验证

- [ ] tests 覆盖 canonical、alias、冲突、未知、大小写/normalization 规则（若合同定义）。
- [ ] 固定输入得到确定输出。
- [ ] current Provider model routing 回归不受影响。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 锁定 registry/Manifest 的真实入口。
- [ ] 只通过分支 + Pull Request 合并。
