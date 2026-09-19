---
title: "类别五：Runtime 与 Process"
slug: /burncloud-node/implementation-plan/runtime-process/
---

# 类别五：Runtime 与 Process

Runtime / Process 层负责让一个 READY Model Artifact 在本机**无需用户操作**地变成健康可服务的 Runtime。

```text
Hardware / Platform
   ↓
Managed llama.cpp Runtime
   ↓
ProcessSpec
   ↓
Resource Admission + Port
   ↓
Spawn
   ↓
Readiness / Health
   ↓
READY
   ↓
Automatic Stop / Crash / Restart / Logs
```

关键原则：

- 用户不安装/寻找 `llama-server` 作为正常产品流程；
- 用户不提供端口、PID、GGUF 路径或启动参数；
- `Process Spawned != Model READY`；
- BurnCloud 对自己启动的所有模型进程负责清理；
- v0.1 只做最小资源准入，不建设复杂 GPU Scheduler。

本类别包括：

- **NODE-400**：确保 llama.cpp Runtime 自动可用；
- **NODE-401**：Runtime Adapter + ProcessSpec；
- **NODE-402**：资源准入、端口分配与 Spawn；
- **NODE-403**：Readiness / Health；
- **NODE-404**：自动 Stop / Crash / Restart / Logs。
