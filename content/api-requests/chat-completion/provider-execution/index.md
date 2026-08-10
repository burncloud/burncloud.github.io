---
title: "Provider Execution — Overview"
slug: /api-requests/chat-completion/provider-execution/
type: runtime-flow
flow_id: user.api.chat.provider
truth: STATIC_CONFIRMED
parent_flow: user.api.chat
entry_points:
  - "proxy_logic candidate loop"
drill_down:
  - "user.api.chat.provider.loop"
  - "user.api.chat.provider.guard"
  - "user.api.chat.provider.dispatch"
  - "user.api.chat.provider.passthrough"
  - "user.api.chat.provider.convert"
  - "user.api.chat.provider.failure"
---

# Provider Execution — Overview

← [Chat Completion](/#/api-requests/chat-completion/) · ← [Channel Selection](/#/api-requests/chat-completion/channel-selection/)

## What happens here?

`proxy_logic()` 对已排序候选逐个尝试。每次 attempt 先处理本地 Rate Budget Shaper，再检查 Circuit Breaker；之后根据 channel protocol 选择 passthrough 或 conversion 路径，真正执行 `reqwest::RequestBuilder::send().await`。失败是否继续下一个候选由具体错误类型和分支决定。

## ICFG — Candidate Attempt

```mermaid
flowchart TD
    C["Ranked candidates (max 5)"]
    L["for (attempt, upstream) in candidates"]
    SH["本地 Rate Budget Shaper"]
    SA{"admitted / fail-open?"}
    NEXT["continue → next candidate"]
    CB["CircuitBreaker::allow_request(upstream)"]
    CBA{"allowed?"}
    URL["构造 target URL + channel protocol context"]
    JSON["解析 JSON body"]
    PT["should_passthrough(path, body, channel_type)"]
    D{"Passthrough or Convert?"}
    P["Passthrough HTTP path"]
    CV["⚠ Dynamic adaptor conversion path"]
    SEND["HTTP send().await"]
    RES{"response / network error"}
    OK["success / streaming processing"]
    FAIL["classify/record failure"]
    RETRY{"该错误允许 failover?"}
    RET["Return ProxyResult"]
    C --> L --> SH --> SA
    SA -->|Rejected| NEXT --> L
    SA -->|Admit/fail-open| CB --> CBA
    CBA -->|No| NEXT
    CBA -->|Yes| URL --> JSON --> PT --> D
    D -->|Passthrough| P --> SEND
    D -->|Convert| CV --> SEND
    SEND --> RES
    RES -->|Success| OK --> RET
    RES -->|Failure| FAIL --> RETRY
    RETRY -->|Yes| NEXT
    RETRY -->|No| RET
    click SH "/#/api-requests/chat-completion/provider-execution/shaper-circuit-breaker/" "Drill into guards" _self
    click D "/#/api-requests/chat-completion/provider-execution/protocol-dispatch/" "Drill into dispatch" _self
    click P "/#/api-requests/chat-completion/provider-execution/passthrough/" "Passthrough path" _self
    click CV "/#/api-requests/chat-completion/provider-execution/conversion/" "Conversion path" _self
    click FAIL "/#/api-requests/chat-completion/provider-execution/failure-retry/" "Failure / retry" _self
```

## Dynamic Boundary

`DynamicAdaptorFactory::get_adaptor(channel_type, api_version)` 返回具体 adaptor；该实现由运行时 channel type / API version 决定。**⚠ Dynamic — 不把某一 Provider 实现画成所有请求固定目标。**

## Continue Drilling Down

- → [Candidate Attempt Loop](/#/api-requests/chat-completion/provider-execution/candidate-attempt-loop/)
- → [Shaper + Circuit Breaker](/#/api-requests/chat-completion/provider-execution/shaper-circuit-breaker/)
- → [Protocol Dispatch](/#/api-requests/chat-completion/provider-execution/protocol-dispatch/)
- → [Passthrough Path](/#/api-requests/chat-completion/provider-execution/passthrough/)
- → [Conversion Path](/#/api-requests/chat-completion/provider-execution/conversion/)
- → [Failure + Retry](/#/api-requests/chat-completion/provider-execution/failure-retry/)

## Source Evidence

- [`crates/router/src/lib.rs:L2336-L4167`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L2336-L4167)

**Confidence: HIGH for loop/branches; DYNAMIC for concrete adaptor implementation.**
