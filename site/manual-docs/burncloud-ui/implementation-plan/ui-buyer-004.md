---
title: "UI-BUYER-004：实现 Buyer API Keys"
slug: /burncloud-ui/implementation-plan/ui-buyer-004/
---

# UI-BUYER-004：实现 Buyer API Keys

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Buyer**  
**功能依赖：UI-003**

> 产品合同：[/burncloud-ui/buyer/api-keys/](/burncloud-ui/buyer/api-keys/)

### TL;DR

Buyer 只管理自己的 BurnCloud API credential：Create、Rotate、Revoke 以及当前 backend 真正支持的 policy。完整 Secret 只允许在批准的创建/轮换响应中短暂展示，不从 list/get 再拿回来。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| owner-scoped create/rotate/revoke | 不显示 Supplier/Provider credential |
| masked metadata / last used | 不长期保存 plaintext secret |
| spend/IP policy（若支持） | 不在 Buyer 页面选 owner |
| explicit failure | 不 optimistic success |

### 审批者关注点（Reviewer Focus）
1. server owner scope 是否仍是授权真相？
2. list/get 是否始终 redacted？
3. optional Name/Scope 是否只有 backend 支持时才出现？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

把现有 API Keys 页面适配为 Buyer self-service credential page，并保持 secret/security invariants。

### 2. Evidence

- STATIC CONFIRMED — `api_keys_live.rs` 已用真实 TokenService create/rotate/revoke。
- STATIC CONFIRMED — server list/get 返回 opaque management id + token hint，不返回 bearer secret。
- STATIC CONFIRMED — server 对 non-admin token management 做 owner scope。
- STATIC CONFIRMED — security tests 验证 cross-user denial/redaction。
- STATIC CONFIRMED — current UI 仍有 admin-style owner selection，需要 Buyer page 去除。
- UNKNOWN — target Name/Scope 若无 backend contract 不得添加。

### 3. Entry / Starting Point

`functional_pages/api_keys_live.rs`、`backend::TokenService`、`server/api/token.rs`、security invariant tests。

### 4. Reuse Targets / Do Not Recreate

Reuse：TokenService、management refs、secret reveal pattern、owner authorization。  
Do Not Recreate：browser vault、client authorization filter、upstream credentials、duplicate token service。

### 5. Scope

Allowed：Buyer self-only page、supported policy controls、confirmation/reveal/test。  
Avoid：token auth model、multi-owner admin management、unsupported schema fields。

### 6. Behavior Contract

**Inputs**：Buyer + explicit token action。  
**Outputs**：owner metadata + approved one-time new secret。  
**Ownership**：server owns auth/secret lifecycle；UI owns reveal/confirm。  
**Side Effects**：real credential mutations。

### 7. Failure / Forbidden Fallbacks

Mutation failure = not applied；secret absent = 不恢复/不读 storage；owner mismatch = server denial。Secret 不进 URL/log/persistent client state。

### 8. Impact / Invariants

Existing token persistence only；management ref ≠ bearer credential；Buyer only own keys；frontend visibility ≠ authorization。

### 9. Dependencies

UI-003；core backend 已有强复用证据。Optional fields 需单独 backend contract。

### 10. Stop Conditions

STOP IF list/get 必须返回 bearer secret，Buyer 需要拉全量 users/tokens 再 client filter，或 unsupported fields 需要未授权 schema change。

---

## 第三层：验收层（Definition of Done）

- [ ] Buyer 仅管理自己的 API Keys。
- [ ] Create/Rotate/Revoke real backend working。
- [ ] list/get never redisclose bearer secret。
- [ ] cross-tenant denied server-side。
- [ ] optional unsupported fields 不伪造。
- [ ] Empty/Error/Recovered verified。
- [ ] security invariants remain green。
- [ ] branch + PR。
