---
title: "BurnCloud Runtime Flow & ICFG Atlas"
slug: /
type: runtime-flow
flow_id: user.burncloud
truth: STATIC_CONFIRMED
---

# BurnCloud Runtime Flow & ICFG Atlas

本 Atlas **只从用户行为开始**。左侧菜单不是 crate / module / file tree，而是用户可以触发的执行流程。

## User Execution Tree

```mermaid
flowchart TD
    U["用户使用 BurnCloud"]
    API["API 请求"]
    ACC["账号访问"]
    CON["Console 管理"]
    OPS["内部运维动作"]
    U --> API
    U --> ACC
    U --> CON
    U --> OPS
    API --> CHAT["Chat Completion"]
    API --> VIDEO["Video Task Polling"]
    API --> MODELS["查询可用模型"]
    API --> USAGE["查询 API Usage"]
    ACC --> REG["注册账号"]
    ACC --> LOGIN["登录账号"]
    ACC --> RESET["找回 / 重置密码"]
    CON --> CH["Channel 管理"]
    CON --> TK["API Token 管理"]
    CON --> UM["用户与余额管理"]
    CON --> OBS["日志 / Billing / Monitor / Cache"]
    OPS --> HEALTH["Health / Metrics"]
    OPS --> PRICE["Price Sync"]
    OPS --> CB["Circuit Breaker Trip-All"]
    click API "/api-requests/" "进入 API 请求" _self
    click ACC "/account/" "进入账号访问" _self
    click CON "/console/" "进入 Console 管理" _self
    click OPS "/operator/" "进入内部运维" _self
```

## Reading Rule

从左侧选一个用户动作：

**User Action → End-to-End Flow → Drill-down ICFG → 更小的 ICFG → Source Evidence**。

图中出现 **⚠ Dynamic** 时，表示具体实现由运行时配置 / trait object 决定，Atlas 不把它画成静态确定路径。
