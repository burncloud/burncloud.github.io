---
title: "UI-BUYER-003：实现 Buyer Playground"
slug: /burncloud-ui/implementation-plan/ui-buyer-003/
---

# UI-BUYER-003：实现 Buyer Playground

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**类别：Buyer**  
**功能依赖：UI-003、UI-BUYER-002、Node demand states、Buyer Logs（trace link）**

> 产品合同：[/burncloud-ui/buyer/playground/](/burncloud-ui/buyer/playground/)

### TL;DR

Playground 是第一次真实 API 使用，不是 demo。Buyer 选 Model/Tier、发真实请求、看到 response/latency/usage/cost/request trace；不能选 Provider/GPU，也不能 Download/Start Runtime。

### 背景与动机（Why）

current `playground_live.rs` 已经通过 authenticated console proxy 发真实路由请求，且 bearer secret 留在 server-side。这是重要复用资产；迁移目标是产品化 Model/Tier 与 Node states，而不是重写执行路径。

### 范围速览（In / Out）
| ✅ 做 | ❌ 不做 |
| --- | --- |
| real request/response | 不 fake response |
| Model/Tier selection | 不选 Provider/GPU |
| latency/usage/cost/trace | 不直接 download/start |
| preparing/blocker/recovered | 不实现 Demand Reconciliation |

### 审批者关注点（Reviewer Focus）
1. 是否继续使用真实 production semantics？
2. management JWT / API credential boundary 是否保持？
3. MODEL_PREPARING 等状态是否来自 backend 而不是 spinner 猜测？

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

把现有真实 Playground 演进为 Buyer Model/Tier 产品入口，并正确解释 Node/Serving 状态。

### 2. Evidence

- STATIC CONFIRMED — current `/console/api/playground/chat` 发真实请求。
- STATIC CONFIRMED — client 使用 opaque token management reference，bearer secret server-side。
- STATIC CONFIRMED — current response 已解析 usage 与 route trace headers。
- STATIC CONFIRMED — current model choices 来自 active Channels，尚未是 product catalog。
- UNKNOWN — Tier contract 与 canonical Node preparing/blocker/recovery semantics。

### 3. Entry / Starting Point

`functional_pages/playground_live.rs`、`/console/api/playground/chat`、existing `/v1/*` semantics、UI-BUYER-002 catalog。

### 4. Reuse Targets / Do Not Recreate

Reuse：existing proxy/token ref/real response/usage/trace/Router。  
Do Not Recreate：fake endpoint、second execution path、Provider/GPU selector、runtime/download controls。

### 5. Scope

Allowed：Buyer Playground UI、Model/Tier selector、structured error/preparing states、Logs trace navigation。  
Avoid：Router/Node demand/runtime backend、catalog backend、billing semantics。

### 6. Behavior Contract

**Inputs**：Buyer + approved Model/Tier + request content。  
**Outputs**：real response or structured production failure/preparing state + usage/cost/latency/trace。  
**Ownership**：Router executes；Node demand prepares；UI composes/presents。  
**Side Effects**：real potentially billable inference request only。

### 7. Failure / Forbidden Fallbacks

区分 Auth/Billing/Serving/MODEL_PREPARING/Hardware 等 approved classes；secondary usage failure 不抹掉成功 response。禁止 fake response、manual Provider/GPU/runtime、无限 spinner 代替 state。

### 8. Impact / Invariants

真实 inference external call/billing semantics；management JWT 不能成为 data-plane credential；Buyer declares Model/Tier only。

### 9. Dependencies

UI-003、UI-BUYER-002、Node state contracts、Buyer Logs trace destination。

### 10. Stop Conditions

STOP IF UI 需要下载/启动 runtime，preparing/blocker 无 authoritative contract，final model list 只能从 raw Channels 得出，或 Router semantics 必须修改。

---

## 第三层：验收层（Definition of Done）

- [ ] Playground 与 production request semantics 一致。
- [ ] no fake response。
- [ ] Buyer 只选择 Model/Tier。
- [ ] response/usage/latency/request trace 真实。
- [ ] preparing/blocker/recovered explicit。
- [ ] no Download/Deploy/Runtime control。
- [ ] Request ID 可去 Buyer Logs。
- [ ] credential security invariants 回归通过。
- [ ] branch + PR。
