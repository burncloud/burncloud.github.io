---
title: "Chat Protocol Dispatch"
slug: /api-requests/chat-completion/provider-execution/protocol-dispatch/
type: runtime-flow
flow_id: user.api.chat.provider.dispatch
truth: STATIC_CONFIRMED_WITH_DYNAMIC_BOUNDARY
parent_flow: user.api.chat.provider
entry_points:
  - "proxy_logic candidate loop"
drill_down:
  - "user.api.chat.provider.passthrough"
  - "user.api.chat.provider.convert"
---

# Chat Protocol Dispatch

← [Provider Execution](/#/api-requests/chat-completion/provider-execution/) · ← [Chat Completion](/#/api-requests/chat-completion/)

## What happens here?

对 `/v1/chat/completions`，`proxy_logic()` 在创建 `Upstream` 前已经跳过非 `OpenAI | Zai` Channel。进入候选执行后，当前 upstream protocol 被映射成 `ChannelType` 并交给 `should_passthrough()`：OpenAI Channel 对 Chat path 明确走原生透传；需要 Convert 的路径再通过 `DynamicAdaptorFactory` 按运行时 ChannelType/API version 获取 adaptor，因此 concrete adaptor 不能静态固定。

## ICFG

```mermaid
flowchart TD
    E["Chat candidate 已进入执行循环<br/>proxy_logic()"]
    FILTER{"ChannelType 是 OpenAI / Zai?"}
    SKIP["No → 在 Upstream 构造前 skip candidate"]
    UP["Yes → 构造 Upstream 并进入 candidate loop"]
    CT["将 upstream.protocol 映射为 ChannelType"]
    JSON["解析当前 request JSON"]
    JOK{"JSON valid?"}
    NEXT["No → continue next candidate"]
    SP["决定原生透传还是转换<br/>should_passthrough()"]
    D{"PassthroughDecision"}
    PT["OpenAI Chat 原生透传"]
    DA["⚠ Dynamic<br/>get_adaptor(channel_type, api_version)"]
    CV["进入协议转换路径"]
    E --> FILTER
    FILTER -->|No| SKIP
    FILTER -->|Yes| UP --> CT --> JSON --> JOK
    JOK -->|No| NEXT
    JOK -->|Yes| SP --> D
    D -->|Passthrough| PT
    D -->|Convert| DA --> CV
    click FILTER "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2160" "Open Chat path filter" _blank
    click SP "https://github.com/burncloud/burncloud/blob/main/crates/router/src/passthrough.rs#L47" "Open passthrough decision" _blank
    click PT "/#/api-requests/chat-completion/provider-execution/passthrough/" "Passthrough drill-down" _self
    click CV "/#/api-requests/chat-completion/provider-execution/conversion/" "Conversion drill-down" _self
    click DA "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L3067" "Open dynamic adaptor lookup" _blank
```

## Decisions

- `/v1/chat/completions` is an OpenAI-format path, so non-OpenAI/Zai channels are skipped before `Upstream` construction.
- OpenAI Channel + `/v1/chat/completions` → `PassthroughDecision::Passthrough`.
- Other selected protocol paths that reach Convert → **⚠ Dynamic** adaptor lookup; this Atlas does not invent the concrete implementation.

## Continue Drilling Down

- → [Passthrough Path](/#/api-requests/chat-completion/provider-execution/passthrough/)
- → [Conversion Path](/#/api-requests/chat-completion/provider-execution/conversion/)

## Source Evidence

- Chat/OpenAI path candidate filter: [`crates/router/src/lib.rs:L2160-L2182`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2160-L2182)
- Passthrough decision: [`crates/router/src/passthrough.rs:L47-L87`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/passthrough.rs#L47-L87)
- Dynamic adaptor lookup: [`crates/router/src/lib.rs:L3067-L3071`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L3067-L3071)

**Confidence: HIGH for static branch selection; DYNAMIC for the concrete conversion adaptor.**
