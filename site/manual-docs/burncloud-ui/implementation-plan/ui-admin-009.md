---
title: "UI-ADMIN-009：实现 Admin Suppliers"
slug: /burncloud-ui/implementation-plan/ui-admin-009/
---

# UI-ADMIN-009：实现 Admin Suppliers

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Admin**  
**功能依赖：UI-003 + Supplier Registry / Verification / Reliability / Contribution / Commercial**

> 产品合同：[/burncloud-ui/admin/suppliers/](/burncloud-ui/admin/suppliers/)

### TL;DR

Suppliers 管供应商身份、Verification/Level、Reliability、Resources、Contribution 和商业状态。Provider Channel 不是 Supplier；Level、Reliability、Contribution、Revenue Share 也不是同一个分数。

### 背景与动机（Why）

BurnCloud 的信任与供给体系需要长期可解释。如果 UI 把上游 Channel、可靠性、贡献度和商业分成混成一个“Supplier Score”，后续很难审计，也容易错误授权。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| Supplier Profile | 不把 Channel 当 Supplier |
| Verification / Level | 不 client-compute trust score |
| Reliability / Resources | 不显示 Buyer credential |
| Contribution / Commercial Status | 不默认暴露 commercial secrets |

### 审批者关注点（Reviewer Focus）
1. Supplier identity 是否来自 registry？
2. Level/Reliability/Contribution/Revenue Share 是否分开？
3. 高风险商业修改是否进入 audit/gate？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

建立 authoritative Supplier business/trust management surface，并保持各 domain 语义独立。

### 2. Evidence

- STATIC CONFIRMED — current Providers/Channels 是 routing entities，不是 verified Supplier identities。
- TARGET CONFIRMED — page 需要 Profile/Level/Verification/Reliability/Resources/Commercial。
- TARGET CONFIRMED — Level/Reliability/Contribution/Revenue Share 必须分离。
- UNKNOWN — Supplier registry、verification/level、Reliability、Contribution、commercial config contracts。

### 3. Entry / Starting Point

UI-003；Supplier Registry；Verification/Reliability；Node resources；Contribution/Earnings；Commercial config/audit。

### 4. Reuse Targets / Do Not Recreate

Reuse：canonical Supplier identity + resource/reliability/contribution/commercial services。  
Do Not Recreate：Channel→Supplier inference、single opaque score、client trust engine、secret exposure。

### 5. Scope

Allowed：Supplier list/detail/evidence + separately authorized profile/commercial changes。  
Avoid：registry/reliability/contribution engine、Provider routing management、raw secrets。

### 6. Behavior Contract

**Inputs**：Admin + Supplier profile/verification/level/reliability/resource/contribution/commercial facts。  
**Outputs**：Supplier list/detail + approved management actions。  
**Ownership**：each domain owns its fact；UI does not merge semantics。  
**Side Effects**：authorized/audited profile/commercial actions only。

### 7. Failure / Forbidden Fallbacks

Unknown verification ≠ Verified；unavailable Reliability/Contribution stays Unknown；save failure not applied。禁止 Channel inference、client trust score、credential secrets。

### 8. Impact / Invariants

Supplier identity ≠ Provider Channel；Trust requires evidence；Level/Reliability/Contribution/Revenue Share separate；high-risk commercial change audited。

### 9. Dependencies

UI-003 + Supplier Registry + Verification/Level + Reliability + Resources + Contribution + Commercial/Audit。

### 10. Stop Conditions

STOP IF Supplier 必须从 Channel 推导、trust/client score、commercial change 无 audit/gate、或需要暴露 secret credentials。

---

## 第三层：验收层（Definition of Done）

- [ ] Supplier identity authoritative。
- [ ] Level/Reliability/Contribution/Revenue Share separated。
- [ ] Verification evidence-backed。
- [ ] commercial sensitive fields permission-controlled。
- [ ] important changes authorized/audited。
- [ ] no credential secret exposure。
- [ ] branch + PR。
