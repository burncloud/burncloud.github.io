---
title: "类别六：Local Channel Integration"
slug: /burncloud-node/implementation-plan/local-channel/
---

# 类别六：Local Channel Integration

READY 的本地 Runtime 必须作为现有 BurnCloud Router 的 Channel / Ability 进入数据面，而不是建立 LocalRouter 旁路。

## Issue

| ID | 功能 | 依赖 | 状态 |
|---|---|---|---|
| NODE-501 | READY Runtime 注册 Local Channel / Ability | NODE-403 | PLANNED |
| NODE-502 | 健康状态联动、摘除与注销 | NODE-404, NODE-501 | PLANNED |
| NODE-503 | `localhost:3000` 本地推理完整 E2E | NODE-003, NODE-502 | PLANNED |

NODE-503 通过后，才认为 BurnCloud Node v0.1 的本地执行主链闭环。