---
title: "UI-ADMIN-006：实现 Admin Operations"
slug: /burncloud-ui/implementation-plan/ui-admin-006/
---

# UI-ADMIN-006：实现 Admin Operations

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003 + Autopilot Event Stream / Proposal / Approval / Audit / Verify**

> 产品合同：[/burncloud-ui/admin/operations/](/burncloud-ui/admin/operations/)

### TL;DR

Operations 是 BurnCloud Autopilot 的观察与例外处理中心。低风险动作自动完成；高风险动作以明确 Proposal 进入 Human Gate；所有动作必须有 Reason → Action → Verify → Result，HTTP 200 不是完成。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Autopilot Actions | 不 generic `Allow AI` |
| Needs Attention | 不每个低风险动作都确认 |
| Proposal Approve/Reject | 不以 HTTP 200 当 Success |
| Verify/Audit | 不 raw PID console |

### 审批者关注点（Reviewer Focus）
1. high-risk Proposal 是否对象化且有 reason/cost/risk/scope？
2. Approve/Reject 是否授权并审计？
3. Verify 是否独立证明目标结果？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立 Autopilot action history + exception/proposal gate，保持 Human by Exception。

### 2. Evidence

- TARGET CONFIRMED — `Observe → Decide → Act → Verify → Report`。
- TARGET CONFIRMED — payment/security/commercial/irreversible infra 等进入 Human Gate。
- STATIC CONFIRMED — current router logs 是 request observability，不等于 Autopilot decision/action audit。
- UNKNOWN — unified Autopilot event stream、Proposal service、approval audit、Verify evidence contracts。

### 3. Entry / Starting Point

Admin workspace；Operations event/proposal/audit services；shared logs/timeline/drawer patterns。

### 4. Reuse Targets / Do Not Recreate

Reuse：authoritative domain action events + audit/security infrastructure。  
Do Not Recreate：router-log-derived Autopilot history、client decision engine、raw process console。

### 5. Scope

Allowed：Operations page/event/proposal/audit clients/approve-reject UX。  
Avoid：Autopilot engine、scheduler/runtime internals、policy definition、payment provider implementation。

### 6. Behavior Contract

**Inputs**：Admin + action events + Proposal + risk/approval policy + Verify evidence。  
**Outputs**：history/active exceptions/proposal decision/verified result。  
**Ownership**：Autopilot decides low-risk；policy defines high-risk gate；UI records explicit human decision。  
**Side Effects**：Approve/Reject only for authorized Proposal objects。

### 7. Failure / Forbidden Fallbacks

API 200 without Verify stays unverified；proposal execution failure remains failed/auditable。禁止 generic AI switch、low-risk every-action confirmation、raw PID controls。

### 8. Impact / Invariants

High-risk action surface；Human by Exception；Verify mandatory；AI/Autopilot cannot self-authorize high-risk financial/security/architecture decisions。

### 9. Dependencies

UI-003 + Events + Proposal/Risk Policy + Approval/Audit + Verify Result。

### 10. Stop Conditions

STOP IF Proposal 由 frontend 合成、Success 无 Verify、generic AI permission 取代 object policy、或必须直接 PID/runtime control。

---

## 第三层：验收层（Definition of Done）

- [ ] every automatic action has Reason/Action/Verify/Result。
- [ ] Proposal explicit/auditable。
- [ ] Approve/Reject authorized/recorded。
- [ ] high-risk cannot bypass Human Gate。
- [ ] Recovered vs Active distinct。
- [ ] no raw process-control dashboard。
- [ ] branch + PR。
