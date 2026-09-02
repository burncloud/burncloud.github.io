---
title: "NODE-400：确保 llama.cpp Runtime 自动可用"
slug: /burncloud-node/implementation-plan/node-400/
---

# NODE-400：确保 llama.cpp Runtime 自动可用

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**功能依赖：NODE-103**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须重新核对 current `burncloud/burncloud/main` 并通过 READY Gate。

### TL;DR

NODE-400 要保证用户不需要自己安装、寻找或配置 `llama-server`。BurnCloud 根据 OS / CPU / GPU / Driver 选择受支持的 Runtime 构建，验证完整性后提供一个 READY Runtime 给后续 ProcessSpec 使用。找不到合适 Runtime 时必须明确失败，不能把问题甩给用户去配 PATH。

### 背景与动机（Why）

当前 InferenceService 会尝试环境变量、本地路径和 PATH 查找 `llama-server`，这对开发环境够用，但不符合“用户只调用 `/v1`”的产品合同。如果 Node 仍要求用户额外安装 llama.cpp，那么模型自动下载和自动启动并没有真正闭环。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 根据平台/硬件选择受支持 Runtime 构建 | 不做大规模 Runtime Marketplace |
| 支持 bundled / managed download 两种实现 | 不让用户手工配置 PATH 才能工作 |
| 校验版本与完整性 | 不启动模型进程 |
| 缓存可复用 Runtime | 不处理 Model Artifact |
| 不可用时结构化失败 | 不静默切换到 Provider |

### 风险与安全网（Risk）

> Runtime 不可用时宁可明确失败，也不能下载未知二进制、跳过完整性校验或执行来源不明的程序。

### 审批者关注点（Reviewer Focus）

1. 是否同意 llama.cpp Runtime 由 BurnCloud 管理，而不是由用户安装？
2. 是否同意 v0.1 只支持明确批准的平台/Runtime 构建？
3. 是否同意 Runtime 完整性必须可验证？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

```text
Hardware / Platform facts
        ↓
Runtime requirement
        ↓
locate bundled runtime OR managed acquire
        ↓
version / integrity verification
        ↓
READY Runtime Artifact
```

### 2. Evidence

current InferenceService 会按 `BURNCLOUD_LLAMA_BIN`、本地路径和 PATH 查找 `llama-server`；current main 尚无 managed runtime availability contract。

### 3. Reuse Targets / Do Not Recreate

Reuse：existing installer/download primitives where appropriate、HardwareProfile、workspace/platform conventions。  
Do Not Recreate：Model DownloadManager semantics unnecessarily、Process Manager、general plugin marketplace。

### 4. Scope

#### Allowed

- supported platform/runtime catalog；
- bundled runtime discovery；
- managed runtime download if product packaging requires；
- version identity；
- checksum/signature/integrity verification；
- local runtime cache/path ownership；
- structured availability errors；
- tests for platform mapping and integrity failure。

#### Avoid

- model Artifact download；
- ProcessSpec generation（NODE-401）；
- process spawn；
- Local Channel registration；
- vLLM/SGLang/general runtime framework；
- arbitrary internet binary execution。

### 5. Behavior Contract

成功输出：

```text
RuntimeArtifact {
  runtime_kind,
  version,
  executable_path,
  platform_identity,
  integrity_status = VERIFIED
}
```

失败至少可表达：

```text
RUNTIME_UNSUPPORTED_PLATFORM
RUNTIME_UNAVAILABLE
RUNTIME_INTEGRITY_FAILED
RUNTIME_VERSION_UNSUPPORTED
```

只有 VERIFIED Runtime Artifact 可交给 NODE-401。

### 6. Failure / Forbidden Fallbacks

禁止：

```text
runtime missing => ask user to configure PATH as normal product flow
checksum mismatch => execute anyway
unknown source => download and run
unsupported platform => guess closest binary
runtime unavailable => silently alter Router/Provider policy
```

### 7. Impact / Invariants

```text
persistence: managed runtime cache only
external_calls: optional approved runtime distribution source
billing/auth/routing: none
process side effect: no model process spawn
```

Candidate invariant：**BurnCloud-managed local inference must use a verified Runtime Artifact.**

### 8. Dependencies

前置：NODE-103。  
后续：NODE-401、NODE-504。

### 9. Stop Conditions

STOP IF：需要执行未验证二进制、需要构建通用 Runtime marketplace、需要修改 Router/Billing/Auth、或 supported platform policy 无法明确。

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] 至少一种 v0.1 目标平台无需用户手工安装即可获得 READY llama.cpp Runtime。
- [ ] Runtime 有明确 version/platform identity。
- [ ] 完整性校验失败时不会执行。
- [ ] unsupported platform 返回结构化失败。

### ✅ 边界保护

- [ ] 未启动模型进程。
- [ ] 未下载 Model Artifact。
- [ ] 未引入 vLLM/SGLang/general marketplace。
- [ ] 未要求正常用户手工配置 PATH 才能完成产品闭环。

### ✅ 回归与验证

- [ ] tests 覆盖 bundled hit、managed acquire、unsupported platform、integrity failure。
- [ ] 固定平台 facts 映射到确定 runtime artifact。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确 runtime distribution source / integrity mechanism。
- [ ] 只通过分支 + Pull Request 合并。
