---
title: "UI-ADMIN-006：实现 Admin Operations"
slug: /burncloud-ui/implementation-plan/ui-admin-006/
---

# UI-ADMIN-006：实现 Admin Operations

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003、UI-007、UI-008 + Autopilot Event / Proposal / Human Gate / Verify contracts**

> 产品合同：[/burncloud-ui/admin/operations/](/burncloud-ui/admin/operations/)  
> Canonical production route：`/console/admin/operations`

### TL;DR
Operations 是 Human-by-Exception 页面。Admin 看到系统自动做了什么、为什么、哪里失败、需要什么人工决策。任何高风险动作必须 `Reason → Proposal → Human Decision → Action → Verify → Result`。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| event/reason/action/result feed | 不逐 PID 操作 |
| proposal approve/reject | 不 HTTP 200=完成 |
| verify evidence | 不绕过 policy/audit |
| failed/recovered | 不手工 scheduler |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal
建立 `/console/admin/operations` 的 Autopilot exception/decision/audit surface。

### 2. Evidence
- STATIC CONFIRMED — Target Operations requires Reason/Action/Verify/Result and Human-by-Exception。
- UNKNOWN — current-main unified Autopilot Event/Proposal/Verify contracts。

### 3. Entry / Starting Point
future Autopilot/Proposal/Audit services、existing observability/guardrail evidence、UI-004、UI-003/007/008。

### 4. Reuse Targets / Do Not Recreate
Reuse：backend events/proposals/audit/verify、Node statuses、security policy。  
Do Not Recreate：client workflow engine、scheduler、process manager。

### 5. Scope
Allowed：event feed、exception detail、approved proposal decisions、verify/result display。  
Avoid：generic automation engine、runtime/process direct controls、unaudited actions。

### 6. Behavior Contract
**Inputs**：Admin identity + events/proposals/reason/evidence + explicit decision + locale。  
**Outputs**：decision/result/audit UI。  
**Ownership**：Autopilot/Policy owns proposal/action；UI gathers explicit human decision。  
**Side Effects**：authorized approve/reject/actions only via backend contract。

### 7. Failure / Forbidden Fallbacks
HTTP 200 submission != success；must verify authoritative result。禁止 optimistic completed、direct runtime command、hidden unaudited retry。

### 8. Impact / Invariants
High-risk operations；route `/console/admin/operations`；Human-by-Exception；audit/verify mandatory。

### 9. Dependencies
UI-003、007、008、UI-004 + Event/Proposal/Human Gate/Verify contracts。

### 10. Stop Conditions
STOP IF action lacks proposal/audit/verify、UI must directly manage runtime/process、or high-risk operation can bypass Human Gate。

---

## 第三层：验收层（Definition of Done）
- [ ] canonical route 与 UI-008 一致。
- [ ] Admin authorization/action policy server-side。
- [ ] Reason→Proposal→Decision→Action→Verify→Result traceable。
- [ ] failed/recovered truthful；HTTP 200 not completion。
- [ ] machine event/action/error IDs stable；explanation localized。
- [ ] branch + PR + approve/reject/failure/recovery E2E。
