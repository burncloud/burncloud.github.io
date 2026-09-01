---
title: "NODE-404：Stop / Crash / Restart / Logs"
slug: /burncloud-node/implementation-plan/node-404/
---

# NODE-404：Stop / Crash / Restart / Logs

**状态：PLANNED**  
**类别：Runtime 与 Process**  
**依赖：NODE-403**

## 目标

补齐模型进程停止、异常退出、最小重启策略和 Runtime 日志生命周期。

## 期望行为

Node 关闭时子进程可控退出；异常 crash 不残留 READY 状态；重启策略必须有边界，不能无限重启风暴。

## 范围

**Allowed**：shutdown、crash detection、bounded restart、stdout/stderr capture。  
**Avoid**：复杂 GPU scheduler、多机恢复。

## Invariants

- Candidate：进程真实状态必须驱动可用状态。

## 验证

主动 stop、crash、restart limit、Node shutdown 清理均覆盖。

## Done When

Process Manager 对进程生命周期拥有完整责任，并能向 NODE-502 提供可靠健康状态。