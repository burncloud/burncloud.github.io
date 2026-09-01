---
title: "NODE-003：组合现有 Server / Router 为 Node 模式"
slug: /burncloud-node/implementation-plan/node-003/
---

# NODE-003：组合现有 Server / Router 为 Node 模式

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Node Core**  
**功能依赖：NODE-001、NODE-002**

> 这是实施计划，不是 Codex 的直接开发授权。实现前必须基于当时 `burncloud/burncloud/main` 重做 Evidence Audit，并通过 READY Gate。

### TL;DR

NODE-003 要让 `burncloud node` 直接复用 BurnCloud 现有 Server 和 Router，对外仍然通过现有 `localhost:3000/v1/...` 数据面提供服务。这样 Node 只增加“本地可路由目标”，不会再造第二套 Gateway 或 Router。完成后，Provider 与未来 Local Runtime 可以继续走同一条认证、路由和数据面入口。

### 背景与动机（Why）

BurnCloud 当前已经有统一 Axum Server，数据面 Router 作为 fallback 被挂在同一个应用里，安全边界也覆盖显式路由和 fallback。如果 Node 再创建自己的 HTTP Server、OpenAI Gateway 或 LocalRouter，就会立即产生第二套入口、第二套认证边界和第二套路由语义。

所以 NODE-003 的核心不是“开发 Node Gateway”，而是**证明 Node 模式只是现有 BurnCloud Server / Router 的一种组合方式**。本地模型以后通过 Channel / Ability 接入已有 Router，而不是从旁边绕过去。

### 范围速览（In / Out）

| ✅ 做 | ❌ 不做 |
| --- | --- |
| 让 Node 模式复用现有统一 Server | 不创建 NodeGateway / 第二个 HTTP Server |
| 复用现有 data-plane Router | 不创建 NodeRouter / LocalRouter |
| 保持 `localhost:3000/v1/...` 为统一入口 | 不改变 Provider routing 语义 |
| 保留现有 security boundary | 不绕过 Auth / Billing / quota |
| 为后续 Local Channel 留出组合位置 | 不在本 Issue 启动本地模型 |

### 风险与安全网（Risk）

> 这是**组合方式调整而不是数据面重写**：如果实现需要重建 Gateway、改变 Router 选择算法或放松安全边界，就说明已经越过 NODE-003，Codex 必须停止。

### 审批者关注点（Reviewer Focus）

1. **是否确认 BurnCloud Node 不拥有第二个 Gateway / Router？**
2. **是否确认 Node 的外部 AI API 继续由现有统一 Server 提供？**
3. **是否确认 Local Runtime 未来只能作为现有 Router 的候选目标接入，而不是旁路数据面？**

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立 Node profile 与现有 Server / Router 的组合合同：

```text
burncloud node
      ↓
Node Core / NodeContext
      ↓
existing burncloud-server
      ↓
existing burncloud-router
      ↓
localhost:3000/v1/...
```

NODE-003 不创建新的请求数据面。

### 2. Evidence

#### STATIC CONFIRMED — Server 已是统一 Axum application

`crates/server/src/lib.rs :: create_app` 当前组合：

- `/health`；
- Management API；
- internal Router routes；
- optional LiveView；
- data-plane `router_app` 作为 `fallback_service`。

对应 `INV-RUNTIME-002`。

#### STATIC CONFIRMED — security boundary 覆盖整个统一应用

`create_app()` 在统一 Router 外层应用 `security_boundary_middleware`，显式路由与 data-plane fallback 都在同一安全边界下。

#### STATIC CONFIRMED — Router 已是现有数据面权威

`ModelRouter` 从 `channel_abilities` 获取候选，继续执行 availability、OrderType、Affinity、Scorer 和 failover 排序。NODE-003 不得建立平行 route engine。

#### STATIC CONFIRMED — `start_server()` 当前负责创建 Database 并启动统一 App

Node profile 如何复用这条 construction path，必须在 READY Audit 中根据当时 main 决定；不得预先假设必须复制 `start_server()`。

### 3. Entry / Starting Point

重新调查：

```text
src/main.rs :: burncloud node dispatch
crates/server/src/lib.rs :: start_server
crates/server/src/lib.rs :: create_app
crates/router/src/lib.rs :: create_router_app
crates/router/src/model_router.rs :: ModelRouter
```

### 4. Reuse Targets / Do Not Recreate

#### Reuse

- `burncloud-server` 统一 Axum app；
- `burncloud-router` data plane；
- existing Database / AppState construction；
- existing security boundary；
- existing Provider routing / failover。

#### Do Not Recreate

```text
NodeGateway
NodeRouter
LocalRouter
second /v1 server
second authentication boundary
parallel provider routing pipeline
```

### 5. Scope

#### Allowed

- Node profile 对 existing Server / Router 的最小 wiring；
- 必要的 construction refactor，使 NodeContext 能复用现有组件；
- host / port 继续沿用现有公开入口语义；
- targeted tests 证明 Node 模式进入同一 data plane。

#### Avoid

- Router scoring / failover 算法变化；
- Channel 数据模型重设计；
- Local Channel registration（NODE-501）；
- model process lifecycle；
- Billing / Auth / quota 语义；
- 新 Gateway / protocol layer；
- provider-specific 改造。

### 6. Behavior Contract

#### Inputs

- NODE-001 提供的 Node lifecycle；
- NODE-002 提供的 NodeConfig / NodeContext；
- 现有 Server / Router construction path。

#### Outputs

- Node 模式启动后存在一个统一 BurnCloud HTTP endpoint；
- `/v1/...` 请求仍进入 existing data-plane Router；
- existing management/internal/security composition 保持语义一致。

#### Ownership

NODE-003 owns：Node profile 对 existing Server / Router 的组合。  
NODE-003 does not own：路由决策、Provider 语义、本地 Runtime、Channel 健康状态。

### 7. Failure / Forbidden Fallbacks

Server / Router 组合失败：Node startup 明确失败，不静默启动简化版 Node Server。  
security boundary 无法保持：停止实现并报告架构冲突。

禁止：

```text
fallback to a second Axum server
bypass security_boundary_middleware
route local requests outside ModelRouter
change provider priority/failover to make Node pass tests
copy management/data-plane APIs into Node module
```

### 8. Impact / Invariants

```text
persistence: reuse existing Database path
external_calls: unchanged
billing_usage_quota: must remain unchanged
 auth_authorization: must remain unchanged
routing_provider: composition only; semantics unchanged
public_api_cli: Node runtime uses existing HTTP API surface
process_runtime_lifecycle: Server lifecycle only
```

必须保持：

- `INV-RUNTIME-001`；
- `INV-RUNTIME-002`；
- `INV-ROUTER-001`；
- `INV-ROUTER-002`；
- `INV-AUTH-002`；
- `INV-BILLING-001`；
- `INV-BILLING-002`。

架构约束：**ModelRouter remains the single Route Engine.**

### 9. Dependencies

前置：`NODE-001`、`NODE-002`。  
后续关键依赖：`NODE-503`。

### 10. Stop Conditions

```text
STOP IF:
- implementation requires NodeGateway / NodeRouter / LocalRouter
- existing security boundary cannot be preserved
- Provider routing semantics must change
- Billing/Auth/quota behavior must be changed
- Local Runtime must bypass Channel/ModelRouter
- a new database or duplicate API surface is required
- an INV-* must change without explicit architecture approval
```

---

## 第三层：验收层（Definition of Done）

### ✅ 功能结果

- [ ] `burncloud node` 可以组合并启动现有 BurnCloud Server / Router。
- [ ] `localhost:3000/v1/...` 仍由 existing data plane 处理。
- [ ] Node 模式没有第二个 Gateway / Router。
- [ ] Node 模式为后续 Local Channel 留出接入位置，但本 Issue 不启动模型。

### ✅ 边界保护

- [ ] 未创建 NodeGateway、NodeRouter、LocalRouter。
- [ ] 未改变 ModelRouter 的 Provider ranking / failover 语义。
- [ ] 未绕过 security boundary、Auth、Billing 或 quota。
- [ ] 未提前实现 NODE-501 / NODE-503 的本地路由行为。

### ✅ 回归与验证

- [ ] `INV-RUNTIME-002`、`INV-ROUTER-001/002` 保持成立。
- [ ] `INV-AUTH-002`、`INV-BILLING-001/002` 保持成立。
- [ ] 现有 Provider 请求在 Node wiring 改动后仍能通过统一 data plane。
- [ ] 管理面 / internal routes 的现有安全语义未改变。

### ✅ 工程流程

- [ ] current-main Evidence Audit 已完成。
- [ ] Engineering Issue 已通过 READY Gate。
- [ ] Task Contract 明确真实 Server / Router construction path。
- [ ] 只通过分支 + Pull Request 合并。
