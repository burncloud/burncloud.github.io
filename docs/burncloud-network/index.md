---
title: "BurnCloud Network"
slug: /burncloud-network/
hide_table_of_contents: false
---

# BurnCloud Network

BurnCloud Network 是建立在 BurnCloud Node 之上的可选网络能力。它不是 BurnCloud Node 运行本地模型的前提：Node 应先能独立工作，再选择是否加入私有网络或 BurnCloud Network。

```mermaid
flowchart LR
    APP["Application"] --> NODE["BurnCloud Node"]
    NODE --> LOCAL["Local Model"]
    NODE -. "when needed" .-> NETWORK["BurnCloud Network"]
    NETWORK --> PROVIDER["Remote BurnCloud Node"]
```

## 设计原则

### Node 先独立运行

```text
BurnCloud Node
   ↓
localhost:3000/v1
   ↓
Local Model
```

即使完全不连接 BurnCloud Network，本地能力仍然成立。

### Network 是可插拔能力

未来可以形成：

```text
Local
  ↓ fallback
Private Network
  ↓ fallback
BurnCloud Network
```

### 供应商控制自己的 Node

```text
BurnCloud Network
       ↓ request
Supplier BurnCloud Node
       ↓ local policy
Supplier GPU / Runtime
```

Network 不直接获得供应商内部 GPU 的 root 控制权；供应商决定开放哪些模型、多少容量以及什么时候退出。

## 后续技术主题

后续会继续拆成独立页面：Node Identity、Join / Leave、Provider Capability、Private Network、Request Routing、Usage Receipt、Reconciliation、Settlement、Trust / Verification。

## 当前状态

**🔭 Architecture / Future**：当前优先完成 BurnCloud Node v0.1。BurnCloud Network 建立在稳定 Node、统一 `/v1`、本地模型生命周期和 Node Identity 之上，不反过来阻塞 Node MVP。
