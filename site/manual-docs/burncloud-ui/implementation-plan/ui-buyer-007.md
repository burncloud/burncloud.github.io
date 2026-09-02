---
title: "UI-BUYER-007：实现 Buyer Logs"
slug: /burncloud-ui/implementation-plan/ui-buyer-007/
---

# UI-BUYER-007：实现 Buyer Logs

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Buyer**  
**功能依赖：UI-003 + tenant-safe Buyer log projection**

> 产品合同：[/burncloud-ui/buyer/logs/](/burncloud-ui/buyer/logs/)

### TL;DR

Buyer Logs 只显示自己的 Request ID、时间、Model/Tier、Status、Latency、Tokens、Cost 和安全错误摘要。当前 Admin `/console/api/logs` 不能拿来前端过滤成 Buyer Logs。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| tenant request list/detail | 不拿 admin logs client-filter |
| safe request/cost metadata | 不显示 API secret |
| search/filter/request ID | 不默认显示完整 Prompt |
| redaction/partial states | 不显示 PID/internal port |

### 审批者关注点（Reviewer Focus）
1. tenant isolation 是否 server-side？
2. admin logs endpoint security 是否保持？
3. request trace 与 Usage/Billing 是否语义一致？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

提供 Buyer-scoped redacted request observability，不弱化 Admin observability security。

### 2. Evidence

- STATIC CONFIRMED — `logs_full.rs` 已有真实 request table/detail patterns。
- STATIC CONFIRMED — `observability::full_logs` 调 `/console/api/logs`。
- STATIC/RUNTIME TEST CONFIRMED — normal user 对 `/console/api/logs` 返回 403，Admin 返回 200。
- UNKNOWN — tenant-safe Buyer log endpoint/projection、approved redaction、Tier metadata。

### 3. Entry / Starting Point

`functional_pages/logs_full.rs`（UI pattern）、`observability.rs`（Admin endpoint evidence）、server log API/security tests。

### 4. Reuse Targets / Do Not Recreate

Reuse：request IDs/log records/table/filter/detail/redaction framework。  
Do Not Recreate：client filtering admin logs、second log store、prompt/secret storage、process info exposure。

### 5. Scope

Allowed：Buyer Logs + Buyer-safe client + trace links。  
Avoid：relax Admin logs auth、new persistence、prompt visibility policy change。

### 6. Behavior Contract

**Inputs**：Buyer + filter/request ID + server-scoped observability projection。  
**Outputs**：redacted list/detail。  
**Ownership**：Observability service owns scope/redaction/facts；UI presents。  
**Side Effects**：read-only。

### 7. Failure / Forbidden Fallbacks

detail failure 保留 list；log service failure 不暗示 data plane down；sensitive detail unavailable stays redacted/forbidden。禁止 fetch admin logs then filter by user_id。

### 8. Impact / Invariants

Read-only tenant observability；Admin endpoint remains Admin-protected；secrets redacted server-side。

### 9. Dependencies

UI-003 + Buyer log projection + Tier/request metadata。

### 10. Stop Conditions

STOP IF Buyer Logs 需要放宽 `/console/api/logs`，tenant isolation 被提议成 client filter，或 safe page 必须暴露 credential/process secrets。

---

## 第三层：验收层（Definition of Done）

- [ ] Buyer tenant isolation server-side verified。
- [ ] Request ID/time/model/tier/status/latency/tokens/cost trace real records。
- [ ] secret/Supplier/internal process details hidden。
- [ ] Logs 与 Usage/Billing reconcile。
- [ ] Empty/Partial/Error/Recovered verified。
- [ ] Admin logs security regression remains green。
- [ ] branch + PR。
