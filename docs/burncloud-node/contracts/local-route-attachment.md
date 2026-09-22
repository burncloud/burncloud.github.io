---
title: "Local Route Attachment Seam"
slug: /burncloud-node/contracts/local-route-attachment/
---

# Local Route Attachment Seam

```text
Owner: crates/interfaces/server + Traffic-owned side effect
Status: Accepted / Framework Only
Source: crates/interfaces/server/src/node_attachment.rs
Contract shape: application seam functions, not a ChannelAdapter trait
```

## 为什么不是 `ChannelAdapter` trait

当前框架没有定义独立的 `ChannelAdapter`。应用层通过回调调用 Traffic 拥有的真实副作用，并在成功后保存精确 Receipt。

```text
Node 准备到 Ready
        ↓
prepare_and_attach_node_route(...)
        ↓
调用 Traffic-owned attach side effect
        ↓
成功返回 LocalRouteAttachmentId
        ↓
记录 RouterAttached evidence
        ↓
Routable
```

不能为了让 Integration Queue 名称整齐而新增一个没有代码证据的 trait。

## 当前公开接线

```text
prepare_and_attach_node_route
├─ 准备到 Ready
├─ 读取 ProcessPlan.local_endpoint
└─ 调用 attach side effect

attach_ready_node_route
├─ 验证 Ready gate
├─ 成功后保存 LocalRouteAttachmentId
└─ 发布 Routable

detach_unhealthy_node_route
├─ 验证 attachment_id 所有权
├─ 先 quarantine
├─ 再 exact detach
└─ 返回 DetachedRoute receipt

begin_detached_route_recovery
└─ 只有有效 DetachedRoute 才能打开恢复流程
```

## 唯一职责

把已经 Ready 的本地 endpoint 接入 Existing ModelRouter，并用精确 Receipt 保证注册、隔离、摘除和恢复的顺序。

## 具体示例

注册输入：

```text
model: "qwen-4b"
local_endpoint: "http://127.0.0.1:39122"
```

注册成功 Receipt：

```text
LocalRouteAttachmentId(101)
```

精确摘除输入：

```text
model: "qwen-4b"
attachment_id: LocalRouteAttachmentId(101)
```

摘除成功 Receipt：

```text
DetachedRoute
├─ model: "qwen-4b"
└─ attachment_id: LocalRouteAttachmentId(101)
```

失败示例：

```text
attach side effect returns Error
        ↓
workload becomes Failed
        ↓
no LocalRouteAttachmentId is invented
        ↓
Routable is not published
```

示例 ID 和 endpoint 只解释 Receipt 的对应关系，不是生产固定值。

## 不负责什么

```text
Local Route Attachment 不负责
├─ 创建第二个 Router 或 Scheduler
├─ 决定 Local Candidate 优先级
├─ 准备模型或 Runtime
├─ 启动进程
├─ 生成 local_endpoint
├─ 修改 Supply 真相
└─ 根据客户余额做路由决策
```

## Fail-closed 顺序

```text
Routable runtime 变成 Unhealthy
        ↓
Traffic quarantine
        ↓ 成功
发布 Unhealthy
        ↓
exact detach(attachment_id)
        ├─ 失败 → 保持不可路由，允许按同一 ID 重试清理
        └─ 成功 → DetachedRoute receipt
                       ↓
                    才允许 Recover
```

## BDD 边界

```gherkin
Scenario: Attachment side effect fails
  Given a workload is Ready
  When Traffic attachment fails
  Then the workload becomes Failed
  And it is not published as Routable
  And no attachment receipt is invented
```

## 停止条件

如果接线需要创建第二套路由、修改 Scheduler、直接访问 Traffic 内部数据表，或无法取得精确 attachment Receipt，立即停止并上升 Traffic Contract 审查。
