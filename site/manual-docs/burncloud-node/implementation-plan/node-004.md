---
title: "NODE-004：建立 Gateway / Protocol Routing Compatibility Gate"
slug: /burncloud-node/implementation-plan/node-004/
---

# NODE-004：建立 Gateway / Protocol Routing Compatibility Gate

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Node Core / Data Plane Compatibility**  
**功能依赖：NODE-003**

> 这是实施计划，不是 Codex 的直接开发授权。真正实现前必须基于当时的 `burncloud/burncloud/main` 重新做 Evidence Audit，并通过 READY Gate。

### TL;DR

NODE-004 不开发第二个 Gateway，也不重写 Protocol Router。它只做一件事：把 BurnCloud Node 产品文档已经承诺的多协议入口、Raw Proxy First、Protocol Translator 边界变成一套可重复验收的兼容性 Gate。完成后，我们能够明确证明 OpenAI Chat / Responses、Anthropic Messages、Gemini、Ollama 等入口仍通过现有统一 Server / Router 工作，同协议请求尽量原样透传，只有协议不一致时才进入 Translator。

### 背景与动机（Why）

BurnCloud Node 首页和 Protocol Routing 文档把 Local API Gateway 与 Protocol Routing 定义为 Node 的核心产品能力，但当前 Implementation Plan 主要通过 NODE-003 说明“复用现有 Server / Router”，并没有一条独立 Issue 对完整协议矩阵、Raw Proxy 字段保留和 Translator 启用条件负责。

这会造成一个危险空档：本地模型链即使全部完成，Node 仍可能在某个协议上破坏 streaming、unknown vendor fields、query/header，或者把所有请求都先转换成统一 Body，而 Implementation Plan 没有一个明确的 Gate 会阻止这种回归。

NODE-004 因此是**兼容性与回归合同**，不是新数据面设计。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 建立协议入口兼容矩阵 | 不创建 NodeGateway |
| 验证 URL → Protocol Detection | 不创建第二个 Protocol Router |
| 验证 model_id → existing ModelRouter | 不改变 Provider scoring/failover |
| 验证 same protocol → Raw Proxy | 不把所有请求统一重建 |
| 验证 different protocol → Translator | 不要求 Translator 成为所有请求必经层 |
| 验证 streaming / unknown fields 保留 | 不扩大到 BurnCloud Network 实现 |

### 风险与安全网（Risk）

> NODE-004 的正确结果可以是“发现现有某协议不满足产品合同并阻塞后续发布”，而不是为了让测试变绿就在本 Issue 中重写整个协议栈。

### 审批者关注点（Reviewer Focus）

1. 是否同意 Gateway / Protocol Routing 作为产品能力必须有独立验收 Gate？
2. 是否同意同协议优先 Raw Proxy，而不是统一内部 AI Body？
3. 是否同意 v0.1 的 Network Route Target 只保留架构扩展位，不在本 Issue 实现 BurnCloud Network？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立 Node v0.1 数据面兼容性合同：

```text
Client Request
    ↓
existing BurnCloud Server
    ↓
URL / Path → Protocol Detection
    ↓
minimal model_id extraction
    ↓
existing ModelRouter
    ↓
protocol match?
  ├─ yes → Raw Proxy
  └─ no  → Protocol Translator
    ↓
Response / Stream
```

### 2. Evidence

STATIC CONFIRMED：

- BurnCloud 已存在 `/v1/chat/completions`、`/v1/messages`、Gemini 等数据面入口；
- NODE-003 已要求 Node 模式复用 existing Server / Router；
- Node 产品文档明确声明 Raw Proxy First：same protocol 原样透传，different protocol 才转换；
- 产品文档还声明 OpenAI Responses、Ollama 等入口属于目标协议矩阵；
- 当前 Implementation Plan 尚无一个 Issue 独立承担完整协议兼容性验收。

### 3. Entry / Starting Point

READY Audit 重新检查：

```text
crates/server/src/lib.rs
crates/router/src/lib.rs
crates/router/src/model_router.rs
existing /v1 and protocol-specific route registration
existing raw proxy path
existing protocol translator path
streaming response path
NODE-003
```

### 4. Reuse Targets / Do Not Recreate

Reuse：existing Server、ModelRouter、当前协议检测/Raw Proxy/Translator、Auth/Billing/Quota、安全边界、现有 streaming transport。

Do Not Recreate：

```text
NodeGateway
NodeProtocolRouter
BurnCloudUnifiedRequest
second streaming stack
second auth boundary
```

### 5. Scope

#### Allowed

- 定义和补齐代表性协议兼容测试；
- 必要的最小 bug fix，使 current implementation 满足已批准的产品合同；
- URL/Protocol detection 回归；
- model_id 最小提取回归；
- Raw Proxy method/path/query/header/body/streaming preservation 回归；
- Translator 仅在 protocol mismatch 时启用的回归；
- unsupported/invalid protocol error contract；
- Provider-only 与 Local candidate 共享同一 Router 的回归。

#### Avoid

- 第二 Gateway/Router；
- Provider scoring/failover 改造；
- BurnCloud Network/P2P；
- Model Resolver/Preparation/Runtime；
- 全量协议栈重写；
- 新的统一 AI Body。

### 6. Behavior Contract

#### Ingress Matrix

Node v0.1 至少建立以下产品兼容目标：

```text
openai-chat
openai-responses
anthropic-messages
google-gemini
ollama-chat / ollama-generate
```

如果 current-main 对其中某项尚未实现，READY Gate 必须明确该项是：

```text
SUPPORTED + verify
or
BLOCKED + separate implementation dependency
```

不能因为文档写了就由 Codex 自行猜实现方式。

#### Raw Proxy Contract

same protocol 时默认保留：

```text
HTTP method
path semantics
query parameters
request body
streaming semantics
unknown vendor fields
protocol-specific fields
```

只允许修改完成代理所必需的连接信息，例如 upstream base URL、Host、upstream Authorization/API key、hop-by-hop headers，以及 route 明确声明的最小 model mapping。

#### Translator Contract

只有入口协议与目标 Route Target 协议不一致时才进入 Translator。Translator 不得成为所有请求的统一数据模型入口。

### 7. Failure / Forbidden Fallbacks

结构化失败至少区分：

```text
UNSUPPORTED_PROTOCOL
INVALID_REQUEST
MODEL_UNAVAILABLE / no route (owned by routing boundary)
TRANSLATION_UNSUPPORTED (when applicable)
```

禁止：

```text
unknown field => drop silently
stream=true => convert to non-stream response
protocol unknown => guess OpenAI
same protocol => rebuild entire body
URL => hard bind Provider
translator missing => silently send malformed raw request
```

### 8. Impact / Invariants

```text
persistence: none
external_calls: existing upstream calls only
billing_usage_quota: unchanged
auth_authorization: unchanged
routing_provider: compatibility only; selection semantics unchanged
public_api_http: yes — compatibility gate for existing/approved protocol surface
runtime_process: none
```

必须保持：

- existing ModelRouter 是唯一 Route Engine；
- security/Auth/Billing/Quota 继续经过现有统一边界；
- Raw Request 与 thin Route Context 分离；
- same protocol → Raw Proxy First；
- Network 不属于 Node v0.1 本 Issue 实现范围。

### 9. Dependencies

前置：NODE-003。  
最终产品验收：NODE-503 应把 NODE-004 作为 Node v0.1 前置 Gate 之一。

### 10. Stop Conditions

```text
STOP IF:
- compatibility requires creating a second Gateway/Router
- current source disproves a documented protocol assumption materially
- satisfying one protocol requires global unified-body redesign
- Provider scoring/failover must change
- Auth/Billing/Quota must be weakened
- BurnCloud Network implementation becomes necessary
- required protocol cannot be meaningfully verified in current environment
```

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] v0.1 协议矩阵有明确 supported / blocked 状态。
- [ ] URL/Path 可以稳定识别协议，不直接绑定 Provider。
- [ ] model_id 只作为路由所需最小上下文进入 existing ModelRouter。
- [ ] same protocol 默认走 Raw Proxy。
- [ ] different protocol 才进入 Translator。
- [ ] unsupported/invalid protocol 有明确错误。

### ✅ Raw Proxy 保护

- [ ] unknown vendor fields 在同协议路径不被无故删除。
- [ ] query / protocol-specific fields 保持。
- [ ] streaming semantics 保持。
- [ ] 只改必要 upstream connection information。

### ✅ 边界保护

- [ ] 未创建 NodeGateway / NodeProtocolRouter。
- [ ] 未创建 BurnCloudUnifiedRequest 或第二套 streaming stack。
- [ ] 未改变 Provider ranking/failover、Auth、Billing、Quota。
- [ ] 未实现 BurnCloud Network/P2P。

### ✅ 回归与验证

- [ ] OpenAI Chat 代表性 request/stream 通过。
- [ ] OpenAI Responses 代表性 request/stream 有明确验证或明确 blocker。
- [ ] Anthropic Messages 代表性 request/stream 通过或有明确 blocker。
- [ ] Gemini 代表性 request 通过或有明确 blocker。
- [ ] Ollama chat/generate 代表性 request 有明确验证或明确 blocker。
- [ ] 至少一个 protocol mismatch Translator 场景通过。
- [ ] Provider-only 请求仍使用现有统一 Server / Router。

### ✅ 工程流程

- [ ] current-main Evidence Audit 完成。
- [ ] Engineering Issue 通过 READY Gate。
- [ ] Task Contract 明确真实 protocol detection / raw proxy / translator 路径。
- [ ] 实现只通过分支 + Pull Request 合并。
