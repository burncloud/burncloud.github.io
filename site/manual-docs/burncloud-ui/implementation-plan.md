---
title: "BurnCloud 界面实施计划"
slug: /burncloud-ui/implementation-plan/
hide_table_of_contents: false
---

# BurnCloud 界面实施计划

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**Canonical Standard：BurnCloud Engineering Issue Standard**

> 本页是 BurnCloud UI 的实施计划索引，不是 Codex 的直接开发授权。每一个计划项真正开始实现前，都必须基于当时的 `burncloud/burncloud/main` 重新执行 Evidence Audit，并创建通过 READY Gate 的 Engineering Issue，再生成 Task Contract。

### TL;DR

BurnCloud UI 不做“React → Dioxus 翻译”，而是把批准后的 Buyer / Supplier / Admin 产品合同迁移到唯一的生产 Dioxus 客户端。实施顺序先固定 Target/Current Truth、设计系统和 Role Workspace，再逐页迁移 Buyer、Supplier、Admin，随后统一 Node Autopilot UX、旧 Route 兼容和最终质量 Gate。

### 核心原则

```text
Implementation Plan
“未来准备做什么”
        ↓
Evidence Audit against current main
        ↓
READY Engineering Issue
“批准实现什么”
        ↓
Task Contract
“当前 main 具体从哪里改”
        ↓
Branch / Pull Request
```

计划页永远不把 Workbench mock、截图、AI 推断或未来设计当成当前生产事实。

### 计划列表

#### Phase 1 — Foundation

| ID | 计划 | 功能依赖 |
| --- | --- | --- |
| [UI-001](/burncloud-ui/implementation-plan/ui-001/) | Target Standard → Production Contract | 无 |
| [UI-002](/burncloud-ui/implementation-plan/ui-002/) | Design Tokens + Shared Components | 无 |
| [UI-003](/burncloud-ui/implementation-plan/ui-003/) | Production Shell + Role/Auth Workspace | UI-001, UI-002 |

#### Phase 2 — Buyer

| ID | 页面 | 功能依赖 |
| --- | --- | --- |
| [UI-BUYER-001](/burncloud-ui/implementation-plan/ui-buyer-001/) | Buyer Overview | UI-003 + Buyer metric contracts |
| [UI-BUYER-002](/burncloud-ui/implementation-plan/ui-buyer-002/) | Buyer Marketplace | UI-003 + Product Catalog/Tier/Pricing |
| [UI-BUYER-003](/burncloud-ui/implementation-plan/ui-buyer-003/) | Buyer Playground | UI-003 + Marketplace + Node demand states |
| [UI-BUYER-004](/burncloud-ui/implementation-plan/ui-buyer-004/) | Buyer API Keys | UI-003 |
| [UI-BUYER-005](/burncloud-ui/implementation-plan/ui-buyer-005/) | Buyer Usage | UI-003 + Usage attribution + Buyer Logs |
| [UI-BUYER-006](/burncloud-ui/implementation-plan/ui-buyer-006/) | Buyer Billing | UI-003 + Buyer financial contracts |
| [UI-BUYER-007](/burncloud-ui/implementation-plan/ui-buyer-007/) | Buyer Logs | UI-003 + tenant-safe log projection |

推荐用户路径：

```text
Discover Model
→ Test
→ Get Credential
→ Call API
→ Understand Usage
→ Manage Billing
→ Diagnose Request
```

#### Phase 3 — Supplier

| ID | 页面 | 功能依赖 |
| --- | --- | --- |
| [UI-SUPPLIER-001](/burncloud-ui/implementation-plan/ui-supplier-001/) | Supplier Overview | UI-003 + Supplier/Node/Earnings |
| [UI-SUPPLIER-002](/burncloud-ui/implementation-plan/ui-supplier-002/) | Supplier Resources | UI-003 + Node inventory/resource lifecycle |
| [UI-SUPPLIER-003](/burncloud-ui/implementation-plan/ui-supplier-003/) | Supplier Deployments | UI-003 + managed deployment lifecycle |
| [UI-SUPPLIER-004](/burncloud-ui/implementation-plan/ui-supplier-004/) | Supplier Reliability | UI-003 + Reliability evidence |
| [UI-SUPPLIER-005](/burncloud-ui/implementation-plan/ui-supplier-005/) | Supplier Earnings | UI-003 + Contribution/Earnings |
| [UI-SUPPLIER-006](/burncloud-ui/implementation-plan/ui-supplier-006/) | Supplier Settlements | UI-003 + Settlement/Payout |
| [UI-SUPPLIER-007](/burncloud-ui/implementation-plan/ui-supplier-007/) | Supplier Settings | UI-003 + Supplier-owned settings |

Supplier 硬边界：**可以观察资源、自动部署结果、稳定性、贡献与收入；不能获得 Model Deployment、Runtime、Traffic 控制权。**

#### Phase 4 — Admin

| ID | 页面 | 功能依赖 |
| --- | --- | --- |
| [UI-ADMIN-001](/burncloud-ui/implementation-plan/ui-admin-001/) | Admin Overview | UI-003 + Revenue/Cost/Capacity |
| [UI-ADMIN-002](/burncloud-ui/implementation-plan/ui-admin-002/) | Admin Supply | UI-003 + Supplier/Node/Hardware |
| [UI-ADMIN-003](/burncloud-ui/implementation-plan/ui-admin-003/) | Admin Capacity | UI-003 + Capacity/Demand/Economics |
| [UI-ADMIN-004](/burncloud-ui/implementation-plan/ui-admin-004/) | Admin Demand | UI-003 + Demand/Forecast |
| [UI-ADMIN-005](/burncloud-ui/implementation-plan/ui-admin-005/) | Admin Models | UI-003 + Product Catalog/Manifest |
| [UI-ADMIN-006](/burncloud-ui/implementation-plan/ui-admin-006/) | Admin Operations | UI-003 + Autopilot Event/Proposal/Verify |
| [UI-ADMIN-007](/burncloud-ui/implementation-plan/ui-admin-007/) | Admin Revenue | UI-003 + Revenue/Verified Cost |
| [UI-ADMIN-008](/burncloud-ui/implementation-plan/ui-admin-008/) | Admin Settlements | UI-003 + Operations + Settlement/Payout |
| [UI-ADMIN-009](/burncloud-ui/implementation-plan/ui-admin-009/) | Admin Suppliers | UI-003 + Supplier/Trust/Commercial |
| [UI-ADMIN-010](/burncloud-ui/implementation-plan/ui-admin-010/) | Admin Customers | UI-003 + Customer Risk/Activity |
| [UI-ADMIN-011](/burncloud-ui/implementation-plan/ui-admin-011/) | Admin Settings | UI-003 + Operations + domain settings |

#### Phase 5–7 — Cross-cutting / Release

| ID | 计划 | 功能依赖 |
| --- | --- | --- |
| [UI-004](/burncloud-ui/implementation-plan/ui-004/) | Canonical Node Autopilot UX States | UI-002, UI-003 + Node state contracts |
| [UI-005](/burncloud-ui/implementation-plan/ui-005/) | Legacy Console Route Compatibility | UI-003 + target page parity |
| [UI-006](/burncloud-ui/implementation-plan/ui-006/) | Final Quality / Golden Page Gates | release pages + UI-004/005 |

### 全局风险与安全网

- Target truth ≠ current source truth。
- Unknown / Unavailable 不得被 0、Success、Ready 或 mock 替代。
- Role 只能来自 Backend Authorization。
- Production 只有一套 Dioxus frontend / Router。
- Buyer 不默认看到 GPU / Supplier / IDC / Runtime。
- Supplier 不拥有 Deploy / Runtime / Traffic 权限。
- Admin 管理系统级结果与例外，不退化成逐 PID / GPU 控制台。
- Node 生命周期和 Autopilot 状态由后端定义，UI 只 Observe / Explain / Report。
- 所有实现通过 branch + Pull Request。

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

把批准后的 BurnCloud UI 产品合同拆成 31 个单一结果计划单元，并确保任何单元只有在 current-main 证据、依赖、边界和验证目标明确后才可以转成 READY Engineering Issue。

### 2. Evidence

当前 Evidence baseline：`burncloud/burncloud@c314bff9646f9113c9a58a818552fc80c77543a6`。

已确认：
- 生产客户端是 `crates/client` 下唯一 Dioxus frontend；
- `app.rs` / `functional_layout.rs` 持有现有 Router/Shell；
- 当前导航仍以 Providers / Models / Routes 等内部对象为主；
- AuthContext 已接收 backend `roles`；
- 已有真实 Billing、Usage、Token、Playground、Logs、Customers 等能力片段；
- Supplier、Capacity、Demand Forecast、Settlement、Autopilot Proposal 等目标域存在大量未确认/未完成 backend contract。

因此：**计划文档完整 ≠ backend 已存在 ≠ 可以编码。**

### 3. Entry / Starting Point

每个计划页独立声明真实入口。全局调查入口：

```text
crates/client/src/app.rs
crates/client/src/functional_layout.rs
crates/client/src/auth_gate.rs
crates/client/src/backend.rs
crates/client/src/critical_pages/*
crates/client/src/functional_pages/*
crates/server/src/api/*
docs/ui/*
```

### 4. Reuse Targets / Do Not Recreate

全局复用：现有 Dioxus Router、AuthContext、visual_system.css、shared components、real backend services、现有 UI gates。

全局禁止：第二套 React frontend、第二个 Router、生产 mock registry、前端 Billing/Settlement/Capacity/Trust truth engine、Node Runtime/Process Manager 的 UI 复制品。

### 5. Scope

每个计划页只能授权一个页面或一个横切合同。缺失 backend domain 必须成为依赖/Blocker，不允许通过扩大 UI Issue scope 来补齐。

### 6. Behavior Contract

所有页面最少定义 Inputs / Outputs / Ownership / Side Effects；所有状态页必须定义 Loading / Empty / Partial Failure / Error / Recovered 或对应领域状态。

### 7. Failure / Forbidden Fallbacks

任何 Unknown、权限不足、backend 缺失、验证不可执行都必须显式失败/阻塞；禁止 mock、client-side authorization、optimistic financial success、silent fallback。

### 8. Impact / Invariants

每页必须声明 persistence、external calls、billing/usage/quota、auth、routing/provider、concurrency、public API/CLI、runtime/process 影响；若需要改变未声明领域，触发 Architecture/Scope Stop。

### 9. Dependencies

本列表定义功能依赖关系。真正实施时必须针对当时 current main 重新确认依赖是否 DONE / waived。

### 10. Stop Conditions

```text
STOP IF:
- current main disproves a material plan assumption
- implementation requires changing an Avoid domain
- required backend truth does not exist
- UI would become a new source of business truth
- authorization would move into frontend state/navigation
- implementation requires a second frontend/router/subsystem
- meaningful targeted/regression/runtime verification cannot be performed
```

触发后不得扩大 scope，必须报告冲突和证据。

---

## 第三层：验收层（Definition of Done）

整个 BurnCloud UI 实施计划完成时：

- [ ] 31 个计划单元均有独立 canonical plan page。
- [ ] Buyer / Supplier / Admin IA 与批准产品合同一致。
- [ ] 所有生产数据来自 authoritative backend 或 explicit Unknown。
- [ ] Role/tenant security 由 backend 保证。
- [ ] Supplier/Buyer/Admin 权限边界保持。
- [ ] Node Autopilot 状态语义统一且 UI 无 runtime authority。
- [ ] 旧 Route 完成兼容迁移，不因重构直接失效。
- [ ] Web / Desktop / LiveView 适用路径通过。
- [ ] Loading / Empty / Partial Failure / Error / Recovered 覆盖完成。
- [ ] Golden Page / Accessibility / UI gates 通过。
- [ ] Production 仍只有一套 Dioxus frontend。
- [ ] 所有代码变化均通过 branch + Pull Request。
