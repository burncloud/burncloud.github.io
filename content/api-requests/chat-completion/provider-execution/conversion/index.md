---
title: "Converted Provider Path"
slug: /api-requests/chat-completion/provider-execution/conversion/
type: runtime-flow
flow_id: user.api.chat.provider.convert
truth: STATIC_CONFIRMED_WITH_DYNAMIC_BOUNDARY
parent_flow: user.api.chat.provider
entry_points:
  - "PassthroughDecision::Convert"
  - "DynamicAdaptorFactory"
drill_down:
  - "user.api.chat.streaming"
  - "user.api.chat.provider.failure"
---

# Converted Provider Path

← [Provider Execution](/#/api-requests/chat-completion/provider-execution/)

## What happens here?

对 Chat Completion，前置 path filter 只保留 OpenAI/Zai，而 OpenAI Chat 会走 passthrough；因此当前用户流程中 Convert branch 对剩余可转换 candidate 进入 **⚠ Dynamic** `DynamicAdaptorFactory::get_adaptor()`。若 body 能解析为 `OpenAIChatRequest`，调用 adaptor 的 `convert_request()`；之后保留 stream/model 字段、应用 channel param/header override，再让 adaptor `build_request()` 构造真正 HTTP request 并发送。

## ICFG

```mermaid
flowchart TD
    E["Convert path"]
    AD["⚠ Dynamic adaptor<br/>get_adaptor(channel_type, api_version)"]
    OAI["尝试解析 OpenAIChatRequest"]
    PARSE{"typed parse success?"}
    CONV["⚠ Dynamic call<br/>adaptor.convert_request(&req)"]
    RAW["使用已解析 JSON body"]
    KEEP["恢复 stream / model 字段"]
    PARAM["应用 param_override"]
    RB["state.client.request(method,target_url)"]
    HDR["apply_header_override()"]
    BUILD["⚠ Dynamic call<br/>adaptor.build_request(...)"]
    SEND["req_builder.send().await"]
    RES{"response / network error"}
    OK["成功响应处理"]
    FAIL["failure / retry path"]
    E --> AD --> OAI --> PARSE
    PARSE -->|Yes| CONV --> KEEP
    PARSE -->|No| RAW --> KEEP
    KEEP --> PARAM --> RB --> HDR --> BUILD --> SEND --> RES
    RES -->|Success| OK
    RES -->|Failure| FAIL
    click AD "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L3067" "Open adaptor lookup" _blank
    click CONV "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L3086" "Open request conversion" _blank
    click BUILD "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L3143" "Open request build" _blank
    click FAIL "/#/api-requests/chat-completion/provider-execution/failure-retry/" "Failure drill-down" _self
```

## Dynamic / Unable to statically resolve

`convert_request()` 与 `build_request()` 的 concrete implementation 通过 runtime adaptor 调用。即使当前候选的 protocol/type 已知，Atlas 仍保留实际 factory dispatch 边界，不仅凭名称伪造 concrete method target。

## Continue Drilling Down

- → [Streaming Response](/#/api-requests/chat-completion/streaming-response/)
- → [Failure + Retry](/#/api-requests/chat-completion/provider-execution/failure-retry/)

## Source Evidence

- Chat path candidate type restriction: [`crates/router/src/lib.rs:L2160-L2182`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2160-L2182)
- Convert path: [`crates/router/src/lib.rs:L3067-L3159`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L3067-L3159)

**Confidence: HIGH for control flow; DYNAMIC for adaptor implementation.**
