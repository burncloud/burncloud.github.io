---
title: "BurnCloud 界面实施计划"
slug: /burncloud-ui/implementation-plan/
hide_table_of_contents: false
---

# BurnCloud 界面实施计划

## 第一层：人类阅读区（Human Readable Layer）

**状态：PLANNED**  
**Canonical Standard：BurnCloud Engineering Issue Standard**

> 本页是 BurnCloud UI 的 canonical 实施计划索引，不是 Codex 的直接开发授权。真正编码前仍必须执行：current-main Evidence Audit → READY Engineering Issue → Task Contract → Branch / Pull Request。

### TL;DR

BurnCloud UI 统一为一个受保护的 Console 管理面。Buyer、Supplier、Admin 不是三个独立根级应用，而是 `/console/*` 下三个拥有不同权限和业务职责的 workspace。

```text
PUBLIC
/
/login
/register

DATA PLANE
/v1/*

MANAGEMENT UI
/console
├── /console/buyer/*
├── /console/supplier/*
└── /console/admin/*

MANAGEMENT / INTERNAL API
├── /console/api/*
└── /console/internal/*

TRANSPORT / HEALTH
/ws
/health
```

核心规则：

```text
/console namespace
≠ authorization

URL
≠ authorization

Sidebar visibility
≠ authorization

Role Switcher
≠ permission grant

Backend Authorization
= final authority
```

### 根级 Legacy URL 的新规则

任何需要 authentication / role / tenant / admin 权限的**真正生产 UI 页面**，canonical URL 必须位于 `/console/*`。

根级旧 URL 只允许作为无业务逻辑的 compatibility redirect：

```text
legacy root URL
      ↓ redirect only
/console/...
      ↓ AuthGate
      ↓ WorkspaceGate
      ↓ Page
      ↓ Backend Authorization
```

因此根级 `/models`、`/logs`、`/billing`、`/providers`、`/routes` 等不能继续渲染敏感页面、读取管理数据或调用管理 API。

### Billing 的业务拆分

Buyer 与 Admin 都有 Billing，但职责不同，不冲突：

```text
Buyer Billing
/console/buyer/billing
= 我自己的余额、充值、交易、Invoice、支付方式、Spend Limit

Admin Billing
/console/admin/billing
= 全平台客户账务、充值订单、欠费、账务异常、Billing Policy、账务操作与审计

Admin Revenue
/console/admin/revenue
= Revenue / Verified Cost / Gross Margin

Admin Settlements
/console/admin/settlements
= Supplier Payable / Settlement Batch / Payout Result
```

必须保持：

```text
Admin Billing
≠ Admin Revenue
≠ Admin Settlements
```

### 执行链

```text
Implementation Plan (PLANNED)
        ↓
Evidence Audit against current main
        ↓
READY Engineering Issue
        ↓
Task Contract
        ↓
Branch / Pull Request
        ↓
Verification / Review
        ↓
main
```

---

## 计划列表

### Phase 1 — Foundation / Platform Contracts

| ID | 计划 | 功能依赖 |
| --- | --- | --- |
| [UI-001](/burncloud-ui/implementation-plan/ui-001/) | Target Standard → Production Contract | 无 |
| [UI-002](/burncloud-ui/implementation-plan/ui-002/) | Design Tokens + Shared Components | 无 |
| [UI-007](/burncloud-ui/implementation-plan/ui-007/) | Production i18n / Localization Contract | UI-001, UI-002 |
| [UI-003](/burncloud-ui/implementation-plan/ui-003/) | Production Shell + Role/Auth Workspace | UI-001, UI-002, UI-007 |
| [UI-008](/burncloud-ui/implementation-plan/ui-008/) | Console Namespace + Route Authorization Contract | UI-003, UI-007 |

Foundation 完成前，角色页面不得靠 URL、localStorage、mock role 或隐藏菜单自行实现权限。

### Phase 2 — Buyer

所有 Buyer 页面都依赖 UI-003 + UI-007 + UI-008。

| ID | 页面 | Canonical Production Route | 主要职责 |
| --- | --- | --- | --- |
| [UI-BUYER-001](/burncloud-ui/implementation-plan/ui-buyer-001/) | Overview | `/console/buyer/overview` | Spend / Balance / Availability / Tokens |
| [UI-BUYER-002](/burncloud-ui/implementation-plan/ui-buyer-002/) | Marketplace | `/console/buyer/marketplace` | Model/Tier 产品目录 |
| [UI-BUYER-003](/burncloud-ui/implementation-plan/ui-buyer-003/) | Playground | `/console/buyer/playground` | 真实 `/v1` 测试 |
| [UI-BUYER-004](/burncloud-ui/implementation-plan/ui-buyer-004/) | API Keys | `/console/buyer/api-keys` | Buyer-owned credentials |
| [UI-BUYER-005](/burncloud-ui/implementation-plan/ui-buyer-005/) | Usage | `/console/buyer/usage` | Requests / Tokens / Cost attribution |
| [UI-BUYER-006](/burncloud-ui/implementation-plan/ui-buyer-006/) | Billing | `/console/buyer/billing` | 自己的余额、充值、交易、Invoice、支付方式、Spend Limit |
| [UI-BUYER-007](/burncloud-ui/implementation-plan/ui-buyer-007/) | Logs | `/console/buyer/logs` | tenant-safe request observability |

Buyer mental model：

```text
Discover Model
→ Test
→ Get Credential
→ Call API
→ Understand Usage
→ Manage Billing
→ Diagnose Request
```

### Phase 3 — Supplier

所有 Supplier 页面都依赖 UI-003 + UI-007 + UI-008。

| ID | 页面 | Canonical Production Route |
| --- | --- | --- |
| [UI-SUPPLIER-001](/burncloud-ui/implementation-plan/ui-supplier-001/) | Overview | `/console/supplier/overview` |
| [UI-SUPPLIER-002](/burncloud-ui/implementation-plan/ui-supplier-002/) | Resources | `/console/supplier/resources` |
| [UI-SUPPLIER-003](/burncloud-ui/implementation-plan/ui-supplier-003/) | Deployments | `/console/supplier/deployments` |
| [UI-SUPPLIER-004](/burncloud-ui/implementation-plan/ui-supplier-004/) | Reliability | `/console/supplier/reliability` |
| [UI-SUPPLIER-005](/burncloud-ui/implementation-plan/ui-supplier-005/) | Earnings | `/console/supplier/earnings` |
| [UI-SUPPLIER-006](/burncloud-ui/implementation-plan/ui-supplier-006/) | Settlements | `/console/supplier/settlements` |
| [UI-SUPPLIER-007](/burncloud-ui/implementation-plan/ui-supplier-007/) | Settings | `/console/supplier/settings` |

Supplier 硬边界：资源、自动部署结果、可靠性、贡献和收入可以观察；Model Deployment、Runtime、Traffic 权限不交给 Supplier。

### Phase 4 — Admin

所有 Admin 页面都依赖 UI-003 + UI-007 + UI-008。

| ID | 页面 | Canonical Production Route | 主要职责 |
| --- | --- | --- | --- |
| [UI-ADMIN-001](/burncloud-ui/implementation-plan/ui-admin-001/) | Overview | `/console/admin/overview` | 系统经营与基础设施结论 |
| [UI-ADMIN-002](/burncloud-ui/implementation-plan/ui-admin-002/) | Supply | `/console/admin/supply` | 供给、Supplier、Node/Hardware |
| [UI-ADMIN-003](/burncloud-ui/implementation-plan/ui-admin-003/) | Capacity | `/console/admin/capacity` | Model/Tier Headroom / Risk |
| [UI-ADMIN-004](/burncloud-ui/implementation-plan/ui-admin-004/) | Demand | `/console/admin/demand` | 请求、Token、Concurrency、Forecast |
| [UI-ADMIN-005](/burncloud-ui/implementation-plan/ui-admin-005/) | Models | `/console/admin/models` | 产品模型目录、Manifest、Pricing/Readiness |
| [UI-ADMIN-006](/burncloud-ui/implementation-plan/ui-admin-006/) | Operations | `/console/admin/operations` | Autopilot Exception / Proposal / Verify |
| [UI-ADMIN-012](/burncloud-ui/implementation-plan/ui-admin-012/) | Billing | `/console/admin/billing` | 客户账务、充值订单、欠费、异常、Billing Policy、审计 |
| [UI-ADMIN-007](/burncloud-ui/implementation-plan/ui-admin-007/) | Revenue | `/console/admin/revenue` | Revenue / Verified Cost / Gross Margin |
| [UI-ADMIN-008](/burncloud-ui/implementation-plan/ui-admin-008/) | Settlements | `/console/admin/settlements` | Supplier Payable / Payout |
| [UI-ADMIN-009](/burncloud-ui/implementation-plan/ui-admin-009/) | Suppliers | `/console/admin/suppliers` | Supplier business/trust view |
| [UI-ADMIN-010](/burncloud-ui/implementation-plan/ui-admin-010/) | Customers | `/console/admin/customers` | Customer accounts / risk / limits |
| [UI-ADMIN-011](/burncloud-ui/implementation-plan/ui-admin-011/) | Settings | `/console/admin/settings` | backend-owned platform settings |

Admin economics 必须拆开：

```text
Customer
   ↓
Admin Billing
   ↓
Revenue
   ↓
Verified Cost
   ↓
Gross Margin

Supplier Earnings
   ↓
Admin Settlements
   ↓
Payout Result
```

### Phase 5–7 — Cross-cutting / Release

| ID | 计划 | 功能依赖 |
| --- | --- | --- |
| [UI-004](/burncloud-ui/implementation-plan/ui-004/) | Canonical Node Autopilot UX States | UI-002/003/007/008 + Node states |
| [UI-005](/burncloud-ui/implementation-plan/ui-005/) | Legacy Console Route Compatibility | UI-008 + target page parity |
| [UI-006](/burncloud-ui/implementation-plan/ui-006/) | Final Quality / Golden Page Gates | role pages + UI-004/005/007/008 |

---

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

把 BurnCloud UI 拆成 **34 个单一结果计划单元**：8 个 platform/cross-cutting contracts、7 个 Buyer 页面、7 个 Supplier 页面、12 个 Admin 页面。所有受保护 UI 的 canonical path 都位于 `/console/*`，所有根级 legacy UI URL 只能作为 redirect-only compatibility stub。

### 2. Evidence

Evidence baseline：`burncloud/burncloud@c314bff9646f9113c9a58a818552fc80c77543a6`。

STATIC CONFIRMED：

- 生产客户端是 `crates/client` 下唯一 Dioxus frontend；
- current protected Dioxus UI 仍存在 root-level `/models`、`/billing` 等路径；
- current `AuthGate` 只检查 authenticated；
- management API 已使用 `/console/api/*`，internal API 使用 `/console/internal/*`；
- current LiveView 仍硬编码 legacy root UI paths；
- current Billing 是 authenticated user-spend/usage 视角，不能替代未来 Admin Billing；
- Target Workbench 的 URL-driven role/i18n 只能作产品参考，不能成为 production authority。

结论：计划文档必须先锁定 Management Plane 边界，之后页面才能进入 READY。

### 3. Entry / Starting Point

```text
crates/client/src/app.rs
crates/client/src/auth_gate.rs
crates/client/src/functional_layout.rs
crates/client/src/lib.rs :: liveview_router
crates/client/src/backend.rs
crates/server/src/lib.rs
crates/server/src/api/*
crates/common/src/constants.rs
rustburn/burncloud-ui (Target reference only)
```

### 4. Reuse Targets / Do Not Recreate

Reuse：single Dioxus Router、AuthContext、management API namespace、visual system、real backend services、existing UI/security gates。

Do Not Recreate：second frontend、second Router、client role DB、client authorization engine、frontend billing/revenue/settlement ledger、production mock source of truth。

### 5. Scope

每个计划页只能授权一个页面或一个横切合同。缺失 backend domain 进入依赖/Blocker；不能为了完成 UI 而扩大 scope。

### 6. Behavior Contract

所有受保护页面继承：

```text
AuthGate
  ↓
WorkspaceGate
  ↓
Canonical /console/* Page
  ↓
Management API
  ↓
Backend role/capability/tenant authorization
```

页面最少定义 Inputs / Outputs / Ownership / Side Effects，并覆盖 Loading / Empty / Partial Failure / Error / Recovered。

### 7. Failure / Forbidden Fallbacks

```text
forbidden:
- root-level sensitive page remains active
- legacy root URL reads data or invokes management action
- URL grants role
- localStorage grants role
- hidden nav treated as authorization
- unknown role -> Admin
- legacy URL changes meaning by active role
- /billing dynamically means Buyer or Admin based on role
- language changes permission/path semantics
- unknown metric -> 0/Healthy/Ready
- mock as production truth
- second frontend/router
```

### 8. Impact / Invariants

新增硬约束：

```text
INV-UI-ROUTE-001
Any production UI page requiring authentication, role, tenant or admin authority
MUST have its canonical URL under /console/*.

INV-UI-ROUTE-002
Legacy UI URLs outside /console/* MAY exist only as redirect-only compatibility stubs.
They MUST NOT render sensitive business pages, fetch protected data, or execute management actions.

INV-UI-AUTH-001
Backend Authorization is final authority; URL/Sidebar/Workspace preference are presentation only.

INV-UI-BILLING-001
Buyer Billing, Admin Billing, Admin Revenue and Admin Settlements are distinct business domains.
```

Data-plane `/v1/*` semantics不因 UI migration 改变。

### 9. Dependencies

```text
UI-001 + UI-002
      ↓
UI-007
      ↓
UI-003
      ↓
UI-008
      ↓
Buyer / Supplier / Admin Pages
      ↓
UI-004 + UI-005
      ↓
UI-006
```

### 10. Stop Conditions

```text
STOP IF:
- a protected business page must remain canonical outside /console/*
- a legacy root URL must render sensitive content to preserve compatibility
- /console/api or /console/internal can be swallowed by UI catch-all
- role must be inferred from URL
- Buyer/Admin Billing must share one client-side truth model
- legacy URL must change meaning by active role
- missing backend fact would be filled with mock/client inference
- second frontend/router/source of truth is required
- meaningful auth/route/i18n/runtime verification cannot be performed
```

---

## 第三层：验收层（Definition of Done）

- [ ] 34 个计划单元均有独立或明确引用的 canonical plan contract。
- [ ] `/console` 是 authenticated Console UI root。
- [ ] Buyer/Supplier/Admin canonical pages 全部位于 `/console/{workspace}/*`。
- [ ] `/console/api/*`、`/console/internal/*` 保持 reserved backend namespace。
- [ ] 所有 root-level legacy UI URL 只做 redirect，不承载敏感业务。
- [ ] `/models` redirect 到 Admin Models，不变成 Buyer Marketplace。
- [ ] `/logs` redirect 到 Admin/legacy Logs，不变成 Buyer Logs。
- [ ] `/billing` redirect 到 Buyer Billing；Admin Billing 独立使用 `/console/admin/billing`。
- [ ] Buyer Billing / Admin Billing / Revenue / Settlements 职责不混。
- [ ] URL/Sidebar/localStorage/locale 都不能授予角色。
- [ ] i18n locale 不进入 Console canonical URL。
- [ ] machine identifiers 不翻译。
- [ ] Production 仍只有一套 Dioxus frontend / Router。
- [ ] Web/Desktop/LiveView 关键路径和 root redirect matrix 可验证。
- [ ] Golden Pages + auth/route/i18n matrix 纳入 Final Gate。
