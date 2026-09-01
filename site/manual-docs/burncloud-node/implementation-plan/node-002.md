---
title: "NODE-002：建立 Node 配置与共享上下文"
slug: /burncloud-node/implementation-plan/node-002/
---

# NODE-002：建立 Node 配置与共享上下文

**状态：PLANNED**  
**类别：Node Core**  
**依赖：NODE-001**

## 目标

建立 Node 级配置和共享 Context，使 HardwareProfile、模型状态、Runtime/Process 状态都通过明确依赖获得，而不是模块自行读取全局状态。

## 当前事实

现有 BurnCloud 已有 Settings、Database 与各服务状态；Node 不需要建立第二套配置数据库。

## 期望行为

Node Core 构造单一共享上下文，明确持有/引用 Node 所需已有服务和后续新增组件。

## 范围

**Allowed**：NodeConfig、NodeContext、已有 service handles 的组合。  
**Avoid**：复制 Settings、复制 Database、把业务逻辑塞进 Context。

## Invariants

- `INV-WORKSPACE-001`
- Candidate：Node 只有一个组合根（composition root）。

## 验证

- Node 初始化时依赖明确注入。
- 无重复数据库或 Router 实例被隐式创建。

## Done When

后续 Node 子系统都能从统一 Context 获得依赖，且 Context 自身不承担模型下载、路由或进程控制业务。