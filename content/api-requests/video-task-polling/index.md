---
title: "Video Task Polling"
slug: /api-requests/video-task-polling/
type: runtime-flow
flow_id: user.api.video_poll
truth: STATIC_CONFIRMED
parent_flow: user.api
entry_points:
  - "GET /v1/videos/{task_id}"
---

# Video Task Polling

← [API 请求](/api-requests/)

## What happens here?

`GET /v1/videos/{task_id}` 在正常 `proxy_logic()` 之前被特殊处理，因为它没有 model 可重新选路。系统读取创建视频任务时保存的 task→channel mapping，再读取该 Channel 的 base URL/key，直接对原 Channel 发 GET。

## ICFG

```mermaid
flowchart TD
    E["GET /v1/videos/{task_id}<br/>proxy_handler special branch"]
    T["RouterVideoTaskModel::get_by_task_id(task_id)"]
    TF{"mapping exists?"}
    E404["Return 404 task_not_found"]
    CH["ChannelProviderModel::get_by_id(task.channel_id)"]
    CF{"channel exists?"}
    E502A["Return 502 channel_unavailable"]
    URL["base_url + /v1/videos/{task_id}"]
    HTTP["reqwest GET + Bearer channel.key + timeout"]
    RES{"upstream result"}
    PASS["Return upstream status/body"]
    E502B["Return 502 bad_gateway"]
    E --> T --> TF
    TF -->|No| E404
    TF -->|Yes| CH --> CF
    CF -->|No| E502A
    CF -->|Yes| URL --> HTTP --> RES
    RES -->|Ok| PASS
    RES -->|Err| E502B
    click E "https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1626" "Open polling branch" _blank
```

## State / Side Effects

- **DB READ:** video task mapping + channel config.
- **External HTTP GET:** selected historical channel.
- No normal ModelRouter re-selection on this branch.

## Source Evidence

- [`crates/router/src/lib.rs:L1626-L1707`](https://github.com/burncloud/burncloud/blob/main/crates/router/src/lib.rs#L1626-L1707)

**Confidence: HIGH — STATIC CONFIRMED**
