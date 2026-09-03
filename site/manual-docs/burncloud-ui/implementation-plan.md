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

BurnCloud UI 统一为一个受保护的 Console 管理面。Buyer、Supplier、Admin 都属于 `/console/*`，权限最终由 Backend Authorization 决定。

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

```text
/console namespace ≠ authorization
URL ≠ authorization
Sidebar visibility ≠ authorization
Role Switcher ≠ permission grant
Backend Authorization = final authority
```

### Root Route Policy

任何需要 authentication / role / tenant / admin 权限的真实生产 UI 页面，其 canonical URL 必须位于 `/console/*`。

Root-level 旧 Console URL 分两类，不再统一按“兼容 redirect”处理。

#### A. 直接退役

以下 7 个 root UI routes 没有继续保存的必要：

```text
/models
/logs
/providers
/routes
/guardrails
/evaluation
/team
```

它们最终必须：

```text
no page
no alias
no redirect
404/410 before data-plane fallback
```

对应业务能力如果仍然需要，使用 `/console/admin/*` 下的新 canonical path，例如 `/console/admin/models`、`/console/admin/providers`、`/console/admin/logs`。

> 404/410 tombstone 是防止请求误入 `router_app` data-plane fallback 的安全边界，不是 legacy compatibility surface。

#### B. 临时 Compatibility Redirect

以下 root URL 暂时可以保留为**无业务逻辑 redirect-only**，以后可单独退役：

```text
/dashboard   → /console
/playground  → /console/buyer/playground
/keys        → /console/buyer/api-keys
/billing     → /console/buyer/billing
/customers   → /console/admin/customers
/users       → /console/admin/customers
/settings    → /console/admin/settings
```

这些 root URL 本身不得读取 protected data、调用 management API 或承载业务状态。

### Billing 的业务拆分

```text
Buyer Billing
/console/buyer/billing
= Buyer 自己的余额、充值、交易、Invoice、支付方式、Spend Limit

Admin Billing
/console/admin/billing
= 全平台客户账务、充值订单、欠费、异常、Billing Policy、账务操作与审计

Admin Revenue
/console/admin/revenue
= Revenue / Verified Cost / Gross Margin

Admin Settlements
/console/admin/settlements
= Supplier Payable / Settlement Batch / Payout Result
```

必须保持：

```text
Buyer Billing
≠ Admin Billing
≠ Admin Revenue
≠ Admin Settlements
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

### Phase 2 — Buyer

| ID | 页面 | Canonical Production Route | 主要职责 |
| --- | --- | --- | --- |
| [UI-BUYER-001](/burncloud-ui/implementation-plan/ui-buyer-001/) | Overview | `/console/buyer/overview` | Spend / Balance / Availability / Tokens |
| [UI-BUYER-002](/burncloud-ui/implementation-plan/ui-buyer-002/) | Marketplace | `/console/buyer/marketplace` | Model/Tier 产品目录 |
| [UI-BUYER-003](/burncloud-ui/implementation-plan/ui-buyer-003/) | Playground | `/console/buyer/playground` | 真实 `/v1` 测试 |
| [UI-BUYER-004](/burncloud-ui/implementation-plan/ui-buyer-004/) | API Keys | `/console/buyer/api-keys` | Buyer-owned credentials |
| [UI-BUYER-005](/burncloud-ui/implementation-plan/ui-buyer-005/) | Usage | `/console/buyer/usage` | Requests / Tokens / Cost attribution |
| [UI-BUYER-006](/burncloud-ui/implementation-plan/ui-buyer-006/) | Billing | `/console/buyer/billing` | Buyer financial workspace |
| [UI-BUYER-007](/burncloud-ui/implementation-plan/ui-buyer-007/) | Logs | `/console/buyer/logs` | tenant-safe request observability |

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

| ID | 页面 | Canonical Production Route |
| --- | --- | --- |
| [UI-SUPPLIER-001](/burncloud-ui/implementation-plan/ui-supplier-001/) | Overview | `/console/supplier/overview` |
| [UI-SUPPLIER-002](/burncloud-ui/implementation-plan/ui-supplier-002/) | Resources | `/console/supplier/resources` |
| [UI-SUPPLIER-003](/burncloud-ui/implementation-plan/ui-supplier-003/) | Deployments | `/console/supplier/deployments` |
| [UI-SUPPLIER-004](/burncloud-ui/implementation-plan/ui-supplier-004/) | Reliability | `/console/supplier/reliability` |
| [UI-SUPPLIER-005](/burncloud-ui/implementation-plan/ui-supplier-005/) | Earnings | `/console/supplier/earnings` |
| [UI-SUPPLIER-006](/burncloud-ui/implementation-plan/ui-supplier-006/) | Settlements | `/console/supplier/settlements` |
| [UI-SUPPLIER-007](/burncloud-ui/implementation-plan/ui-supplier-007/) | Settings | `/console/supplier/settings` |

Supplier 可以 Observe / Explain / Graceful Offline；不能获得 Model Deployment / Runtime / Traffic authority。

### Phase 4 — Admin

| ID | 页面 | Canonical Production Route | 主要职责 |
| --- | --- | --- | --- |
| [UI-ADMIN-001](/burncloud-ui/implementation-plan/ui-admin-001/) | Overview | `/console/admin/overview` | 系统经营与基础设施结论 |
| [UI-ADMIN-002](/burncloud-ui/implementation-plan/ui-admin-002/) | Supply | `/console/admin/supply` | 供给、Supplier、Node/Hardware |
| [UI-ADMIN-003](/burncloud-ui/implementation-plan/ui-admin-003/) | Capacity | `/console/admin/capacity` | Model/Tier Headroom / Risk |
| [UI-ADMIN-004](/burncloud-ui/implementation-plan/ui-admin-004/) | Demand | `/console/admin/demand` | Requests / Tokens / Concurrency / Forecast |
| [UI-ADMIN-005](/burncloud-ui/implementation-plan/ui-admin-005/) | Models | `/console/admin/models` | Catalog / Manifest / Pricing / Readiness |
| [UI-ADMIN-006](/burncloud-ui/implementation-plan/ui-admin-006/) | Operations | `/console/admin/operations` | Autopilot Exception / Proposal / Verify |
| [UI-ADMIN-012](/burncloud-ui/implementation-plan/ui-admin-012/) | Billing | `/console/admin/billing` | Customer billing / policy / audit |
| [UI-ADMIN-007](/burncloud-ui/implementation-plan/ui-admin-007/) | Revenue | `/console/admin/revenue` | Revenue / Verified Cost / Gross Margin |
| [UI-ADMIN-008](/burncloud-ui/implementation-plan/ui-admin-008/) | Settlements | `/console/admin/settlements` | Supplier Payable / Payout |
| [UI-ADMIN-009](/burncloud-ui/implementation-plan/ui-admin-009/) | Suppliers | `/console/admin/suppliers` | Supplier business/trust view |
| [UI-ADMIN-010](/burncloud-ui/implementation-plan/ui-admin-010/) | Customers | `/console/admin/customers` | Customer accounts / risk / limits |
| [UI-ADMIN-011](/burncloud-ui/implementation-plan/ui-admin-011/) | Settings | `/console/admin/settings` | backend-owned platform settings |

Admin Advanced 能力如 Providers / Routes / Admin Logs / Guardrails / Evaluation / Team 若继续需要，只能有 `/console/admin/*` canonical path；旧 root URL 不因此继续存在。

### Phase 5–7 — Cross-cutting / Release

| ID | 计划 | 功能依赖 |
| --- | --- | --- |
| [UI-004](/burncloud-ui/implementation-plan/ui-004/) | Canonical Node Autopilot UX States | UI-002/003/007/008 + Node states |
| [UI-005](/burncloud-ui/implementation-plan/ui-005/) | Retire Legacy Root Console Routes | UI-008 + canonical page availability |
| [UI-006](/burncloud-ui/implementation-plan/ui-006/) | Final Quality / Golden Page Gates | role pages + UI-004/005/007/008 |

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

## 第二层：机器执行层（Machine Executable Specification）

### 1. Goal

把 BurnCloud UI 拆成 **34 个单一结果计划单元**：8 个 platform/cross-cutting contracts、7 个 Buyer 页面、7 个 Supplier 页面、12 个 Admin 页面。所有受保护 UI canonical paths 位于 `/console/*`，并明确区分 temporary compatibility roots 与 retired roots。

### 2. Evidence

Evidence baseline：`burncloud/burncloud@c314bff9646f9113c9a58a818552fc80c77543a6`。

STATIC CONFIRMED：

- 生产客户端是 `crates/client` 下唯一 Dioxus frontend；
- current Dioxus/LiveView 仍注册多条 root-level Console routes；
- current `AuthGate` 只检查 authenticated；
- management API 已使用 `/console/api/*`，internal API 使用 `/console/internal/*`；
- `/models` `/logs` `/providers` `/routes` `/guardrails` `/evaluation` `/team` 的 root UI URL 没有 repo evidence 表明是稳定公共 compatibility contract；
- Server 最终使用 `fallback_service(router_app)`，因此 retired path 必须在 data-plane fallback 前终止；
- current Billing 是 authenticated user spend/usage 视角，不能替代 Admin Billing；
- Target Workbench 只能作为产品参考，不能成为 production route/auth truth。

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

Reuse：single Dioxus Router、AuthContext、management API namespace、existing server route ordering/security boundary、visual system、real backend services。

Do Not Recreate：second frontend、second Router、client role DB、client authorization engine、frontend billing/revenue/settlement truth engine、redirects for explicitly retired root routes。

### 5. Scope

每个计划页只能授权一个页面或一个横切合同。缺失 backend domain 进入依赖/Blocker；不能为了完成 UI 扩大 scope。

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

Retired root routes：

```text
/models /logs /providers /routes /guardrails /evaluation /team
→ 404/410 before data-plane fallback
```

Temporary compatibility roots：

```text
/dashboard /playground /keys /billing /customers /users /settings
→ redirect-only
```

### 7. Failure / Forbidden Fallbacks

```text
forbidden:
- root-level sensitive page remains active
- retired root has redirect or alias
- retired root falls into router_app/data plane
- temporary root reads data or invokes management action
- URL/localStorage/hidden nav grants role
- unknown role -> Admin
- /billing dynamically means Buyer or Admin by active role
- language changes permission/path semantics
- unknown metric -> 0/Healthy/Ready
- mock as production truth
- second frontend/router
```

### 8. Impact / Invariants

```text
INV-UI-ROUTE-001
Protected production UI canonical URL MUST be under /console/*.

INV-UI-ROUTE-002
A root URL explicitly retained for temporary compatibility MAY only redirect.
It MUST NOT render protected content, fetch protected data, or execute management actions.

INV-UI-ROUTE-003
A retired root UI URL MUST NOT exist as page, alias, or redirect.
It MUST terminate with 404/410 before data-plane fallback.

INV-UI-AUTH-001
Backend Authorization is final authority.

INV-UI-BILLING-001
Buyer Billing, Admin Billing, Admin Revenue and Admin Settlements are distinct domains.
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
- a retired root route can reach data-plane fallback
- an internal production link still requires a retired root route
- /console/api or /console/internal can be swallowed by UI catch-all
- role must be inferred from URL
- Buyer/Admin Billing must share one client-side truth model
- missing backend fact would be filled with mock/client inference
- second frontend/router/source of truth is required
- meaningful auth/route/i18n/runtime verification cannot be performed
```

---

## 第三层：验收层（Definition of Done）

- [ ] 34 个计划单元均有 canonical plan contract。
- [ ] `/console` 是 authenticated Console UI root。
- [ ] Buyer/Supplier/Admin canonical pages 全部位于 `/console/{workspace}/*`。
- [ ] `/console/api/*`、`/console/internal/*` 保持 reserved backend namespace。
- [ ] `/models` `/logs` `/providers` `/routes` `/guardrails` `/evaluation` `/team` 无 page / alias / redirect。
- [ ] 七个 retired roots 在 data-plane fallback 前返回 404/410。
- [ ] `/dashboard` `/playground` `/keys` `/billing` `/customers` `/users` `/settings` 如暂留，只能 redirect-only。
- [ ] `/billing` 只兼容 Buyer Billing；Admin Billing 独立 `/console/admin/billing`。
- [ ] URL/Sidebar/localStorage/locale 都不能授予角色。
- [ ] Backend API authorization 仍是最终权限真相。
- [ ] Buyer / Admin Billing / Revenue / Settlements 语义分离。
- [ ] i18n 至少覆盖 `en/zh/zh-TW/ja` contract，且 locale 不进入 Console URL。
- [ ] machine identifiers/model IDs/API paths/error codes 不翻译。
- [ ] Production 仍只有一套 Dioxus frontend / Router。
- [ ] Web/Desktop/LiveView 关键路径与 retired outcome 一致。
- [ ] Golden Pages 与 auth/route/i18n/fallback matrix 纳入 Final Gate。
